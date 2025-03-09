"""
Humanizer Agent for the Agentic Writer System.
Responsible for adding a human touch to the article content.
"""

from typing import Dict, Optional, List
import random

from src.agents.base import Agent
from src.utils.llm import generate_text

class HumanizerAgent(Agent):
    """
    Agent responsible for adding a human touch to article content.
    """
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """
        Add a human touch to the article content.
        
        Args:
            task: Description of the humanizing task
            context: Dictionary containing article content and metadata
            
        Returns:
            Dictionary containing the humanized article
        """
        if not context:
            context = {}
            
        article_content = context.get("article_content", "")
        style = context.get("style", "conversational")
        platform = context.get("platform")
        
        self.log("Adding human touch to article content")
        
        # Humanize the article in a single call
        humanized_content = self._humanize_article(article_content, style, platform)
        
        return {
            "humanized_article": humanized_content,
            "original_article": article_content
        }
    
    def _humanize_article(self, content: str, style: str, platform: str = None) -> str:
        """
        Add a human touch to the article in a single comprehensive pass.
        
        Args:
            content: The article content
            style: The writing style
            platform: Optional publishing platform
            
        Returns:
            Humanized article content
        """
        platform_str = f" for {platform}" if platform else ""
        
        # Select a few personality traits to incorporate
        personality_traits = random.sample([
            "thoughtful", "curious", "empathetic", "enthusiastic", 
            "analytical", "reflective", "practical", "creative"
        ], 3)
        traits_str = ", ".join(personality_traits)
        
        prompt = f"""
        Revise this article{platform_str} to make it feel more authentically human and engaging.
        
        Add these human elements:
        1. PERSONAL VOICE:
           - Add occasional first-person perspective where appropriate
           - Incorporate personal anecdotes or reflections that feel genuine
           - Use more conversational language and contractions
           - Add rhetorical questions that engage the reader directly
        
        2. NATURAL IMPERFECTIONS (if appropriate for the style):
           - Add occasional parenthetical asides or tangential thoughts
           - Include a few natural thought transitions (e.g., "Actually, that reminds me...")
           - Add one or two places where a point is slightly reconsidered
           - Incorporate subtle verbal tics that real writers use (e.g., "you know," "I think," "perhaps")
        
        3. PERSONALITY:
           - Infuse the writing with these personality traits: {traits_str}
           - The personality should come through in the writing style, word choice, and perspective
           - Don't explicitly state "I am {traits_str}" - show it through the writing
        
        Example of good humanization:
        
        ORIGINAL:
        ```
        Machine learning algorithms process data to identify patterns. These patterns enable predictions about new data.
        ```
        
        HUMANIZED:
        ```
        I've always been fascinated by how machine learning algorithms can sift through mountains of data to uncover hidden patterns. (Trust me, after spending countless late nights debugging my first neural network, this fascination was hard-earned!) These patterns, once identified, allow us to make surprisingly accurate predictions about new data—though, as you might expect, the real-world results aren't always as clean as the textbooks suggest.
        ```
        
        Please maintain the article's core content and expertise level while making it feel like it was written by a real person with genuine experiences and opinions. The humanization should be subtle and appropriate for a {style} style.
        
        ARTICLE:
        {content}
        
        HUMANIZED ARTICLE:
        """
        
        return generate_text(prompt) 