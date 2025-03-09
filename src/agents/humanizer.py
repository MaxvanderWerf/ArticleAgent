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
        
        # Apply humanizing techniques
        humanized_content = self._add_personal_voice(article_content, style, platform)
        humanized_content = self._add_imperfections(humanized_content, style)
        
        return {
            "humanized_article": humanized_content,
            "original_article": article_content
        }
    
    def _add_personal_voice(self, content: str, style: str, platform: str = None) -> str:
        """
        Add a personal voice to the article.
        
        Args:
            content: The article content
            style: The writing style
            platform: Optional publishing platform
            
        Returns:
            Article content with personal voice
        """
        platform_str = f" for {platform}" if platform else ""
        
        prompt = f"""
        Revise this article{platform_str} to add a more authentic, human voice.
        
        Focus on:
        - Adding occasional first-person perspective where appropriate
        - Incorporating personal anecdotes or reflections that feel genuine
        - Using more conversational language and contractions
        - Adding rhetorical questions that engage the reader directly
        - Maintaining a {style} style throughout
        
        Make the article feel like it was written by a real person with genuine experiences and opinions,
        without changing the core content or expertise level.
        
        ARTICLE:
        {content}
        
        HUMANIZED ARTICLE:
        """
        
        return generate_text(prompt)
    
    def _add_imperfections(self, content: str, style: str) -> str:
        """
        Add subtle imperfections to make the content feel more human.
        
        Args:
            content: The article content
            style: The writing style
            
        Returns:
            Article content with subtle imperfections
        """
        # Only apply this to conversational or storytelling styles
        if style not in ["conversational", "storytelling"]:
            return content
            
        prompt = f"""
        Revise this article to add subtle, natural imperfections that make it feel more authentically human.
        
        Focus on:
        - Adding occasional parenthetical asides or tangential thoughts
        - Including a few natural thought transitions (e.g., "Actually, that reminds me...")
        - Adding one or two places where a point is slightly reconsidered
        - Incorporating subtle verbal tics that real writers use (e.g., "you know," "I think," "perhaps")
        
        The imperfections should be subtle and sparse - the article should still be professional and well-written,
        just with a touch of human authenticity. Don't overdo it.
        
        ARTICLE:
        {content}
        
        HUMANIZED ARTICLE:
        """
        
        return generate_text(prompt)
    
    def _add_personality_traits(self, content: str, traits: List[str] = None) -> str:
        """
        Add specific personality traits to the writing.
        
        Args:
            content: The article content
            traits: List of personality traits to incorporate
            
        Returns:
            Article content with personality traits
        """
        if not traits:
            # Default traits if none specified
            traits = ["thoughtful", "curious", "empathetic"]
            
        traits_str = ", ".join(traits)
        
        prompt = f"""
        Revise this article to incorporate the following personality traits: {traits_str}.
        
        The personality should come through in the writing style, word choice, and perspective,
        without explicitly stating "I am {traits_str}."
        
        Make these traits subtle but noticeable, as if the article was written by someone with these characteristics.
        Don't change the core content or expertise level of the article.
        
        ARTICLE:
        {content}
        
        PERSONALITY-INFUSED ARTICLE:
        """
        
        return generate_text(prompt) 