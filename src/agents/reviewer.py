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
        
        # If this is a summarize improvements task, handle it separately
        if task.lower().startswith("summarize"):
            if "original_article" in context and "improved_article" in context:
                return {
                    "improvements": self._summarize_improvements(
                        context["original_article"], 
                        context["improved_article"]
                    )
                }
            return {"improvements": {}}
        
        self.log("Reviewing and improving article content")
        
        # Improve the article in a single call
        improved_content = self._improve_article(article_content, style, platform)
        
        return {
            "improved_article": improved_content,
            "original_article": article_content,
            "improvements_made": self._summarize_improvements(article_content, improved_content)
        }
    
    def _improve_article(self, content: str, style: str, platform: str = None) -> str:
        """
        Improve the article in a single comprehensive pass.
        
        Args:
            content: The article content
            style: The writing style
            platform: Optional publishing platform
            
        Returns:
            Improved article content
        """
        platform_str = f" for {platform}" if platform else ""
        
        prompt = f"""
        Review and improve this article{platform_str} to make it more engaging, readable, and coherent.
        
        Focus on:
        1. READABILITY:
           - Simplify complex sentences
           - Break up long paragraphs
           - Add subheadings where appropriate
           - Ensure consistent tone in {style} style
           - Improve transitions between ideas
        
        2. ENGAGEMENT:
           - Enhance the hook in the introduction
           - Add compelling examples or anecdotes where appropriate
           - Make the conclusion more impactful
           - Add rhetorical questions or thought-provoking statements
        
        3. COHERENCE:
           - Ensure logical progression of ideas
           - Strengthen connections between sections
           - Remove redundancies or repetitive points
           - Ensure consistent terminology throughout
        
        Example of good improvements:
        
        ORIGINAL:
        ```
        AI tools can help with content creation. They use algorithms to generate text. Many businesses are using them now.
        ```
        
        IMPROVED:
        ```
        AI-powered writing assistants have revolutionized content creation, offering a helping hand to writers across industries. These sophisticated tools leverage advanced algorithms to analyze patterns in language and generate human-like text that resonates with readers. From small startups to Fortune 500 companies, organizations are increasingly incorporating these AI collaborators into their content workflows—and seeing impressive results.
        ```
        
        Please maintain the article's core structure and message while making it more polished and professional. Return the complete improved article.
        
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