import {
  ArtSpotlightSchema,
  CollectionAnnouncementSchema,
  HowToGuideSchema,
  SeasonalContentSchema,
  ArtistInterviewSchema,
  WordPressPost,
  WordPressCategory,
  WordPressTag
} from "./types.js";
import { WordPressClient } from "./WordPressClient.js";
import { z } from "zod";

export class ArtOfSpaceGenerators {
  constructor(private wordpressClient: WordPressClient) {}

  async createArtSpotlight(data: z.infer<typeof ArtSpotlightSchema>): Promise<WordPressPost> {
    const validatedData = ArtSpotlightSchema.parse(data);

    // Generate SEO-optimized content
    const title = `Artist Spotlight: ${validatedData.artist_name} - "${validatedData.artwork_title}"`;
    
    const content = this.generateArtSpotlightContent(validatedData);
    const excerpt = this.generateArtSpotlightExcerpt(validatedData);

    // Ensure Art Spotlight category exists
    const category = await this.ensureCategory("Artist Spotlight", "Featured artists and their remarkable artworks");
    
    // Create/get tags
    const tags = await this.ensureTags([
      validatedData.artist_name,
      "artist spotlight",
      "featured artist",
      ...(validatedData.tags || [])
    ]);

    const postData = {
      title: { rendered: title },
      content: { rendered: content, protected: false },
      excerpt: { rendered: excerpt, protected: false },
      status: (validatedData.publish_date ? "future" : "draft") as "future" | "draft",
      date: validatedData.publish_date,
      categories: [category.id],
      tags: tags.map(tag => tag.id),
      featured_media: validatedData.featured_image,
      meta: {
        artist_name: validatedData.artist_name,
        artwork_title: validatedData.artwork_title,
        artwork_year: validatedData.artwork_year,
        artwork_medium: validatedData.artwork_medium,
        artwork_dimensions: validatedData.artwork_dimensions,
        artist_website: validatedData.artist_website,
        artist_social: validatedData.artist_social,
        price_range: validatedData.price_range,
        availability: validatedData.availability,
        gallery_images: validatedData.gallery_images,
        content_type: "art_spotlight"
      }
    };

    return await this.wordpressClient.createPost(postData);
  }

  private generateArtSpotlightContent(data: z.infer<typeof ArtSpotlightSchema>): string {
    return `
<!-- wp:paragraph -->
<p class="has-large-font-size">Discover the captivating world of <strong>${data.artist_name}</strong> and their stunning piece, "${data.artwork_title}".</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">About the Artist</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${data.artist_bio}</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Featured Artwork: "${data.artwork_title}"</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${data.artwork_description}</p>
<!-- /wp:paragraph -->

${data.artwork_year || data.artwork_medium || data.artwork_dimensions ? `
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Artwork Details</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
${data.artwork_year ? `<li><strong>Year:</strong> ${data.artwork_year}</li>` : ''}
${data.artwork_medium ? `<li><strong>Medium:</strong> ${data.artwork_medium}</li>` : ''}
${data.artwork_dimensions ? `<li><strong>Dimensions:</strong> ${data.artwork_dimensions}</li>` : ''}
${data.price_range ? `<li><strong>Price Range:</strong> ${data.price_range}</li>` : ''}
${data.availability ? `<li><strong>Availability:</strong> ${data.availability}</li>` : ''}
</ul>
<!-- /wp:list -->
` : ''}

${data.gallery_images?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Gallery</h2>
<!-- /wp:heading -->

<!-- wp:gallery {"columns":3,"linkTo":"media"} -->
<figure class="wp-block-gallery has-nested-images columns-3 is-cropped">
${data.gallery_images.map(imageId => `
<!-- wp:image {"id":${imageId},"linkDestination":"media"} -->
<figure class="wp-block-image"><a href="#"><img src="#" alt="" class="wp-image-${imageId}"/></a></figure>
<!-- /wp:image -->
`).join('')}
</figure>
<!-- /wp:gallery -->
` : ''}

${data.artist_website || data.artist_social ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Connect with the Artist</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Learn more about ${data.artist_name} and their work:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
${data.artist_website ? `<li><a href="${data.artist_website}" target="_blank" rel="noopener">Official Website</a></li>` : ''}
${Object.entries(data.artist_social || {}).map(([platform, url]) => 
  `<li><a href="${url}" target="_blank" rel="noopener">${platform.charAt(0).toUpperCase() + platform.slice(1)}</a></li>`
).join('')}
</ul>
<!-- /wp:list -->
` : ''}

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:paragraph -->
<p><em>Interested in featuring your artwork on Art of Space? <a href="/contact">Contact us</a> to learn about our submission process.</em></p>
<!-- /wp:paragraph -->
    `.trim();
  }

  private generateArtSpotlightExcerpt(data: z.infer<typeof ArtSpotlightSchema>): string {
    return `Discover the captivating world of ${data.artist_name} and their stunning piece, "${data.artwork_title}". Learn about the artist's background, creative process, and the inspiration behind this remarkable artwork.`;
  }

  async createCollectionAnnouncement(data: z.infer<typeof CollectionAnnouncementSchema>): Promise<WordPressPost> {
    const validatedData = CollectionAnnouncementSchema.parse(data);

    const title = `New Collection: ${validatedData.collection_name}${validatedData.artist_name ? ` by ${validatedData.artist_name}` : ''}`;
    const content = this.generateCollectionContent(validatedData);
    const excerpt = this.generateCollectionExcerpt(validatedData);

    const category = await this.ensureCategory("Collection Announcements", "New art collections and featured artist series");
    
    const tags = await this.ensureTags([
      "new collection",
      "collection announcement",
      validatedData.collection_name,
      ...(validatedData.artist_name ? [validatedData.artist_name] : []),
      ...(validatedData.tags || [])
    ]);

    const postData = {
      title: { rendered: title },
      content: { rendered: content, protected: false },
      excerpt: { rendered: excerpt, protected: false },
      status: (validatedData.launch_date ? "future" : "draft") as "future" | "draft",
      date: validatedData.launch_date,
      categories: [category.id],
      tags: tags.map(tag => tag.id),
      featured_media: validatedData.featured_image,
      meta: {
        collection_name: validatedData.collection_name,
        artist_name: validatedData.artist_name,
        launch_date: validatedData.launch_date,
        collection_theme: validatedData.collection_theme,
        featured_artworks: validatedData.featured_artworks,
        gallery_images: validatedData.gallery_images,
        content_type: "collection_announcement"
      }
    };

    return await this.wordpressClient.createPost(postData);
  }

  private generateCollectionContent(data: z.infer<typeof CollectionAnnouncementSchema>): string {
    return `
<!-- wp:paragraph -->
<p class="has-large-font-size">We're excited to introduce <strong>${data.collection_name}</strong>${data.artist_name ? ` by renowned artist ${data.artist_name}` : ''} - a stunning new addition to our curated art collection.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>${data.collection_description}</p>
<!-- /wp:paragraph -->

${data.collection_theme ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Collection Theme</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${data.collection_theme}</p>
<!-- /wp:paragraph -->
` : ''}

${data.inspiration ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Artist's Inspiration</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${data.inspiration}</p>
<!-- /wp:paragraph -->
` : ''}

${data.featured_artworks?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Featured Pieces</h2>
<!-- /wp:heading -->

${data.featured_artworks.map((artwork, index) => `
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column {"width":"66.66%"} -->
<div class="wp-block-column" style="flex-basis:66.66%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">"${artwork.title}"</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${artwork.description}</p>
<!-- /wp:paragraph -->

${artwork.price ? `
<!-- wp:paragraph -->
<p><strong>Price:</strong> ${artwork.price}</p>
<!-- /wp:paragraph -->
` : ''}
</div>
<!-- /wp:column -->

${artwork.image_id ? `
<!-- wp:column {"width":"33.33%"} -->
<div class="wp-block-column" style="flex-basis:33.33%">
<!-- wp:image {"id":${artwork.image_id},"linkDestination":"media"} -->
<figure class="wp-block-image"><a href="#"><img src="#" alt="${artwork.title}" class="wp-image-${artwork.image_id}"/></a></figure>
<!-- /wp:image -->
</div>
<!-- /wp:column -->
` : ''}
</div>
<!-- /wp:columns -->

${index < (data.featured_artworks?.length || 0) - 1 ? `
<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->
` : ''}
`).join('')}
` : ''}

${data.launch_date ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Launch Details</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>Collection Launch:</strong> ${new Date(data.launch_date).toLocaleDateString('en-US', { 
  weekday: 'long', 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric' 
})}</p>
<!-- /wp:paragraph -->
` : ''}

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:paragraph -->
<p><em>Stay tuned for more updates about ${data.collection_name}. <a href="/collections">Browse our full collection</a> or <a href="/contact">contact us</a> for more information about available pieces.</em></p>
<!-- /wp:paragraph -->
    `.trim();
  }

  private generateCollectionExcerpt(data: z.infer<typeof CollectionAnnouncementSchema>): string {
    return `Introducing ${data.collection_name}${data.artist_name ? ` by ${data.artist_name}` : ''} - a stunning new addition to our curated art collection. ${data.collection_description.substring(0, 100)}...`;
  }

  async createHowToGuide(data: z.infer<typeof HowToGuideSchema>): Promise<WordPressPost> {
    const validatedData = HowToGuideSchema.parse(data);

    const title = `How To: ${validatedData.guide_title}`;
    const content = this.generateHowToContent(validatedData);
    const excerpt = this.generateHowToExcerpt(validatedData);

    const category = await this.ensureCategory("Art Care Guides", "Expert guides for art care, display, and maintenance");
    
    const tags = await this.ensureTags([
      "how to",
      "art care",
      validatedData.guide_type,
      validatedData.difficulty_level,
      ...(validatedData.tags || [])
    ]);

    const postData = {
      title: { rendered: title },
      content: { rendered: content, protected: false },
      excerpt: { rendered: excerpt, protected: false },
      status: "draft" as const,
      categories: [category.id],
      tags: tags.map(tag => tag.id),
      featured_media: validatedData.featured_image,
      meta: {
        guide_type: validatedData.guide_type,
        difficulty_level: validatedData.difficulty_level,
        time_required: validatedData.time_required,
        materials_needed: validatedData.materials_needed,
        content_type: "how_to_guide"
      }
    };

    return await this.wordpressClient.createPost(postData);
  }

  private generateHowToContent(data: z.infer<typeof HowToGuideSchema>): string {
    return `
<!-- wp:paragraph -->
<p class="has-large-font-size">Learn how to ${data.guide_title.toLowerCase()} with this comprehensive ${data.difficulty_level}-level guide.</p>
<!-- /wp:paragraph -->

<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column {"width":"50%"} -->
<div class="wp-block-column" style="flex-basis:50%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Guide Overview</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>Difficulty:</strong> ${data.difficulty_level.charAt(0).toUpperCase() + data.difficulty_level.slice(1)}</li>
${data.time_required ? `<li><strong>Time Required:</strong> ${data.time_required}</li>` : ''}
<li><strong>Type:</strong> ${data.guide_type.charAt(0).toUpperCase() + data.guide_type.slice(1).replace('_', ' ')}</li>
</ul>
<!-- /wp:list -->
</div>
<!-- /wp:column -->

${data.materials_needed?.length ? `
<!-- wp:column {"width":"50%"} -->
<div class="wp-block-column" style="flex-basis:50%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Materials Needed</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
${data.materials_needed.map(material => `<li>${material}</li>`).join('')}
</ul>
<!-- /wp:list -->
</div>
<!-- /wp:column -->
` : ''}
</div>
<!-- /wp:columns -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Step-by-Step Instructions</h2>
<!-- /wp:heading -->

${data.steps.map(step => `
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Step ${step.step_number}: ${step.title}</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${step.description}</p>
<!-- /wp:paragraph -->

${step.image_id ? `
<!-- wp:image {"id":${step.image_id},"align":"center","linkDestination":"media"} -->
<figure class="wp-block-image aligncenter"><a href="#"><img src="#" alt="Step ${step.step_number}: ${step.title}" class="wp-image-${step.image_id}"/></a></figure>
<!-- /wp:image -->
` : ''}

${step.tips?.length ? `
<!-- wp:group {"backgroundColor":"light-gray","className":"tips-box"} -->
<div class="wp-block-group tips-box has-light-gray-background-color has-background">
<!-- wp:heading {"level":4} -->
<h4 class="wp-block-heading">💡 Pro Tips</h4>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
${step.tips.map(tip => `<li>${tip}</li>`).join('')}
</ul>
<!-- /wp:list -->
</div>
<!-- /wp:group -->
` : ''}
`).join('')}

${data.expert_tips?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Expert Tips</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
${data.expert_tips.map(tip => `<li>${tip}</li>`).join('')}
</ul>
<!-- /wp:list -->
` : ''}

${data.common_mistakes?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Common Mistakes to Avoid</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
${data.common_mistakes.map(mistake => `<li>${mistake}</li>`).join('')}
</ul>
<!-- /wp:list -->
` : ''}

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:paragraph -->
<p><em>Need more art care advice? Check out our <a href="/category/art-care-guides">complete collection of guides</a> or <a href="/contact">reach out to our experts</a> for personalized recommendations.</em></p>
<!-- /wp:paragraph -->
    `.trim();
  }

  private generateHowToExcerpt(data: z.infer<typeof HowToGuideSchema>): string {
    return `Learn how to ${data.guide_title.toLowerCase()} with this comprehensive ${data.difficulty_level}-level guide. Perfect for art lovers looking to properly ${data.guide_type.replace('_', ' ')} their collection.`;
  }

  async createSeasonalContent(data: z.infer<typeof SeasonalContentSchema>): Promise<WordPressPost> {
    const validatedData = SeasonalContentSchema.parse(data);

    const title = validatedData.title;
    const content = this.generateSeasonalContent(validatedData);
    const excerpt = this.generateSeasonalExcerpt(validatedData);

    const category = await this.ensureCategory("Seasonal Collections", "Art collections and styling for every season");
    
    const tags = await this.ensureTags([
      validatedData.season,
      validatedData.content_type.replace('_', ' '),
      "seasonal art",
      "home decor",
      ...(validatedData.tags || [])
    ]);

    const postData = {
      title: { rendered: title },
      content: { rendered: content, protected: false },
      excerpt: { rendered: excerpt, protected: false },
      status: "draft" as const,
      categories: [category.id],
      tags: tags.map(tag => tag.id),
      featured_media: validatedData.featured_image,
      meta: {
        season: validatedData.season,
        content_type: validatedData.content_type,
        featured_artworks: validatedData.featured_artworks,
        styling_tips: validatedData.styling_tips,
        color_palette: validatedData.color_palette,
        mood_description: validatedData.mood_description,
        content_type_meta: "seasonal_content"
      }
    };

    return await this.wordpressClient.createPost(postData);
  }

  private generateSeasonalContent(data: z.infer<typeof SeasonalContentSchema>): string {
    const seasonCapitalized = data.season.charAt(0).toUpperCase() + data.season.slice(1).replace('_', ' ');
    
    return `
<!-- wp:paragraph -->
<p class="has-large-font-size">Embrace the beauty of ${seasonCapitalized.toLowerCase()} with our curated selection of artworks that capture the essence of this magical time of year.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>${data.description}</p>
<!-- /wp:paragraph -->

${data.mood_description ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Seasonal Mood</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${data.mood_description}</p>
<!-- /wp:paragraph -->
` : ''}

${data.color_palette?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Color Palette</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This ${data.season} season is defined by a beautiful palette of colors:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
${data.color_palette.map(color => `<li><strong>${color}</strong></li>`).join('')}
</ul>
<!-- /wp:list -->
` : ''}

${data.featured_artworks?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Featured ${seasonCapitalized} Artworks</h2>
<!-- /wp:heading -->

${data.featured_artworks.map((artwork, index) => `
<!-- wp:columns -->
<div class="wp-block-columns">
${artwork.image_id ? `
<!-- wp:column {"width":"33.33%"} -->
<div class="wp-block-column" style="flex-basis:33.33%">
<!-- wp:image {"id":${artwork.image_id},"linkDestination":"media"} -->
<figure class="wp-block-image"><a href="#"><img src="#" alt="${artwork.title}" class="wp-image-${artwork.image_id}"/></a></figure>
<!-- /wp:image -->
</div>
<!-- /wp:column -->
` : ''}

<!-- wp:column {"width":"66.66%"} -->
<div class="wp-block-column" style="flex-basis:66.66%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">"${artwork.title}"${artwork.artist ? ` by ${artwork.artist}` : ''}</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${artwork.description}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><em>${seasonCapitalized} Connection:</em> ${artwork.seasonal_relevance}</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->

${index < (data.featured_artworks?.length || 0) - 1 ? `
<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->
` : ''}
`).join('')}
` : ''}

${data.styling_tips?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">${seasonCapitalized} Styling Tips</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Make the most of your ${data.season} art display with these expert styling suggestions:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
${data.styling_tips.map(tip => `<li>${tip}</li>`).join('')}
</ul>
<!-- /wp:list -->
` : ''}

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:paragraph -->
<p><em>Ready to refresh your space for ${data.season}? <a href="/collections">Explore our full collection</a> or <a href="/contact">get personalized styling advice</a> from our art consultants.</em></p>
<!-- /wp:paragraph -->
    `.trim();
  }

  private generateSeasonalExcerpt(data: z.infer<typeof SeasonalContentSchema>): string {
    const seasonCapitalized = data.season.charAt(0).toUpperCase() + data.season.slice(1).replace('_', ' ');
    return `Embrace the beauty of ${seasonCapitalized.toLowerCase()} with our curated selection of artworks and styling tips. ${data.description.substring(0, 100)}...`;
  }

  async createArtistInterview(data: z.infer<typeof ArtistInterviewSchema>): Promise<WordPressPost> {
    const validatedData = ArtistInterviewSchema.parse(data);

    const title = `Artist Interview: ${validatedData.artist_name}`;
    const content = this.generateInterviewContent(validatedData);
    const excerpt = this.generateInterviewExcerpt(validatedData);

    const category = await this.ensureCategory("Artist Interviews", "In-depth conversations with featured artists");
    
    const tags = await this.ensureTags([
      "artist interview",
      validatedData.artist_name,
      "featured artist",
      "artist spotlight",
      ...(validatedData.tags || [])
    ]);

    const postData = {
      title: { rendered: title },
      content: { rendered: content, protected: false },
      excerpt: { rendered: excerpt, protected: false },
      status: "draft" as const,
      categories: [category.id],
      tags: tags.map(tag => tag.id),
      featured_media: validatedData.featured_image,
      meta: {
        artist_name: validatedData.artist_name,
        featured_artworks: validatedData.featured_artworks,
        artist_influences: validatedData.artist_influences,
        upcoming_exhibitions: validatedData.upcoming_exhibitions,
        contact_info: validatedData.contact_info,
        content_type: "artist_interview"
      }
    };

    return await this.wordpressClient.createPost(postData);
  }

  private generateInterviewContent(data: z.infer<typeof ArtistInterviewSchema>): string {
    return `
<!-- wp:paragraph -->
<p class="has-large-font-size">Join us for an intimate conversation with <strong>${data.artist_name}</strong>, exploring their artistic journey, creative process, and the stories behind their remarkable works.</p>
<!-- /wp:paragraph -->

${data.artist_photo ? `
<!-- wp:image {"id":${data.artist_photo},"align":"center","className":"artist-photo"} -->
<figure class="wp-block-image aligncenter artist-photo"><img src="#" alt="${data.artist_name}" class="wp-image-${data.artist_photo}"/></figure>
<!-- /wp:image -->
` : ''}

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">About ${data.artist_name}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${data.artist_bio}</p>
<!-- /wp:paragraph -->

${data.artist_statement ? `
<!-- wp:quote -->
<blockquote class="wp-block-quote">
<p>"${data.artist_statement}"</p>
<cite>— ${data.artist_name}</cite>
</blockquote>
<!-- /wp:quote -->
` : ''}

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">The Interview</h2>
<!-- /wp:heading -->

${data.interview_questions.map((qa, index) => `
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">${qa.question}</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>${data.artist_name}:</strong> ${qa.answer}</p>
<!-- /wp:paragraph -->

${index < data.interview_questions.length - 1 ? `
<!-- wp:separator {"className":"interview-separator"} -->
<hr class="wp-block-separator has-alpha-channel-opacity interview-separator"/>
<!-- /wp:separator -->
` : ''}
`).join('')}

${data.featured_artworks?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Featured Works</h2>
<!-- /wp:heading -->

${data.featured_artworks.map((artwork, index) => `
<!-- wp:columns -->
<div class="wp-block-columns">
${artwork.image_id ? `
<!-- wp:column {"width":"40%"} -->
<div class="wp-block-column" style="flex-basis:40%">
<!-- wp:image {"id":${artwork.image_id},"linkDestination":"media"} -->
<figure class="wp-block-image"><a href="#"><img src="#" alt="${artwork.title}" class="wp-image-${artwork.image_id}"/></a></figure>
<!-- /wp:image -->
</div>
<!-- /wp:column -->
` : ''}

<!-- wp:column {"width":"60%"} -->
<div class="wp-block-column" style="flex-basis:60%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">"${artwork.title}"${artwork.year ? ` (${artwork.year})` : ''}</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>${artwork.description}</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->

${index < (data.featured_artworks?.length || 0) - 1 ? `
<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->
` : ''}
`).join('')}
` : ''}

${data.artist_influences?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Artistic Influences</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
${data.artist_influences.map(influence => `<li>${influence}</li>`).join('')}
</ul>
<!-- /wp:list -->
` : ''}

${data.upcoming_exhibitions?.length ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Upcoming Exhibitions</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
${data.upcoming_exhibitions.map(exhibition => `<li>${exhibition}</li>`).join('')}
</ul>
<!-- /wp:list -->
` : ''}

${data.contact_info ? `
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Connect with ${data.artist_name}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Stay connected with ${data.artist_name} and follow their artistic journey:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
${data.contact_info.website ? `<li><a href="${data.contact_info.website}" target="_blank" rel="noopener">Official Website</a></li>` : ''}
${Object.entries(data.contact_info.social_media || {}).map(([platform, url]) => 
  `<li><a href="${url}" target="_blank" rel="noopener">${platform.charAt(0).toUpperCase() + platform.slice(1)}</a></li>`
).join('')}
${data.contact_info.gallery_representation ? `<li><strong>Gallery Representation:</strong> ${data.contact_info.gallery_representation}</li>` : ''}
</ul>
<!-- /wp:list -->
` : ''}

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:paragraph -->
<p><em>Thank you to ${data.artist_name} for sharing their insights with us. Interested in being featured? <a href="/contact">Contact us</a> about our artist interview series.</em></p>
<!-- /wp:paragraph -->
    `.trim();
  }

  private generateInterviewExcerpt(data: z.infer<typeof ArtistInterviewSchema>): string {
    return `Join us for an intimate conversation with ${data.artist_name}, exploring their artistic journey, creative process, and the stories behind their remarkable works.`;
  }

  // Helper methods
  private async ensureCategory(name: string, description: string): Promise<WordPressCategory> {
    try {
      const { categories } = await this.wordpressClient.getCategories({ search: name, per_page: 1 });
      
      if (categories.length > 0) {
        return categories[0];
      }

      return await this.wordpressClient.createCategory({
        name,
        description,
        slug: name.toLowerCase().replace(/\s+/g, '-')
      });
    } catch (error) {
      throw new Error(`Failed to ensure category "${name}": ${error}`);
    }
  }

  private async ensureTags(tagNames: string[]): Promise<WordPressTag[]> {
    const tags: WordPressTag[] = [];

    for (const tagName of tagNames) {
      try {
        const { tags: existingTags } = await this.wordpressClient.getTags({ search: tagName, per_page: 1 });
        
        if (existingTags.length > 0) {
          tags.push(existingTags[0]);
        } else {
          const newTag = await this.wordpressClient.createTag({
            name: tagName,
            slug: tagName.toLowerCase().replace(/\s+/g, '-')
          });
          tags.push(newTag);
        }
      } catch (error) {
        console.error(`Failed to ensure tag "${tagName}":`, error);
        // Continue with other tags if one fails
      }
    }

    return tags;
  }
}