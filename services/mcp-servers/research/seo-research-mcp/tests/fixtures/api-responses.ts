/**
 * Test Fixtures - Mock API Responses
 * Contains realistic mock data for all integrated APIs
 */

export const mockDataForSEOKeywordResponse = {
  version: "0.1.20240801",
  status_code: 20000,
  status_message: "Ok.",
  time: "0.1234 sec.",
  cost: 0.02,
  tasks_count: 1,
  tasks_error: 0,
  tasks: [{
    id: "12345678-1234-1234-1234-123456789012",
    status_code: 20000,
    status_message: "Ok.",
    time: "0.0987 sec.",
    cost: 0.02,
    result_count: 1,
    path: ["v3", "keywords_data", "google_ads", "search_volume", "live"],
    data: {
      api_version: "v3",
      results: [{
        keyword: "email marketing",
        location_code: 2840,
        language_code: "en",
        search_partners: false,
        competition: 0.92,
        competition_level: "HIGH",
        cpc: 2.45,
        search_volume: 74000,
        low_top_of_page_bid: 1.23,
        high_top_of_page_bid: 4.56,
        categories: [10178, 10179],
        monthly_searches: [
          { year: 2024, month: 1, search_volume: 74000 },
          { year: 2024, month: 2, search_volume: 81000 }
        ]
      }]
    }
  }]
};

export const mockDataForSEOBacklinkResponse = {
  version: "0.1.20240801",
  status_code: 20000,
  status_message: "Ok.",
  time: "0.2345 sec.",
  cost: 0.05,
  tasks_count: 1,
  tasks_error: 0,
  tasks: [{
    id: "87654321-4321-4321-4321-210987654321",
    status_code: 20000,
    status_message: "Ok.",
    time: "0.1876 sec.",
    cost: 0.05,
    result_count: 100,
    path: ["v3", "backlinks", "backlinks", "live"],
    data: {
      api_version: "v3",
      results: [{
        target: "example.com",
        mode: "as_is",
        items_count: 2,
        items: [
          {
            type: "backlink",
            domain_from: "authority-site.com",
            url_from: "https://authority-site.com/blog/email-marketing-guide",
            url_to: "https://example.com/features",
            tld_from: "com",
            is_new: false,
            is_lost: false,
            crawl_progress: "finished",
            crawl_time: "2024-01-15 10:30:00 +00:00",
            updated_time: "2024-01-15 10:30:00 +00:00",
            page_from_rank: 85,
            domain_from_rank: 92,
            page_from_page_rank: 7.2,
            domain_from_page_rank: 8.1,
            anchor: "best email marketing platform",
            text_pre: "Looking for the",
            text_post: "for your business?",
            semantic_location: "main_content",
            link_attribute: "dofollow",
            page_from_external_links: 45,
            page_from_internal_links: 23,
            page_from_size: 12543,
            encoding: "utf-8",
            language: "en",
            url_from_https: true,
            domain_from_ip: "192.168.1.1",
            domain_from_country: "US"
          }
        ]
      }]
    }
  }]
};

export const mockBraveSearchResponse = {
  type: "search",
  discussions: {
    type: "search_result",
    results: [
      {
        type: "search_result",
        url: "https://reddit.com/r/marketing/comments/email-marketing-tips",
        title: "Best Email Marketing Tips - Reddit Discussion",
        description: "Community discussion about effective email marketing strategies and tools.",
        age: "2024-01-10T00:00:00",
        page_age: "2024-01-10T00:00:00",
        profile: {
          name: "Reddit",
          url: "https://reddit.com",
          long_name: "reddit.com"
        },
        language: "en",
        family_friendly: true
      }
    ]
  },
  web: {
    type: "search",
    results: [
      {
        type: "search_result",
        url: "https://example.com/email-marketing-guide",
        title: "Complete Email Marketing Guide 2024",
        description: "Learn the best email marketing strategies, tools, and techniques to grow your business with effective email campaigns.",
        age: "2024-01-15T00:00:00",
        page_age: "2024-01-15T00:00:00",
        profile: {
          name: "Example Marketing",
          url: "https://example.com",
          long_name: "example.com"
        },
        language: "en",
        family_friendly: true,
        extra_snippets: [
          "Email marketing remains one of the highest ROI marketing channels",
          "Segmentation can improve email performance by up to 760%"
        ]
      }
    ]
  }
};

export const mockPerplexityResponse = {
  id: "pplx_12345",
  object: "chat.completion",
  created: 1704067200,
  model: "llama-3.1-sonar-small-128k-online",
  choices: [{
    index: 0,
    finish_reason: "stop",
    message: {
      role: "assistant",
      content: "Based on recent search results, email marketing continues to be one of the most effective digital marketing channels in 2024. Key trends include increased personalization, AI-driven automation, and interactive email content. The average ROI for email marketing is $42 for every $1 spent, making it highly cost-effective for businesses of all sizes."
    },
    delta: {
      role: "assistant",
      content: ""
    }
  }],
  usage: {
    prompt_tokens: 50,
    completion_tokens: 75,
    total_tokens: 125
  }
};

export const mockTavilyResponse = {
  query: "email marketing trends 2024",
  follow_up_questions: [
    "What are the best email marketing platforms in 2024?",
    "How to improve email deliverability rates?",
    "What are the latest email design trends?"
  ],
  answer: "Email marketing in 2024 focuses on hyper-personalization, AI-driven content optimization, and interactive elements like AMP emails. Key trends include zero-party data collection, advanced segmentation, and cross-channel integration.",
  images: [],
  results: [
    {
      title: "Email Marketing Trends 2024: What Marketers Need to Know",
      url: "https://marketingland.com/email-trends-2024",
      content: "The email marketing landscape continues to evolve with new technologies and consumer expectations. Personalization has moved beyond simple name insertion to dynamic content based on behavior, preferences, and real-time data.",
      score: 0.95,
      raw_content: null
    }
  ],
  response_time: 1.23
};

export const mockSerpAPIResponse = {
  search_metadata: {
    id: "search_12345",
    status: "Success",
    json_endpoint: "https://serpapi.com/searches/search_12345.json",
    created_at: "2024-01-15T10:30:00.000Z",
    processed_at: "2024-01-15T10:30:01.234Z",
    google_url: "https://www.google.com/search?q=email+marketing&oq=email+marketing",
    raw_html_file: "https://serpapi.com/searches/search_12345.html",
    total_time_taken: 1.23
  },
  search_parameters: {
    engine: "google",
    q: "email marketing",
    location_requested: "United States",
    location_used: "United States",
    google_domain: "google.com",
    hl: "en",
    gl: "us",
    device: "desktop"
  },
  search_information: {
    organic_results_state: "Results for exact spelling",
    query_displayed: "email marketing",
    total_results: 2840000000,
    time_taken_displayed: 0.45
  },
  organic_results: [
    {
      position: 1,
      title: "Email Marketing Platform | Send Better Email | Mailchimp",
      link: "https://mailchimp.com/marketing-platform/email/",
      displayed_link: "https://mailchimp.com › marketing-platform › email",
      snippet: "Mailchimp's email marketing platform helps you design better emails, automate email sequences, and analyze performance with advanced analytics.",
      snippet_highlighted_words: ["email marketing", "emails", "email"],
      sitelinks: {
        inline: [
          {
            title: "Email Templates",
            link: "https://mailchimp.com/email-templates/"
          },
          {
            title: "Email Automation",
            link: "https://mailchimp.com/features/email-automation/"
          }
        ]
      },
      rich_snippet: {
        top: {
          detected_extensions: {
            rating: 4.5,
            reviews: 12543,
            price: "Free plan available"
          }
        }
      }
    }
  ],
  related_searches: [
    {
      query: "email marketing best practices",
      link: "https://www.google.com/search?q=email+marketing+best+practices"
    },
    {
      query: "email marketing automation",
      link: "https://www.google.com/search?q=email+marketing+automation"
    }
  ]
};

export const mockOpenAIResponse = {
  id: "chatcmpl-12345",
  object: "chat.completion",
  created: 1704067200,
  model: "gpt-4",
  choices: [{
    index: 0,
    message: {
      role: "assistant",
      content: JSON.stringify({
        keywords: [
          {
            keyword: "email marketing automation tools",
            searchIntent: "commercial",
            difficulty: "medium",
            relevanceScore: 0.92,
            estimatedVolume: "5000-10000"
          },
          {
            keyword: "best email marketing platform for small business",
            searchIntent: "commercial",
            difficulty: "high",
            relevanceScore: 0.88,
            estimatedVolume: "1000-5000"
          }
        ],
        analysis: "These long-tail keywords target specific user needs and have good commercial intent for email marketing platforms."
      })
    },
    finish_reason: "stop"
  }],
  usage: {
    prompt_tokens: 150,
    completion_tokens: 200,
    total_tokens: 350
  }
};

// Error response examples
export const mockAPIErrorResponse = {
  error: {
    code: "RATE_LIMIT_EXCEEDED",
    message: "API rate limit exceeded. Please try again later.",
    details: {
      retryAfter: 60,
      limit: 100,
      remaining: 0
    }
  }
};

export const mockInvalidAPIKeyResponse = {
  error: {
    code: "INVALID_API_KEY",
    message: "The provided API key is invalid or has expired.",
    details: {
      providedKey: "test-***-key"
    }
  }
}; 