#!/usr/bin/env python3
"""
VividWalls Artwork Processing Script
Extracts artwork data from CSV, downloads images, and processes them through color analysis workflow
"""

import os
import csv
import json
import requests
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Optional
from urllib.parse import urlparse
import logging
from pathlib import Path
import re
from html.parser import HTMLParser

# Configure logging with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vividwalls_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CSV_FILE_PATH = "../data/shared/vividwalls-products-cleaned.csv"
# MCP-based workflow endpoints
N8N_WEBHOOK_URL = "https://n8n.vividwalls.blog/webhook/artwork-color-analysis-mcp"
# Legacy OpenAI-based workflow (for fallback)
LEGACY_WEBHOOK_URL = "https://n8n.vividwalls.blog/webhook/artwork-color-analysis"
BULK_WEBHOOK_URL = "https://n8n.vividwalls.blog/webhook/bulk-artwork-analysis"
IMAGE_DOWNLOAD_DIR = "../data/artwork_images"
BATCH_SIZE = 10  # Process in batches for bulk endpoint
RATE_LIMIT_DELAY = 2  # Seconds between API calls
MAX_RETRIES = 3
TIMEOUT = 30  # Seconds
USE_MCP_WORKFLOW = True  # Toggle between MCP and legacy workflow

class HTMLTextExtractor(HTMLParser):
    """Extract text content from HTML"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
    
    def handle_data(self, data):
        if self.current_tag not in ['script', 'style']:
            self.text.append(data.strip())
    
    def get_text(self):
        return ' '.join(filter(None, self.text))

class ArtworkProcessor:
    """Process VividWalls artwork from CSV to color analysis"""
    
    def __init__(self):
        """Initialize the processor with necessary directories and tracking"""
        self.processed_artworks: Set[str] = set()
        self.unique_artworks: List[Dict] = []
        self.failed_downloads: List[str] = []
        self.analysis_results: List[Dict] = []
        
        # Create image download directory if it doesn't exist
        Path(IMAGE_DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized ArtworkProcessor with download directory: {IMAGE_DOWNLOAD_DIR}")
    
    def extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML content"""
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        return parser.get_text()
    
    def extract_tags_from_html(self, html_content: str) -> List[str]:
        """Extract tags from the HTML content"""
        tags = []
        # Look for spans with specific styling that contain tags
        tag_pattern = r'<span[^>]*style="[^"]*border-radius:\s*20px[^"]*"[^>]*>([^<]+)</span>'
        matches = re.findall(tag_pattern, html_content)
        tags.extend([tag.strip() for tag in matches])
        return tags
    
    def parse_csv(self) -> None:
        """Parse CSV file and extract unique artworks"""
        logger.info(f"Starting to parse CSV file: {CSV_FILE_PATH}")
        
        try:
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                row_count = 0
                
                for row in reader:
                    row_count += 1
                    handle = row.get('Handle', '').strip()
                    
                    # Skip if we've already processed this artwork
                    if handle in self.processed_artworks or not handle:
                        continue
                    
                    # Extract first variant's data (main artwork info)
                    if row.get('Title') and row.get('Image Src'):
                        # Clean the description
                        body_html = row.get('Body (HTML)', '')
                        description = self.extract_text_from_html(body_html)
                        tags = self.extract_tags_from_html(body_html)
                        
                        artwork = {
                            'id': handle,
                            'title': row['Title'].strip(),
                            'collection': row.get('Collections', 'Unknown').strip(),
                            'artist': row.get('Vendor', 'VividWalls').strip(),
                            'imageUrl': row['Image Src'].strip(),
                            'description': description,
                            'tags': tags,
                            'status': row.get('Status', 'active').strip()
                        }
                        
                        self.unique_artworks.append(artwork)
                        self.processed_artworks.add(handle)
                        logger.debug(f"Added artwork: {artwork['title']} from {artwork['collection']}")
        
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            raise
        
        logger.info(f"Parsed {row_count} rows, found {len(self.unique_artworks)} unique artworks")
    
    def download_image(self, url: str, artwork_id: str) -> Optional[str]:
        """Download image from URL and save locally"""
        try:
            # Create filename from artwork ID
            file_extension = os.path.splitext(urlparse(url).path)[1] or '.png'
            filename = f"{artwork_id}{file_extension}"
            filepath = os.path.join(IMAGE_DOWNLOAD_DIR, filename)
            
            # Skip if already downloaded
            if os.path.exists(filepath):
                logger.debug(f"Image already exists: {filename}")
                return filepath
            
            # Download the image
            logger.info(f"Downloading image for {artwork_id} from {url}")
            response = requests.get(url, timeout=TIMEOUT, stream=True)
            response.raise_for_status()
            
            # Save to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download image for {artwork_id}: {str(e)}")
            self.failed_downloads.append(artwork_id)
            return None
    
    def process_single_artwork(self, artwork: Dict) -> Optional[Dict]:
        """Process a single artwork through the color analysis workflow"""
        try:
            # Download image first
            local_image_path = self.download_image(artwork['imageUrl'], artwork['id'])
            if not local_image_path:
                logger.warning(f"Skipping {artwork['id']} due to download failure")
                return None
            
            # Prepare payload for n8n webhook
            payload = {
                'artworkId': artwork['id'],
                'title': artwork['title'],
                'collection': artwork['collection'],
                'artist': artwork['artist'],
                'imageUrl': artwork['imageUrl'],
                'tags': artwork['tags'],
                'description': artwork['description'],
                'localImagePath': local_image_path
            }
            
            logger.info(f"Sending {artwork['title']} to color analysis workflow")
            
            # Make request with retries
            for attempt in range(MAX_RETRIES):
                try:
                    response = requests.post(
                        N8N_WEBHOOK_URL,
                        json=payload,
                        timeout=TIMEOUT
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    logger.info(f"Successfully analyzed {artwork['title']}")
                    
                    # Add local processing metadata
                    result['localImagePath'] = local_image_path
                    result['processedAt'] = datetime.now().isoformat()
                    
                    return result
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {artwork['id']}: {str(e)}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RATE_LIMIT_DELAY * (attempt + 1))
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Failed to process {artwork['id']}: {str(e)}")
            return None
    
    def process_bulk_artworks(self, artworks: List[Dict]) -> List[Dict]:
        """Process multiple artworks in bulk"""
        try:
            # Download all images first
            for artwork in artworks:
                self.download_image(artwork['imageUrl'], artwork['id'])
            
            # Prepare bulk payload
            payload = {
                'artworks': artworks
            }
            
            logger.info(f"Sending batch of {len(artworks)} artworks to bulk analysis")
            
            response = requests.post(
                BULK_WEBHOOK_URL,
                json=payload,
                timeout=TIMEOUT * len(artworks)  # Adjust timeout for bulk
            )
            response.raise_for_status()
            
            results = response.json()
            logger.info(f"Bulk analysis completed: {results.get('successful', 0)} successful, {results.get('failed', 0)} failed")
            
            return results.get('results', [])
            
        except Exception as e:
            logger.error(f"Bulk processing failed: {str(e)}")
            return []
    
    def generate_summary_report(self) -> Dict:
        """Generate a summary report of the processing"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_artworks': len(self.unique_artworks),
            'processed_successfully': len(self.analysis_results),
            'failed_downloads': len(self.failed_downloads),
            'collections': {},
            'color_distribution': {},
            'mood_distribution': {},
            'failed_artwork_ids': self.failed_downloads
        }
        
        # Analyze by collection
        for artwork in self.unique_artworks:
            collection = artwork['collection']
            if collection not in report['collections']:
                report['collections'][collection] = 0
            report['collections'][collection] += 1
        
        # Analyze color and mood distribution from results
        for result in self.analysis_results:
            if 'colorAnalysis' in result:
                # Track dominant colors
                dominant_colors = result['colorAnalysis'].get('dominantColors', [])
                for color in dominant_colors[:1]:  # Just the primary color
                    color_name = color.get('name', 'Unknown')
                    if color_name not in report['color_distribution']:
                        report['color_distribution'][color_name] = 0
                    report['color_distribution'][color_name] += 1
            
            if 'psychologicalProfile' in result:
                # Track moods
                mood = result['psychologicalProfile'].get('primaryMood', 'Unknown')
                if mood not in report['mood_distribution']:
                    report['mood_distribution'][mood] = 0
                report['mood_distribution'][mood] += 1
        
        return report
    
    def save_results(self) -> None:
        """Save processing results to files"""
        # Save analysis results
        results_file = os.path.join(IMAGE_DOWNLOAD_DIR, 'analysis_results.json')
        with open(results_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        logger.info(f"Saved analysis results to {results_file}")
        
        # Save summary report
        report = self.generate_summary_report()
        report_file = os.path.join(IMAGE_DOWNLOAD_DIR, 'processing_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved processing report to {report_file}")
        
        # Log summary
        logger.info("\n" + "="*50)
        logger.info("PROCESSING SUMMARY")
        logger.info("="*50)
        logger.info(f"Total Artworks: {report['total_artworks']}")
        logger.info(f"Successfully Processed: {report['processed_successfully']}")
        logger.info(f"Failed Downloads: {report['failed_downloads']}")
        logger.info("\nCollections Distribution:")
        for collection, count in report['collections'].items():
            logger.info(f"  {collection}: {count}")
        logger.info("="*50)
    
    def run(self, use_bulk: bool = False, limit: Optional[int] = None) -> None:
        """Run the complete processing pipeline"""
        logger.info("Starting VividWalls artwork processing pipeline")
        
        # Parse CSV
        self.parse_csv()
        
        # Apply limit if specified
        if limit:
            self.unique_artworks = self.unique_artworks[:limit]
            logger.info(f"Limited processing to {limit} artworks")
        
        # Filter only active artworks
        active_artworks = [a for a in self.unique_artworks if a['status'] == 'active']
        logger.info(f"Found {len(active_artworks)} active artworks to process")
        
        if use_bulk:
            # Process in batches
            for i in range(0, len(active_artworks), BATCH_SIZE):
                batch = active_artworks[i:i+BATCH_SIZE]
                logger.info(f"Processing batch {i//BATCH_SIZE + 1} of {(len(active_artworks) + BATCH_SIZE - 1)//BATCH_SIZE}")
                
                results = self.process_bulk_artworks(batch)
                self.analysis_results.extend(results)
                
                # Rate limiting between batches
                if i + BATCH_SIZE < len(active_artworks):
                    time.sleep(RATE_LIMIT_DELAY)
        else:
            # Process individually
            for i, artwork in enumerate(active_artworks):
                logger.info(f"Processing {i+1}/{len(active_artworks)}: {artwork['title']}")
                
                result = self.process_single_artwork(artwork)
                if result:
                    self.analysis_results.append(result)
                
                # Rate limiting
                if i < len(active_artworks) - 1:
                    time.sleep(RATE_LIMIT_DELAY)
        
        # Save results
        self.save_results()
        logger.info("Processing pipeline completed!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process VividWalls artwork for color analysis')
    parser.add_argument('--bulk', action='store_true', help='Use bulk processing endpoint')
    parser.add_argument('--limit', type=int, help='Limit number of artworks to process')
    parser.add_argument('--csv', default=CSV_FILE_PATH, help='Path to CSV file')
    
    args = parser.parse_args()
    
    # Update CSV path if provided
    if args.csv:
        global CSV_FILE_PATH
        CSV_FILE_PATH = args.csv
    
    # Create processor and run
    processor = ArtworkProcessor()
    processor.run(use_bulk=args.bulk, limit=args.limit)


if __name__ == "__main__":
    main() 