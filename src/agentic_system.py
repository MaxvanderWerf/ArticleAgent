"""
Agentic System for the Agentic Writer.
Coordinates all agents and manages the article generation process.
"""

import time
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime

from src.agents.base import Agent
from src.agents.planner import PlannerAgent
from src.agents.writer import WriterAgent
from src.agents.reviewer import ReviewerAgent
from src.agents.humanizer import HumanizerAgent
from src.tools.web_research import WebResearchTool
from src.utils.file_manager import save_article
from src.utils.llm import generate_text

class AgenticSystem:
    """
    Main system that coordinates all agents and manages the article generation process.
    """
    
    def __init__(self, topic: str, description: str, style: str = "conversational", platform: str = None):
        """
        Initialize the AgenticSystem.
        
        Args:
            topic: The main topic of the article
            description: Additional description or context
            style: The writing style to use
            platform: Optional publishing platform
        """
        self.topic = topic
        self.description = description
        self.style = style
        self.platform = platform
        
        # Initialize agents
        self.planner = PlannerAgent("Planner", self)
        self.writer = WriterAgent("Writer", self)
        self.reviewer = ReviewerAgent("Reviewer", self)
        self.humanizer = HumanizerAgent("Humanizer", self)
        
        # Initialize tools
        self.web_research_tool = WebResearchTool()
        
        # Initialize state
        self.outline = None
        self.research = None
        self.platform_style = None
        self.article_content = None
        self.improved_article = None
        self.final_article = None
        
        # Progress tracking
        self.progress = {
            "phase": "initialization",
            "section": None,
            "progress": 0,
            "total": 100,
            "start_time": time.time(),
            "phase_times": {}
        }
        
        # Log initialization
        self._log(f"Initialized AgenticSystem for topic: {topic}")
    
    def _log(self, message: str):
        """
        Log a message with timestamp.
        
        Args:
            message: The message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [System] {message}")
    
    def analyze_platform_style(self):
        """
        Analyze the writing style of the target platform.
        
        Returns:
            Dictionary containing platform-specific style information
        """
        if not self.platform or self.platform.lower() == "none":
            return None
            
        self._log(f"Analyzing writing style for {self.platform}...")
        start_time = time.time()
        self.platform_style = self.web_research_tool.analyze_platform_style(self.platform, self.topic)
        elapsed = time.time() - start_time
        self._log(f"Platform style analysis completed in {elapsed:.2f} seconds")
        return self.platform_style
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text response
        """
        return generate_text(prompt)
    
    def _update_progress(self, phase: str, section: str = None, progress: int = None, total: int = None):
        """
        Update the progress tracking information.
        
        Args:
            phase: The current phase of the process
            section: Optional section being processed
            progress: Optional progress value
            total: Optional total value
        """
        # If we're starting a new phase, record the time of the previous phase
        if phase != self.progress["phase"]:
            end_time = time.time()
            elapsed = end_time - self.progress.get("phase_start_time", self.progress["start_time"])
            self.progress["phase_times"][self.progress["phase"]] = elapsed
            self._log(f"Phase '{self.progress['phase']}' completed in {elapsed:.2f} seconds")
            self.progress["phase_start_time"] = end_time
            
        self.progress["phase"] = phase
        
        if section is not None:
            self.progress["section"] = section
            
        if progress is not None:
            self.progress["progress"] = progress
            
        if total is not None:
            self.progress["total"] = total
            
        # Log progress update
        progress_msg = f"Progress: {phase}"
        if section:
            progress_msg += f" - {section}"
        if progress is not None and total is not None:
            progress_msg += f" - {progress}/{total}"
        self._log(progress_msg)
            
        # Call the progress callback if set
        if hasattr(self, "progress_callback") and self.progress_callback:
            self.progress_callback(
                phase=self.progress["phase"],
                section=self.progress["section"],
                progress=self.progress["progress"],
                total=self.progress["total"]
            )
    
    def run_with_progress_callback(self, callback=None):
        """
        Run the full article generation process with progress updates.
        
        Args:
            callback: Optional function to call with progress updates
            
        Returns:
            The generated article
        """
        self.progress_callback = callback
        self.progress["start_time"] = time.time()
        self.progress["phase_start_time"] = time.time()
        
        self._log(f"Starting article generation for topic: {self.topic}")
        
        # Phase 1: Platform Analysis
        self._update_progress("platform_analysis", progress=0, total=100)
        if self.platform and self.platform.lower() != "none":
            self.platform_style = self.analyze_platform_style()
        self._update_progress("platform_analysis", progress=100, total=100)
        
        # Phase 2: Research
        self._update_progress("research", progress=0, total=100)
        self.research = self.conduct_comprehensive_research()
        self._update_progress("research", progress=100, total=100)
        
        # Phase 3: Planning
        self._update_progress("planning", progress=0, total=100)
        planning_context = {
            "topic": self.topic,
            "description": self.description,
            "style": self.style,
            "platform": self.platform,
            "platform_style": self.platform_style,
            "research": self.research
        }
        planning_result = self.planner.act("Create an article outline", planning_context)
        self.outline = planning_result
        self._update_progress("planning", progress=100, total=100)
        
        # Phase 4: Writing
        self._update_progress("writing", progress=0, total=100)
        writing_context = {
            "outline": self.outline.get("outline", ""),
            "sections": self.outline.get("sections", []),
            "title": self.outline.get("title", ""),
            "style": self.style,
            "platform": self.platform,
            "research": self.research
        }
        
        # Track progress through sections
        total_sections = len(writing_context["sections"])
        self._update_progress("writing", progress=0, total=total_sections)
        
        writing_result = self.writer.act("Write article content", writing_context)
        self.article_content = writing_result.get("article_content", "")
        self._update_progress("writing", progress=total_sections, total=total_sections)
        
        # Phase 5: Reviewing
        self._update_progress("reviewing", progress=0, total=100)
        reviewing_context = {
            "article_content": self.article_content,
            "style": self.style,
            "platform": self.platform
        }
        reviewing_result = self.reviewer.act("Review and improve article", reviewing_context)
        self.improved_article = reviewing_result.get("improved_article", self.article_content)
        self._update_progress("reviewing", progress=100, total=100)
        
        # Phase 6: Humanizing
        self._update_progress("humanizing", progress=0, total=100)
        humanizing_context = {
            "article_content": self.improved_article,
            "style": self.style,
            "platform": self.platform
        }
        humanizing_result = self.humanizer.act("Add human touch to article", humanizing_context)
        self.final_article = humanizing_result.get("humanized_article", self.improved_article)
        self._update_progress("humanizing", progress=100, total=100)
        
        # Phase 7: Saving
        self._update_progress("saving", progress=0, total=100)
        self.save_article(self.final_article)
        self._update_progress("saving", progress=100, total=100)
        
        # Complete
        self._update_progress("complete", progress=100, total=100)
        
        # Log total time
        total_time = time.time() - self.progress["start_time"]
        self._log(f"Article generation completed in {total_time:.2f} seconds")
        
        # Log time breakdown
        self._log("Time breakdown by phase:")
        for phase, elapsed in self.progress["phase_times"].items():
            self._log(f"  {phase}: {elapsed:.2f} seconds ({elapsed/total_time*100:.1f}%)")
        
        return self.final_article
    
    def generate_full_article(self):
        """
        Generate a full article without progress updates.
        
        Returns:
            The generated article
        """
        return self.run_with_progress_callback(None)
    
    def save_article(self, article_content):
        """
        Save the article and its metadata.
        
        Args:
            article_content: The article content to save
            
        Returns:
            Dictionary with paths to the saved files
        """
        # Prepare metadata
        metadata = {
            "topic": self.topic,
            "description": self.description,
            "style": self.style,
            "platform": self.platform if self.platform else "none",
            "generation_date": datetime.now().isoformat(),
            "word_count": len(article_content.split()),
            "title": self.outline.get("title", "Untitled Article") if self.outline else "Untitled Article",
            "generation_process": {
                "platform_style": self.platform_style,
                "research_summary": self.research.get("summary", "") if self.research else "",
                "outline": self.outline.get("outline", "") if self.outline else "",
                "improvements": self.reviewer.act("Summarize improvements", {"original_article": self.article_content, "improved_article": self.improved_article}) if hasattr(self, "article_content") and hasattr(self, "improved_article") else {}
            },
            "performance": {
                "total_time": time.time() - self.progress["start_time"],
                "phase_times": self.progress["phase_times"]
            }
        }
        
        # Save article and metadata
        return save_article(article_content, metadata)
    
    def conduct_comprehensive_research(self):
        """
        Conduct comprehensive research on the topic.
        
        Returns:
            Dictionary containing research results
        """
        self._log(f"Researching topic: {self.topic}...")
        start_time = time.time()
        
        # Generate subtopics based on the main topic
        subtopics_prompt = f"""
        Generate 3-5 key subtopics that would be important to cover in an article about {self.topic}.
        List each subtopic on a new line with no numbering or bullets.
        """
        
        subtopics_text = generate_text(subtopics_prompt)
        subtopics = [s.strip() for s in subtopics_text.split("\n") if s.strip()]
        
        # Conduct research on the topic and subtopics
        research_results = self.web_research_tool.research_topic(self.topic, subtopics)
        
        # If we have a platform, also analyze similar articles on that platform
        if self.platform and self.platform.lower() != "none":
            similar_articles = self.web_research_tool.analyze_similar_articles(self.topic, self.platform)
            research_results["similar_articles"] = similar_articles
        
        # Find trending topics related to the main topic
        trending_topics = self.web_research_tool.find_trending_topics(self.topic)
        research_results["trending_topics"] = trending_topics
        
        elapsed = time.time() - start_time
        self._log(f"Research completed in {elapsed:.2f} seconds")
        
        return research_results 