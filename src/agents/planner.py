"""
Planner Agent for the Agentic Writer System.
Responsible for creating article outlines and planning the content structure.
"""

from typing import Dict, Optional, List

from src.agents.base import Agent
from src.utils.llm import generate_text

class PlannerAgent(Agent):
    """
    Agent responsible for planning article structure and creating outlines.
    """
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """
        Create an article outline based on the given topic and description.
        
        Args:
            task: Description of the planning task
            context: Dictionary containing topic, description, and other parameters
            
        Returns:
            Dictionary containing the outline and section prompts
        """
        if not context:
            context = {}
            
        topic = context.get("topic", "AI Agents")
        description = context.get("description", "")
        platform = context.get("platform")
        style = context.get("style", "conversational")
        
        self.log(f"Creating outline for topic: {topic}")
        
        # If we have platform-specific style information, use it
        platform_style = context.get("platform_style", {})
        
        if platform and platform_style:
            return self._create_platform_specific_outline(topic, description, platform, platform_style, style)
        else:
            return self._create_default_outline(topic, description, style)
    
    def _create_default_outline(self, topic: str, description: str, style: str = "conversational") -> Dict:
        """
        Create a default article outline without platform-specific considerations.
        
        Args:
            topic: The main topic of the article
            description: Additional description or context
            style: The writing style to use
            
        Returns:
            Dictionary containing the outline and section prompts
        """
        prompt = f"""
        Create a detailed outline for an article about {topic}.
        
        Additional context: {description}
        
        The article should be written in a {style} style.
        
        Your outline should include:
        1. A catchy title
        2. 5-7 main sections with descriptive headings
        3. 2-3 bullet points under each section describing what to cover
        
        Format the outline as a Markdown document with ## for section headings and - for bullet points.
        """
        
        outline_text = generate_text(prompt)
        
        # Parse the outline to create section prompts
        sections = self._parse_outline(outline_text)
        
        return {
            "outline": outline_text,
            "sections": sections,
            "title": self._extract_title(outline_text),
            "style": style
        }
    
    def _create_platform_specific_outline(self, topic: str, description: str, 
                                         platform: str, platform_style: Dict, 
                                         style: str = "conversational") -> Dict:
        """
        Create a platform-specific article outline.
        
        Args:
            topic: The main topic of the article
            description: Additional description or context
            platform: The target publishing platform
            platform_style: Dictionary containing platform-specific style information
            style: The writing style to use
            
        Returns:
            Dictionary containing the outline and section prompts
        """
        # Extract platform style characteristics
        avg_word_count = platform_style.get("avg_word_count", 1500)
        avg_section_count = platform_style.get("avg_section_count", 5)
        common_formats = platform_style.get("common_formats", ["listicle", "how-to", "explainer"])
        tone = platform_style.get("tone", "informative")
        
        prompt = f"""
        Create a detailed outline for an article about {topic} specifically for publication on {platform}.
        
        Additional context: {description}
        
        The article should:
        - Be written in a {style} style with a {tone} tone
        - Have approximately {avg_section_count} sections
        - Target around {avg_word_count} words total
        - Use a {' or '.join(common_formats)} format that works well on {platform}
        
        Your outline should include:
        1. A catchy, {platform}-optimized title
        2. {avg_section_count} main sections with descriptive headings
        3. 2-3 bullet points under each section describing what to cover
        
        Format the outline as a Markdown document with ## for section headings and - for bullet points.
        """
        
        outline_text = generate_text(prompt)
        
        # Parse the outline to create section prompts
        sections = self._parse_outline(outline_text)
        
        return {
            "outline": outline_text,
            "sections": sections,
            "title": self._extract_title(outline_text),
            "style": style,
            "platform": platform,
            "platform_style": platform_style
        }
    
    def _parse_outline(self, outline_text: str) -> List[Dict]:
        """
        Parse an outline text into structured sections.
        
        Args:
            outline_text: The markdown outline text
            
        Returns:
            List of section dictionaries with headings and bullet points
        """
        sections = []
        current_section = None
        
        for line in outline_text.split("\n"):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for section headings (## or # format)
            if line.startswith("## ") or (line.startswith("# ") and not line.startswith("# ")):
                if current_section:
                    sections.append(current_section)
                
                heading = line.lstrip("#").strip()
                current_section = {
                    "heading": heading,
                    "bullet_points": [],
                    "content": ""
                }
            
            # Check for bullet points
            elif line.startswith("- ") or line.startswith("* "):
                if current_section:
                    bullet_point = line[2:].strip()
                    current_section["bullet_points"].append(bullet_point)
        
        # Add the last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_title(self, outline_text: str) -> str:
        """
        Extract the title from an outline text.
        
        Args:
            outline_text: The markdown outline text
            
        Returns:
            The extracted title or a default title
        """
        lines = outline_text.split("\n")
        
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        
        # If no title found, use the first line or a default
        if lines and lines[0].strip():
            return lines[0].strip()
        else:
            return "Untitled Article" 