"""
Reviewer Agent for the Agentic Writer System.
Responsible for reviewing and improving article content.
"""

from typing import Dict, Optional, List

from src.agents.base import Agent
from src.utils.llm import generate_text

class ReviewerAgent(Agent):
    """
    Agent responsible for reviewing and improving article content.
    """
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """
        Review and improve article content.
        
        Args:
            task: Description of the review task
            context: Dictionary containing article content and metadata
            
        Returns:
            Dictionary containing the improved article
        """
        if not context:
            context = {}
            
        article_content = context.get("article_content", "")
        style = context.get("style", "conversational")
        platform = context.get("platform")
        
        self.log("Reviewing and improving article content")
        
        # Perform different types of improvements
        improved_content = self._improve_readability(article_content, style, platform)
        improved_content = self._improve_engagement(improved_content, style, platform)
        improved_content = self._improve_coherence(improved_content, style, platform)
        
        return {
            "improved_article": improved_content,
            "original_article": article_content,
            "improvements_made": self._summarize_improvements(article_content, improved_content)
        }
    
    def _improve_readability(self, content: str, style: str, platform: str = None) -> str:
        """
        Improve the readability of the article.
        
        Args:
            content: The article content
            style: The writing style
            platform: Optional publishing platform
            
        Returns:
            Improved article content
        """
        platform_str = f" for {platform}" if platform else ""
        
        prompt = f"""
        Review and improve the readability of this article{platform_str}. 
        
        Focus on:
        - Simplifying complex sentences
        - Breaking up long paragraphs
        - Adding subheadings where appropriate
        - Ensuring consistent tone in {style} style
        - Improving transitions between ideas
        
        Make the article more accessible without changing the core content or meaning.
        
        ARTICLE:
        {content}
        
        IMPROVED ARTICLE:
        """
        
        return generate_text(prompt)
    
    def _improve_engagement(self, content: str, style: str, platform: str = None) -> str:
        """
        Improve the engagement factor of the article.
        
        Args:
            content: The article content
            style: The writing style
            platform: Optional publishing platform
            
        Returns:
            Improved article content
        """
        platform_str = f" for {platform}" if platform else ""
        
        prompt = f"""
        Review and improve the engagement of this article{platform_str}.
        
        Focus on:
        - Adding compelling examples or anecdotes where appropriate
        - Enhancing the hook in the introduction
        - Making the conclusion more impactful
        - Adding rhetorical questions or thought-provoking statements
        - Maintaining a {style} style throughout
        
        Make the article more engaging without significantly increasing its length or changing its core message.
        
        ARTICLE:
        {content}
        
        IMPROVED ARTICLE:
        """
        
        return generate_text(prompt)
    
    def _improve_coherence(self, content: str, style: str, platform: str = None) -> str:
        """
        Improve the coherence and flow of the article.
        
        Args:
            content: The article content
            style: The writing style
            platform: Optional publishing platform
            
        Returns:
            Improved article content
        """
        platform_str = f" for {platform}" if platform else ""
        
        prompt = f"""
        Review and improve the coherence and flow of this article{platform_str}.
        
        Focus on:
        - Ensuring logical progression of ideas
        - Strengthening connections between sections
        - Removing redundancies or repetitive points
        - Ensuring consistent terminology throughout
        - Maintaining a {style} style
        
        Make the article flow more naturally without changing its core structure or message.
        
        ARTICLE:
        {content}
        
        IMPROVED ARTICLE:
        """
        
        return generate_text(prompt)
    
    def _summarize_improvements(self, original: str, improved: str) -> Dict:
        """
        Summarize the improvements made to the article.
        
        Args:
            original: The original article content
            improved: The improved article content
            
        Returns:
            Dictionary summarizing the improvements
        """
        prompt = f"""
        Compare the original and improved versions of this article and provide a concise summary of the improvements made.
        
        Focus on identifying:
        - Readability improvements
        - Engagement enhancements
        - Coherence and flow improvements
        - Any other significant changes
        
        Format your response as a JSON object with these categories as keys and brief descriptions as values.
        
        ORIGINAL:
        {original[:1000]}... (truncated)
        
        IMPROVED:
        {improved[:1000]}... (truncated)
        """
        
        improvements_text = generate_text(prompt)
        
        # Try to parse as JSON, but provide a fallback if it's not valid JSON
        try:
            import json
            return json.loads(improvements_text)
        except:
            return {
                "readability": "Improved sentence structure and paragraph organization",
                "engagement": "Enhanced examples and narrative elements",
                "coherence": "Strengthened transitions and logical flow",
                "other": improvements_text
            } 