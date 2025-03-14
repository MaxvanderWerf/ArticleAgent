"""
Writer Agent for the Agentic Writer System.
Responsible for generating article content based on outlines.
"""

from typing import Dict, Optional, List

from src.agents.base import Agent
from src.utils.llm import generate_text

class WriterAgent(Agent):
    """
    Agent responsible for writing article content based on outlines.
    """
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate content for an article based on the outline.
        
        Args:
            task: Description of the writing task
            context: Dictionary containing outline, section, and style information
            
        Returns:
            Dictionary containing the generated content
        """
        if not context:
            context = {}
            
        outline = context.get("outline", "")
        sections = context.get("sections", [])
        title = context.get("title", "Untitled Article")
        style = context.get("style", "conversational")
        platform = context.get("platform")
        research = context.get("research", {})
        
        self.log("Generating article content")
        
        # Generate the entire article in one call
        article_content = self._generate_full_article(
            title,
            outline,
            sections,
            style,
            platform,
            research
        )
        
        return {
            "article_content": article_content,
            "title": title
        }
    
    def _generate_full_article(self, title: str, outline: str, sections: List[Dict], 
                              style: str, platform: str = None, research: Dict = None) -> str:
        """
        Generate the full article content in a single LLM call.
        
        Args:
            title: The article title
            outline: The article outline
            sections: List of section dictionaries with headings and bullet points
            style: The writing style to use
            platform: Optional publishing platform
            research: Optional research information
            
        Returns:
            Complete article text
        """
        platform_str = f" for {platform}" if platform else ""
        research_summary = research.get("summary", "") if research else ""
        
        # Format sections for the prompt
        sections_str = ""
        for i, section in enumerate(sections):
            heading = section["heading"]
            bullet_points = "\n".join([f"- {point}" for point in section["bullet_points"]])
            sections_str += f"\n## Section {i+1}: {heading}\nKey points to cover:\n{bullet_points}\n"
        
        # Create a comprehensive prompt with examples
        prompt = f"""
        Write a complete, well-structured article titled "{title}"{platform_str}.
        
        Style: {style}
        
        Here's the outline of the article:
        {outline}
        
        Here are the sections with key points to cover:
        {sections_str}
        
        Research summary to incorporate:
        {research_summary}
        
        Guidelines:
        1. Write a compelling introduction that hooks the reader
        2. Develop each section fully based on the key points provided
        3. Include a thoughtful conclusion that summarizes the main points
        4. Use a {style} writing style throughout
        5. Format the article in Markdown with proper headings (# for title, ## for sections)
        6. Make the content engaging, informative, and well-structured
        7. Use concrete examples and avoid generic statements
        8. Ensure smooth transitions between sections
        
        Example of good article structure:
        ```
        # How AI is Transforming Content Creation
        
        In today's digital landscape, artificial intelligence is revolutionizing how we create and consume content. From automated blog posts to personalized recommendations, AI tools are becoming indispensable for content creators.
        
        ## Understanding AI Content Tools
        
        AI content tools leverage natural language processing to generate human-like text. These systems analyze patterns in existing content to produce new material that matches specific styles and tones.
        
        The most advanced tools can:
        - Adapt to different writing styles and brand voices
        - Generate content across multiple formats and topics
        - Learn from feedback to improve output quality
        
        ## Practical Applications in Marketing
        
        Marketing teams are increasingly adopting AI tools to scale their content production...
        
        ## Conclusion
        
        As AI technology continues to evolve, the relationship between human creators and AI tools will become increasingly collaborative. The future of content creation lies not in choosing between human or AI-generated content, but in finding the optimal balance between the two.
        ```
        
        Please write the complete article now, maintaining a cohesive flow throughout.
        """
        
        return generate_text(prompt)
    
    def _generate_section_content(self, heading: str, bullet_points: List[str], 
                                 style: str, platform: str = None, 
                                 research: Dict = None) -> str:
        """
        Generate content for a specific section.
        
        Args:
            heading: The section heading
            bullet_points: List of bullet points describing the section content
            style: The writing style to use
            platform: Optional publishing platform
            research: Optional research information relevant to this section
            
        Returns:
            Generated section content
        """
        platform_str = f" for {platform}" if platform else ""
        research_str = ""
        
        if research and research.get("content"):
            research_str = f"\n\nUse the following research information where relevant:\n{research.get('content')}"
        
        bullet_points_str = "\n".join([f"- {point}" for point in bullet_points])
        
        prompt = f"""
        Write a detailed section for an article{platform_str} with the heading "{heading}".
        
        The section should cover these key points:
        {bullet_points_str}
        
        Write in a {style} style.{research_str}
        
        Make the content engaging, informative, and well-structured with smooth transitions between ideas.
        Use concrete examples and avoid generic statements where possible.
        """
        
        return generate_text(prompt)
    
    def _generate_introduction(self, sections: List[Dict], style: str, 
                              platform: str = None, research: Dict = None) -> str:
        """
        Generate an introduction for the article.
        
        Args:
            sections: List of section dictionaries
            style: The writing style to use
            platform: Optional publishing platform
            research: Optional research information
            
        Returns:
            Generated introduction
        """
        # Extract key topics from sections
        topics = [section["heading"] for section in sections]
        topics_str = ", ".join(topics)
        
        platform_str = f" for {platform}" if platform else ""
        research_str = ""
        
        if research and research.get("summary"):
            research_str = f"\n\nUse the following research information where relevant:\n{research.get('summary')}"
        
        prompt = f"""
        Write an engaging introduction for an article{platform_str} that will cover the following topics:
        {topics_str}
        
        The introduction should:
        - Hook the reader with an interesting opening
        - Provide context for why this topic matters
        - Briefly outline what the article will cover
        - Set the tone for the rest of the piece
        
        Write in a {style} style.{research_str}
        
        The introduction should be 2-3 paragraphs long.
        """
        
        return generate_text(prompt)
    
    def _generate_conclusion(self, sections: List[Dict], style: str, platform: str = None) -> str:
        """
        Generate a conclusion for the article.
        
        Args:
            sections: List of section dictionaries
            style: The writing style to use
            platform: Optional publishing platform
            
        Returns:
            Generated conclusion
        """
        # Extract key points from sections
        key_points = []
        for section in sections:
            key_points.extend(section["bullet_points"][:1])  # Just take the first bullet point from each section
        
        key_points_str = "\n".join([f"- {point}" for point in key_points])
        platform_str = f" for {platform}" if platform else ""
        
        prompt = f"""
        Write a thoughtful conclusion for an article{platform_str} that has covered these key points:
        {key_points_str}
        
        The conclusion should:
        - Summarize the main takeaways
        - Provide a sense of closure
        - Leave the reader with something to think about or act on
        - Not introduce new major points
        
        Write in a {style} style.
        
        The conclusion should be 2-3 paragraphs long.
        """
        
        return generate_text(prompt)
    
    def _assemble_article(self, title: str, introduction: str, 
                         sections: List[Dict], conclusion: str) -> str:
        """
        Assemble the full article from its components.
        
        Args:
            title: The article title
            introduction: The introduction text
            sections: List of section dictionaries with headings and content
            conclusion: The conclusion text
            
        Returns:
            Complete article text
        """
        article_parts = [f"# {title}\n"]
        
        # Add introduction if it exists
        if introduction:
            article_parts.append(introduction + "\n")
        
        # Add each section
        for section in sections:
            article_parts.append(f"## {section['heading']}\n")
            article_parts.append(section['content'] + "\n")
        
        # Add conclusion if it exists
        if conclusion:
            article_parts.append("## Conclusion\n")
            article_parts.append(conclusion)
        
        return "\n".join(article_parts)
    
    def _get_relevant_research(self, heading: str, research: Dict) -> Dict:
        """
        Extract research information relevant to a specific section.
        
        Args:
            heading: The section heading
            research: Dictionary containing research information
            
        Returns:
            Dictionary with research relevant to this section
        """
        if not research:
            return {}
            
        # If we have section-specific research, use it
        subtopics = research.get("subtopics", {})
        for subtopic, content in subtopics.items():
            if subtopic.lower() in heading.lower() or heading.lower() in subtopic.lower():
                return {"content": content}
        
        # Otherwise return the general summary
        return {"content": research.get("summary", "")} 