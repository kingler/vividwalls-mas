#!/usr/bin/env python3
"""
Image generation configuration for VividWalls Color Palette Agent.

This module contains configuration settings and prompts for the OpenAI
Image Generation API to ensure consistent, high-quality composite images.

CRITICAL RULE: NO HUMANS OR ANIMALS should ever appear in generated images.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ImageGenerationConfig:
    """Configuration for OpenAI Image Generation API with strict content rules."""
    
    # Model configuration
    model: str = "dall-e-3"
    size: str = "1024x1024"
    quality: str = "hd"
    style: str = "natural"
    
    # CRITICAL NEGATIVE PROMPTS - ALWAYS INCLUDED
    # These are enforced to ensure NO HUMANS OR ANIMALS in any generated images
    negative_prompts: List[str] = field(default_factory=lambda: [
        "NO humans whatsoever",
        "NO people at all", 
        "NO person in any form",
        "NO human figures",
        "NO human silhouettes",
        "NO animals of any kind",
        "NO pets whatsoever",
        "NO dogs anywhere",
        "NO cats anywhere",
        "NO birds anywhere",
        "NO fish or aquatic life",
        "NO insects",
        "NO living creatures",
        "NO faces anywhere",
        "NO hands anywhere",
        "NO body parts",
        "NO human shadows",
        "NO animal shadows",
        "ABSOLUTELY empty of life",
        "ONLY inanimate objects",
        "ONLY furniture and decor",
        "ONLY architectural elements",
        "STRICTLY interior spaces only",
        "COMPLETELY uninhabited"
    ])
    
    # Positive quality prompts
    quality_prompts: List[str] = field(default_factory=lambda: [
        "photorealistic interior",
        "high resolution photography",
        "professional architectural photo",
        "accurate color reproduction",
        "proper perspective and scale",
        "natural interior lighting",
        "sharp architectural details",
        "authentic empty room atmosphere",
        "pristine uninhabited space"
    ])
    
    # Artwork integration prompts
    artwork_prompts: List[str] = field(default_factory=lambda: [
        "artwork perfectly mounted on wall",
        "exact reproduction of the VividWalls artwork",
        "proper scale relative to room",
        "realistic wall mounting and framing",
        "appropriate shadows and reflections",
        "seamless integration with room aesthetic",
        "professional gallery-style presentation"
    ])
    
    def build_prompt(self, 
                    room_description: str,
                    artwork_description: str,
                    wall_position: Dict[str, Any],
                    custom_instructions: Optional[str] = None) -> str:
        """
        Build a comprehensive prompt for image generation with strict content rules.
        
        Args:
            room_description: Description of the room from vision analysis
            artwork_description: Description of the artwork to place
            wall_position: Position details for artwork placement
            custom_instructions: Additional custom instructions
            
        Returns:
            Complete prompt for OpenAI Image Generation API
        """
        logger.info("Building image generation prompt with STRICT no humans/animals rule")
        
        # Start with the main request
        prompt_parts = [
            "Generate a photorealistic interior room image.",
            f"Room description: {room_description}",
            f"Artwork to place: {artwork_description}",
            f"Wall position: {wall_position.get('description', 'centered on the optimal wall')}"
        ]
        
        # Add custom instructions if provided
        if custom_instructions:
            prompt_parts.append(f"Additional requirements: {custom_instructions}")
        
        # CRITICAL: Add negative prompts with maximum emphasis
        prompt_parts.append("\n🚫 ABSOLUTELY CRITICAL RULES - MUST BE FOLLOWED WITHOUT EXCEPTION:")
        prompt_parts.append("━" * 50)
        for neg in self.negative_prompts:
            prompt_parts.append(f"❌ {neg}")
        prompt_parts.append("━" * 50)
        
        # Add what we DO want
        prompt_parts.append("\n✅ REQUIRED ELEMENTS:")
        prompt_parts.extend([f"• {qual}" for qual in self.quality_prompts])
        
        # Add artwork integration requirements
        prompt_parts.append("\n🎨 ARTWORK INTEGRATION:")
        prompt_parts.extend([f"• {art}" for art in self.artwork_prompts])
        
        # Final emphasis
        prompt_parts.append("\n⚠️ FINAL REMINDER: The room must be COMPLETELY EMPTY of any humans, animals, or living creatures. This is NON-NEGOTIABLE.")
        
        # Join all parts
        full_prompt = "\n".join(prompt_parts)
        
        # Log the prompt for debugging (excluding sensitive details)
        logger.debug(f"Generated prompt with {len(self.negative_prompts)} negative constraints")
        logger.info("Prompt includes strict NO HUMANS/ANIMALS enforcement")
        
        return full_prompt
    
    def validate_generation_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate that a generation request follows our strict content rules.
        
        Args:
            request_data: The request data to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If request contains forbidden content
        """
        # List of forbidden terms that indicate humans or animals
        forbidden_terms = [
            # Human-related terms
            "person", "people", "human", "man", "woman", "child", "baby",
            "boy", "girl", "kid", "adult", "teenager", "elderly",
            "face", "hand", "foot", "body", "figure", "silhouette",
            "customer", "visitor", "resident", "owner", "guest",
            
            # Animal-related terms
            "dog", "cat", "pet", "animal", "bird", "fish", "hamster",
            "rabbit", "mouse", "horse", "cow", "pig", "chicken",
            "insect", "bug", "spider", "creature", "wildlife",
            
            # Living being indicators
            "living", "breathing", "moving", "walking", "sitting",
            "standing", "playing", "sleeping", "eating"
        ]
        
        request_text = str(request_data).lower()
        
        # Check for forbidden terms
        for term in forbidden_terms:
            # Allow the term only if it's preceded by "no" or "without"
            if term in request_text:
                # Check if it's negated
                negated = any(f"{neg} {term}" in request_text for neg in ["no", "without", "empty of", "devoid of"])
                if not negated:
                    logger.error(f"Request contains forbidden term: {term}")
                    raise ValueError(
                        f"❌ Generation request REJECTED: Contains reference to '{term}'. "
                        f"VividWalls policy strictly prohibits ANY humans or animals in generated images."
                    )
        
        logger.info("✅ Generation request validated - no humans/animals referenced")
        return True
    
    def post_generation_check(self, generated_prompt: str) -> bool:
        """
        Final check to ensure the generated prompt emphasizes no humans/animals.
        
        Args:
            generated_prompt: The final prompt to be sent to the API
            
        Returns:
            True if prompt is safe
        """
        required_phrases = [
            "NO humans",
            "NO animals",
            "empty of life",
            "uninhabited"
        ]
        
        prompt_lower = generated_prompt.lower()
        
        for phrase in required_phrases:
            if phrase.lower() not in prompt_lower:
                logger.warning(f"Generated prompt missing required phrase: {phrase}")
                return False
        
        logger.info("✅ Post-generation check passed - all safety phrases present")
        return True


# Singleton instance with strict configuration
STRICT_GENERATION_CONFIG = ImageGenerationConfig()


def get_safe_generation_prompt(room_desc: str, 
                              artwork_desc: str,
                              wall_pos: Dict[str, Any],
                              custom: Optional[str] = None) -> str:
    """
    Get a generation prompt that strictly enforces NO HUMANS OR ANIMALS rule.
    
    Args:
        room_desc: Room description
        artwork_desc: Artwork description  
        wall_pos: Wall position info
        custom: Custom instructions
        
    Returns:
        Safe generation prompt with all content rules enforced
    """
    # Validate inputs don't contain forbidden content
    STRICT_GENERATION_CONFIG.validate_generation_request({
        "room": room_desc,
        "artwork": artwork_desc,
        "position": wall_pos,
        "custom": custom
    })
    
    # Build the prompt
    prompt = STRICT_GENERATION_CONFIG.build_prompt(
        room_desc, artwork_desc, wall_pos, custom
    )
    
    # Final safety check
    if not STRICT_GENERATION_CONFIG.post_generation_check(prompt):
        raise ValueError("Generated prompt failed safety check")
    
    return prompt


# Example usage for documentation
if __name__ == "__main__":
    # Example of safe prompt generation
    example_prompt = get_safe_generation_prompt(
        room_desc="Modern living room with beige walls and minimalist furniture",
        artwork_desc="Abstract blue and gold canvas painting, 24x36 inches",
        wall_pos={"description": "centered above the sofa"},
        custom="Ensure proper lighting on the artwork"
    )
    
    print("Example Safe Prompt:")
    print("=" * 80)
    print(example_prompt)
    print("=" * 80) 