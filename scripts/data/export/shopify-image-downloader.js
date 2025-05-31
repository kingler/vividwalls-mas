#!/usr/bin/env node

/**
 * Shopify CDN Image Downloader
 * 
 * Downloads images from Shopify CDN and stores them locally on the droplet
 * for uploading to Pictorem during order processing.
 */

import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';

class ShopifyImageDownloader {
    constructor() {
        this.storageDir = process.env.IMAGE_STORAGE_DIR || '/var/www/vividwalls/images';
        this.maxFileSize = 50 * 1024 * 1024; // 50MB max
        this.allowedFormats = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
    }

    async initialize() {
        console.log('📦 Initializing Shopify Image Downloader...');
        
        // Ensure storage directory exists
        if (!fs.existsSync(this.storageDir)) {
            fs.mkdirSync(this.storageDir, { recursive: true });
            console.log(`✅ Created storage directory: ${this.storageDir}`);
        }
        
        // Set proper permissions (readable by web server)
        try {
            fs.chmodSync(this.storageDir, 0o755);
            console.log('✅ Storage directory permissions set');
        } catch (error) {
            console.log('⚠️ Could not set directory permissions:', error.message);
        }
    }

    async downloadImage(imageUrl, orderId, productId = null) {
        console.log(`📥 Downloading image from Shopify CDN...`);
        console.log(`🔗 Source URL: ${imageUrl}`);
        
        try {
            // Validate URL
            if (!this.isValidShopifyUrl(imageUrl)) {
                throw new Error('Invalid Shopify CDN URL');
            }
            
            // Generate local filename
            const filename = this.generateFilename(imageUrl, orderId, productId);
            const localPath = path.join(this.storageDir, filename);
            
            console.log(`💾 Target file: ${localPath}`);
            
            // Download with streaming to handle large files
            const response = await axios({
                method: 'GET',
                url: imageUrl,
                responseType: 'stream',
                timeout: 30000,
                headers: {
                    'User-Agent': 'VividWalls-OrderProcessor/1.0'
                }
            });
            
            // Validate content type
            const contentType = response.headers['content-type'];
            if (!this.isValidImageType(contentType)) {
                throw new Error(`Invalid image type: ${contentType}`);
            }
            
            // Validate file size
            const contentLength = parseInt(response.headers['content-length'] || '0');
            if (contentLength > this.maxFileSize) {
                throw new Error(`File too large: ${contentLength} bytes (max: ${this.maxFileSize})`);
            }
            
            // Download file
            const writer = createWriteStream(localPath);
            await pipeline(response.data, writer);
            
            // Verify file was written correctly
            const stats = fs.statSync(localPath);
            if (stats.size === 0) {
                fs.unlinkSync(localPath);
                throw new Error('Downloaded file is empty');
            }
            
            console.log(`✅ Image downloaded successfully:`);
            console.log(`   📁 File: ${filename}`);
            console.log(`   📏 Size: ${this.formatFileSize(stats.size)}`);
            console.log(`   🔗 Local Path: ${localPath}`);
            
            return {
                success: true,
                local_path: localPath,
                filename: filename,
                file_size: stats.size,
                content_type: contentType,
                download_timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error(`❌ Image download failed: ${error.message}`);
            return {
                success: false,
                error: error.message,
                attempted_url: imageUrl
            };
        }
    }

    async downloadMultipleImages(imageUrls, orderId, productId = null) {
        console.log(`📥 Downloading ${imageUrls.length} images from Shopify CDN...`);
        
        const results = [];
        
        for (let i = 0; i < imageUrls.length; i++) {
            const imageUrl = imageUrls[i];
            console.log(`\n📷 Image ${i + 1}/${imageUrls.length}:`);
            
            const result = await this.downloadImage(imageUrl, orderId, `${productId}_${i + 1}`);
            results.push(result);
            
            // Small delay between downloads
            if (i < imageUrls.length - 1) {
                await this.sleep(1000);
            }
        }
        
        const successful = results.filter(r => r.success);
        const failed = results.filter(r => !r.success);
        
        console.log(`\n📊 Download Summary:`);
        console.log(`   ✅ Successful: ${successful.length}`);
        console.log(`   ❌ Failed: ${failed.length}`);
        
        return {
            total: imageUrls.length,
            successful: successful.length,
            failed: failed.length,
            results: results,
            primary_image: successful.length > 0 ? successful[0] : null
        };
    }

    generateFilename(imageUrl, orderId, productId = null) {
        // Extract original filename or generate one
        const urlPath = new URL(imageUrl).pathname;
        const originalExt = path.extname(urlPath).toLowerCase() || '.jpg';
        const timestamp = Date.now();
        
        let baseFilename;
        if (productId) {
            baseFilename = `${orderId}_${productId}_${timestamp}`;
        } else {
            baseFilename = `${orderId}_${timestamp}`;
        }
        
        return `${baseFilename}${originalExt}`;
    }

    isValidShopifyUrl(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.hostname.includes('shopify') || 
                   urlObj.hostname.includes('cdn') ||
                   urlObj.hostname.includes('vividwalls'); // Allow VividWalls CDN too
        } catch {
            return false;
        }
    }

    isValidImageType(contentType) {
        if (!contentType) return false;
        
        const validTypes = [
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'image/webp',
            'image/gif'
        ];
        
        return validTypes.some(type => contentType.toLowerCase().includes(type));
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async cleanup(orderId, maxAge = 24 * 60 * 60 * 1000) {
        console.log(`🧹 Cleaning up old images for order: ${orderId}`);
        
        try {
            const files = fs.readdirSync(this.storageDir);
            const orderFiles = files.filter(file => file.startsWith(orderId));
            let deletedCount = 0;
            
            for (const file of orderFiles) {
                const filePath = path.join(this.storageDir, file);
                const stats = fs.statSync(filePath);
                const age = Date.now() - stats.mtime.getTime();
                
                if (age > maxAge) {
                    fs.unlinkSync(filePath);
                    deletedCount++;
                }
            }
            
            console.log(`✅ Cleaned up ${deletedCount} old image files`);
            
        } catch (error) {
            console.error(`❌ Cleanup failed: ${error.message}`);
        }
    }

    getImageUrl(filename) {
        // Return web-accessible URL for the downloaded image
        const webBaseUrl = process.env.WEB_BASE_URL || 'https://157.230.13.13';
        return `${webBaseUrl}/images/${filename}`;
    }

    async getStorageStats() {
        try {
            const files = fs.readdirSync(this.storageDir);
            let totalSize = 0;
            let imageCount = 0;
            
            for (const file of files) {
                const filePath = path.join(this.storageDir, file);
                const stats = fs.statSync(filePath);
                if (stats.isFile()) {
                    totalSize += stats.size;
                    imageCount++;
                }
            }
            
            return {
                total_images: imageCount,
                total_size: totalSize,
                total_size_formatted: this.formatFileSize(totalSize),
                storage_directory: this.storageDir
            };
            
        } catch (error) {
            return {
                error: error.message,
                storage_directory: this.storageDir
            };
        }
    }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
    const downloader = new ShopifyImageDownloader();
    
    const command = process.argv[2];
    const imageUrl = process.argv[3];
    const orderId = process.argv[4];
    
    if (command === 'download' && imageUrl && orderId) {
        downloader.initialize()
            .then(() => downloader.downloadImage(imageUrl, orderId))
            .then(result => {
                console.log('\n📋 Download Result:', JSON.stringify(result, null, 2));
                process.exit(result.success ? 0 : 1);
            })
            .catch(error => {
                console.error('❌ Download failed:', error.message);
                process.exit(1);
            });
    } else if (command === 'stats') {
        downloader.getStorageStats()
            .then(stats => {
                console.log('\n📊 Storage Statistics:', JSON.stringify(stats, null, 2));
                process.exit(0);
            });
    } else {
        console.log('Usage:');
        console.log('  node shopify-image-downloader.js download <image_url> <order_id>');
        console.log('  node shopify-image-downloader.js stats');
        process.exit(1);
    }
}

export default ShopifyImageDownloader; 