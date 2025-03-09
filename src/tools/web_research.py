"""
Web Research Tool for the Agentic Writer System.
Provides functionality for researching topics and analyzing platform-specific writing styles.
"""

import os
import json
import requests
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import random
from datetime import datetime

from src.utils.config import SERPER_API_KEY, USE_REAL_SEARCH

class WebResearchTool:
    """
    Tool for conducting web research and analyzing platform-specific writing styles.
    """
    
    def __init__(self):
        """Initialize the WebResearchTool."""
        self.serper_api_key = SERPER_API_KEY
        self.use_real_search = USE_REAL_SEARCH
        
        # Cache for expensive operations
        self._cache = {
            "platform_style": {},
            "search_results": {},
            "article_content": {},
            "research": {}
        }
    
    def _log(self, message: str):
        """
        Log a message with timestamp.
        
        Args:
            message: The message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [WebResearch] {message}")
    
    def analyze_platform_style(self, platform: str, topic: str = None) -> Dict:
        """
        Analyze the writing style of a specific publishing platform.
        
        Args:
            platform: The publishing platform to analyze
            topic: Optional topic to focus the analysis on
            
        Returns:
            Dictionary containing platform-specific style information
        """
        platform = platform.lower()
        
        # Check cache first
        cache_key = f"{platform}_{topic if topic else 'general'}"
        if cache_key in self._cache["platform_style"]:
            self._log(f"Using cached platform style for {platform}")
            return self._cache["platform_style"][cache_key]
        
        start_time = time.time()
        self._log(f"Analyzing writing style for {platform}")
        
        # Dispatch to platform-specific analysis methods
        if platform == "medium":
            result = self._analyze_medium_style(topic)
        elif platform == "substack":
            result = self._analyze_substack_style(topic)
        elif platform == "dev.to":
            result = self._analyze_devto_style(topic)
        else:
            # Default to medium if platform not specifically supported
            result = self._analyze_medium_style(topic)
        
        # Cache the result
        self._cache["platform_style"][cache_key] = result
        
        elapsed = time.time() - start_time
        self._log(f"Platform style analysis for {platform} completed in {elapsed:.2f} seconds")
        
        return result
    
    def _analyze_medium_style(self, topic: str = None) -> Dict:
        """
        Analyze the writing style of Medium articles.
        
        Args:
            topic: Optional topic to focus the analysis on
            
        Returns:
            Dictionary containing Medium-specific style information
        """
        # For performance reasons, we'll use mock data instead of real analysis
        # In a production system, this would do real analysis
        return {
            "platform": "medium",
            "avg_word_count": 1200,
            "avg_section_count": 5,
            "common_formats": ["listicle", "how-to", "personal story"],
            "tone": "conversational yet informative",
            "common_patterns": [
                "Use of first-person perspective",
                "Personal anecdotes mixed with factual information",
                "Subheadings that pose questions",
                "Short, punchy paragraphs",
                "Use of embedded links to other articles"
            ]
        }
    
    def _analyze_substack_style(self, topic: str = None) -> Dict:
        """
        Analyze the writing style of Substack newsletters.
        
        Args:
            topic: Optional topic to focus the analysis on
            
        Returns:
            Dictionary containing Substack-specific style information
        """
        # Similar implementation to Medium, but for Substack
        # For brevity, returning mock data
        return {
            "platform": "substack",
            "avg_word_count": 1500,
            "avg_section_count": 4,
            "common_formats": ["newsletter", "essay", "analysis"],
            "tone": "personal and authoritative",
            "common_patterns": [
                "Direct address to subscribers",
                "More in-depth analysis than typical blog posts",
                "Personal voice with expert positioning",
                "Clear section breaks with thematic shifts",
                "Call to action for subscribing or sharing"
            ]
        }
    
    def _analyze_devto_style(self, topic: str = None) -> Dict:
        """
        Analyze the writing style of Dev.to articles.
        
        Args:
            topic: Optional topic to focus the analysis on
            
        Returns:
            Dictionary containing Dev.to-specific style information
        """
        # Similar implementation to Medium, but for Dev.to
        # For brevity, returning mock data
        return {
            "platform": "dev.to",
            "avg_word_count": 1000,
            "avg_section_count": 6,
            "common_formats": ["tutorial", "explainer", "list"],
            "tone": "casual and practical",
            "common_patterns": [
                "Code snippets with explanations",
                "Step-by-step instructions",
                "Practical examples and use cases",
                "Informal, developer-to-developer tone",
                "Frequent use of headings and lists"
            ]
        }
    
    def _search_for_articles(self, search_term: str, max_results: int = 5) -> List[str]:
        """
        Search for articles using the Serper API or mock data.
        
        Args:
            search_term: The search term to use
            max_results: Maximum number of results to return
            
        Returns:
            List of article URLs
        """
        # Check cache first
        cache_key = f"{search_term}_{max_results}"
        if cache_key in self._cache["search_results"]:
            self._log(f"Using cached search results for '{search_term}'")
            return self._cache["search_results"][cache_key]
        
        start_time = time.time()
        self._log(f"Searching for articles with term: '{search_term}'")
        
        # For performance reasons, we'll use mock data
        results = self._get_mock_search_results(search_term, max_results)
        
        # Cache the results
        self._cache["search_results"][cache_key] = results
        
        elapsed = time.time() - start_time
        self._log(f"Search completed in {elapsed:.2f} seconds, found {len(results)} results")
        
        return results
    
    def _get_mock_search_results(self, search_term: str, max_results: int) -> List[str]:
        """
        Generate mock search results for testing.
        
        Args:
            search_term: The search term
            max_results: Maximum number of results to return
            
        Returns:
            List of mock article URLs
        """
        # Extract platform from search term if present
        platform = "medium.com"
        if "site:" in search_term:
            site_match = re.search(r"site:([^\s]+)", search_term)
            if site_match:
                platform = site_match.group(1)
        
        # Extract topic from search term
        topic = search_term.replace(f"site:{platform}", "").strip()
        if not topic:
            topic = "technology"
        
        # Generate mock URLs based on platform and topic
        urls = []
        for i in range(max_results):
            slug = topic.lower().replace(" ", "-")
            urls.append(f"https://{platform}/{slug}-article-{i+1}")
        
        return urls
    
    def _extract_article_content(self, url: str) -> str:
        """
        Extract the content from an article URL.
        
        Args:
            url: The URL of the article
            
        Returns:
            Extracted article text or empty string if extraction fails
        """
        # Check cache first
        if url in self._cache["article_content"]:
            self._log(f"Using cached content for {url}")
            return self._cache["article_content"][url]
        
        start_time = time.time()
        self._log(f"Extracting content from {url}")
        
        # Generate mock content for testing
        domain = urlparse(url).netloc
        path = urlparse(url).path
        
        content = f"""
        This is a mock article from {domain} about {path.replace('-', ' ')}.
        
        # Introduction
        
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        
        ## First Section
        
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        
        ## Second Section
        
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        
        ## Conclusion
        
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """
        
        # Cache the content
        self._cache["article_content"][url] = content
        
        elapsed = time.time() - start_time
        self._log(f"Content extraction completed in {elapsed:.2f} seconds")
        
        return content
    
    def _extract_style_patterns(self, article_texts: List[str], platform: str) -> Dict:
        """
        Extract style patterns from a list of article texts.
        
        Args:
            article_texts: List of article texts
            platform: The publishing platform
            
        Returns:
            Dictionary containing style information
        """
        # In a real implementation, this would use NLP techniques to analyze the texts
        # For simplicity, we'll return mock data based on the platform
        
        if platform == "medium":
            return {
                "platform": "medium",
                "avg_word_count": 1200,
                "avg_section_count": 5,
                "common_formats": ["listicle", "how-to", "personal story"],
                "tone": "conversational yet informative",
                "common_patterns": [
                    "Use of first-person perspective",
                    "Personal anecdotes mixed with factual information",
                    "Subheadings that pose questions",
                    "Short, punchy paragraphs",
                    "Use of embedded links to other articles"
                ]
            }
        elif platform == "substack":
            return {
                "platform": "substack",
                "avg_word_count": 1500,
                "avg_section_count": 4,
                "common_formats": ["newsletter", "essay", "analysis"],
                "tone": "personal and authoritative",
                "common_patterns": [
                    "Direct address to subscribers",
                    "More in-depth analysis than typical blog posts",
                    "Personal voice with expert positioning",
                    "Clear section breaks with thematic shifts",
                    "Call to action for subscribing or sharing"
                ]
            }
        elif platform == "dev.to":
            return {
                "platform": "dev.to",
                "avg_word_count": 1000,
                "avg_section_count": 6,
                "common_formats": ["tutorial", "explainer", "list"],
                "tone": "casual and practical",
                "common_patterns": [
                    "Code snippets with explanations",
                    "Step-by-step instructions",
                    "Practical examples and use cases",
                    "Informal, developer-to-developer tone",
                    "Frequent use of headings and lists"
                ]
            }
        else:
            # Default style information
            return {
                "platform": platform,
                "avg_word_count": 1000,
                "avg_section_count": 5,
                "common_formats": ["article", "blog post"],
                "tone": "informative",
                "common_patterns": [
                    "Clear introduction and conclusion",
                    "Use of subheadings to organize content",
                    "Mix of short and medium-length paragraphs",
                    "Occasional use of lists and bullet points",
                    "Formal but accessible language"
                ]
            }
    
    def test_serper_api(self):
        """
        Test the Serper API connection.
        
        Returns:
            Dictionary with test results
        """
        if not self.serper_api_key:
            return {
                "success": False,
                "message": "No Serper API key provided. Set the SERPER_API_KEY environment variable."
            }
        
        try:
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": "test query",
                "num": 1
            }
            
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Successfully connected to Serper API",
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "message": f"Error connecting to Serper API: {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Exception testing Serper API: {e}"
            }
    
    def research_topic(self, topic: str, subtopics: List[str] = None) -> Dict:
        """
        Research a topic and its subtopics.
        
        Args:
            topic: The main topic to research
            subtopics: Optional list of subtopics to research
            
        Returns:
            Dictionary containing research results
        """
        # Check cache first
        cache_key = f"{topic}_{'-'.join(subtopics) if subtopics else 'no_subtopics'}"
        if cache_key in self._cache["research"]:
            self._log(f"Using cached research for '{topic}'")
            return self._cache["research"][cache_key]
        
        start_time = time.time()
        self._log(f"Researching topic: '{topic}' with {len(subtopics) if subtopics else 0} subtopics")
        
        research_results = {
            "topic": topic,
            "summary": "",
            "subtopics": {}
        }
        
        # Generate a summary of the main topic - using mock data for performance
        research_results["summary"] = self._summarize_content([], topic)
        
        # Research subtopics if provided - using mock data for performance
        if subtopics:
            for subtopic in subtopics:
                research_results["subtopics"][subtopic] = self._summarize_content([], subtopic)
        
        # Cache the results
        self._cache["research"][cache_key] = research_results
        
        elapsed = time.time() - start_time
        self._log(f"Research completed in {elapsed:.2f} seconds")
        
        return research_results
    
    def _summarize_content(self, content_list: List[str], topic: str) -> str:
        """
        Summarize a list of content items.
        
        Args:
            content_list: List of content items to summarize
            topic: The topic being summarized
            
        Returns:
            Summarized content
        """
        # Return mock summary for performance
        return f"""
        {topic} is a significant area of interest with various aspects to consider.
        
        Key points about {topic}:
        1. It has evolved significantly over time
        2. There are multiple approaches and perspectives
        3. Recent developments have changed how we understand it
        4. Experts generally agree on its importance but debate specific details
        5. Future trends suggest continued growth and evolution in this area
        """
    
    def analyze_similar_articles(self, topic: str, platform: str = None) -> Dict:
        """
        Analyze similar articles on a topic to identify patterns and approaches.
        
        Args:
            topic: The topic to analyze
            platform: Optional platform to focus on
            
        Returns:
            Dictionary containing analysis results
        """
        # Check cache first
        cache_key = f"{topic}_{platform if platform else 'no_platform'}"
        if cache_key in self._cache.get("similar_articles", {}):
            self._log(f"Using cached similar articles analysis for '{topic}'")
            return self._cache["similar_articles"][cache_key]
        
        start_time = time.time()
        self._log(f"Analyzing similar articles for '{topic}' on {platform if platform else 'all platforms'}")
        
        # Return mock analysis for performance
        result = {
            "topic": topic,
            "platform": platform,
            "common_approaches": [
                "Historical overview followed by current state",
                "Problem-solution structure",
                "Comparison of different perspectives",
                "Case study analysis",
                "Expert interview or opinion synthesis"
            ],
            "common_sections": [
                "Introduction to the topic",
                "Historical background",
                "Current state of the field",
                "Challenges and opportunities",
                "Future trends",
                "Practical applications",
                "Conclusion with key takeaways"
            ],
            "tone_and_style": "Informative with occasional personal insights",
            "article_count": 5
        }
        
        # Ensure the similar_articles cache exists
        if "similar_articles" not in self._cache:
            self._cache["similar_articles"] = {}
            
        # Cache the result
        self._cache["similar_articles"][cache_key] = result
        
        elapsed = time.time() - start_time
        self._log(f"Similar articles analysis completed in {elapsed:.2f} seconds")
        
        return result
    
    def find_trending_topics(self, main_topic: str) -> List[Dict]:
        """
        Find trending subtopics related to a main topic.
        
        Args:
            main_topic: The main topic to find trends for
            
        Returns:
            List of trending subtopics with relevance scores
        """
        # Check cache first
        if main_topic in self._cache.get("trending_topics", {}):
            self._log(f"Using cached trending topics for '{main_topic}'")
            return self._cache["trending_topics"][main_topic]
        
        start_time = time.time()
        self._log(f"Finding trending topics related to '{main_topic}'")
        
        # Generate some plausible trending subtopics based on the main topic
        base_trends = [
            {"subtopic": "future of", "relevance": 0.9},
            {"subtopic": "impact on society", "relevance": 0.8},
            {"subtopic": "ethical considerations", "relevance": 0.7},
            {"subtopic": "best practices", "relevance": 0.85},
            {"subtopic": "case studies", "relevance": 0.75}
        ]
        
        # Customize the trends based on the main topic
        trending_topics = []
        for trend in base_trends:
            full_subtopic = f"{trend['subtopic']} {main_topic}"
            trending_topics.append({
                "subtopic": full_subtopic,
                "relevance": trend["relevance"],
                "estimated_interest": f"{int(trend['relevance'] * 100)}%",
                "suggested_angle": f"Explore how {full_subtopic} is changing the landscape"
            })
        
        # Sort by relevance
        trending_topics.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Ensure the trending_topics cache exists
        if "trending_topics" not in self._cache:
            self._cache["trending_topics"] = {}
            
        # Cache the result
        self._cache["trending_topics"][main_topic] = trending_topics
        
        elapsed = time.time() - start_time
        self._log(f"Found {len(trending_topics)} trending topics in {elapsed:.2f} seconds")
        
        return trending_topics 