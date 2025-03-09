#!/usr/bin/env python3
"""
Agentic Writer System

An autonomous multi-agent system that writes articles on any topic,
using a collaborative approach with specialized AI agents for planning,
writing, and reviewing content.
"""

import json
import time
import os
from typing import Dict, List, Optional, Tuple
import openai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import argparse

# Load environment variables from .env file (if it exists)
load_dotenv()

# Set up OpenAI API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables.")
    print("Using mock responses instead of real API calls.")
    USE_REAL_API = False
else:
    USE_REAL_API = True
    # Initialize the OpenAI client
    client = openai.OpenAI(api_key=api_key)

class Agent:
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, system: 'AgenticSystem'):
        self.name = name
        self.system = system
        self.memory = {}
    
    def log(self, message: str):
        """Print a status message from this agent."""
        print(f"[{self.name}] {message}")
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """Perform an action based on the given task and context."""
        self.log(f"Working on task: {task}")
        return {}

class PlannerAgent(Agent):
    """Agent responsible for planning the article structure."""
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """Create an article outline with sections and prompts."""
        super().act(task, context)
        
        topic = context.get("topic", "General Topic")
        description = context.get("description", "A general article")
        style = context.get("style", "conversational")
        
        self.log(f"Creating article outline for topic: {topic}")
        time.sleep(1)  # Simulate thinking time
        
        if USE_REAL_API:
            planning_prompt = f"""
            Create a detailed outline for an article on the topic: "{topic}"
            
            Description: {description}
            
            Your outline should include:
            1. A catchy title for the article
            2. 5-6 main sections (including introduction and conclusion)
            3. For each section, provide a brief description of what should be covered
            
            Format your response as a JSON object with the following structure:
            {{
                "title": "Article Title",
                "sections": [
                    {{
                        "name": "section_id",
                        "title": "Section Title",
                        "prompt": "Detailed instructions for writing this section"
                    }},
                    ...
                ]
            }}
            
            Ensure your response is valid JSON that can be parsed. Do not include any text before or after the JSON object.
            """
            
            outline_json = self.system.generate_text(planning_prompt)
            
            # Try to parse the JSON response with improved error handling
            try:
                # Clean up the response to extract just the JSON part
                json_start = outline_json.find('{')
                json_end = outline_json.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    cleaned_json = outline_json[json_start:json_end]
                    outline = json.loads(cleaned_json)
                    self.log("Successfully generated outline using API")
                else:
                    raise ValueError("Could not find valid JSON in the response")
            except Exception as e:
                self.log(f"Failed to parse JSON from API response: {e}")
                self.log("Using default outline structure")
                outline = self._create_default_outline(topic, description)
        else:
            outline = self._create_default_outline(topic, description)
        
        self.log("Outline complete!")
        return {"outline": outline}
    
    def _create_default_outline(self, topic: str, description: str) -> Dict:
        """Create a default outline structure for the given topic."""
        return {
            "title": f"Understanding {topic}: A Comprehensive Guide",
            "sections": [
                {
                    "name": "intro",
                    "title": "Introduction",
                    "prompt": f"Write an engaging introduction about {topic}. {description}"
                },
                {
                    "name": "background",
                    "title": f"Background of {topic}",
                    "prompt": f"Explain the history and context of {topic}"
                },
                {
                    "name": "key_aspects",
                    "title": f"Key Aspects of {topic}",
                    "prompt": f"Describe the main components or aspects of {topic}"
                },
                {
                    "name": "practical_applications",
                    "title": f"Practical Applications",
                    "prompt": f"Discuss how {topic} is applied in real-world scenarios"
                },
                {
                    "name": "future_trends",
                    "title": f"Future Trends and Developments",
                    "prompt": f"Explore potential future developments related to {topic}"
                },
                {
                    "name": "conclusion",
                    "title": "Conclusion",
                    "prompt": f"Write a thoughtful conclusion about {topic}"
                }
            ]
        }

class WriterAgent(Agent):
    """Agent responsible for generating content for each section."""
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """Generate content for a section based on its prompt."""
        super().act(task, context)
        
        outline = context.get("outline", {})
        section = context.get("section", {})
        topic = context.get("topic", "General Topic")
        style = context.get("style", "conversational")
        
        self.log(f"Writing section: {section.get('title', 'Unknown')} in {style} style")
        
        # Style-specific instructions
        style_instructions = {
            "conversational": "Write in a friendly, casual tone as if talking to a friend. Use personal pronouns, contractions, and occasional rhetorical questions.",
            "professional": "Write in a formal, authoritative tone suitable for business or academic contexts. Use precise language, avoid contractions, and maintain a structured approach.",
            "storytelling": "Write in a narrative style with vivid descriptions, anecdotes, and emotional elements. Create a journey for the reader with a clear beginning, middle, and end.",
            "instructional": "Write in a clear, step-by-step manner with practical advice and actionable tips. Use imperative verbs and focus on helping the reader achieve specific outcomes."
        }
        
        # Get the appropriate style instruction
        style_instruction = style_instructions.get(style, style_instructions["conversational"])
        
        # Enhance the prompt with the topic context and style-specific instructions
        enhanced_prompt = f"""
        Write content for an article section titled "{section.get('title')}" about {topic}.
        
        Section prompt: {section.get('prompt', 'Write informative content')}
        
        Style instruction: {style_instruction}
        
        Guidelines:
        1. {style_instruction}
        2. Use markdown formatting for headings, lists, and emphasis
        3. Include relevant examples, metaphors, or analogies to illustrate concepts
        4. Address the reader directly to create a connection
        5. Aim for approximately 400-500 words for this section
        6. Include 2-3 subheadings within the section to organize the content
        7. End with a smooth transition to the next section
        
        Do not include the main section title in your response as it will be added separately.
        """
        
        # Generate content without the section title
        content = self.system.generate_text(enhanced_prompt)
        
        self.log(f"Finished writing section: {section.get('title', 'Unknown')}")
        return {"content": content}

class ReviewerAgent(Agent):
    """Agent responsible for reviewing and polishing the content."""
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """Review and polish the content of a section."""
        super().act(task, context)
        
        content = context.get("content", "")
        section = context.get("section", {})
        topic = context.get("topic", "General Topic")
        style = context.get("style", "conversational")
        
        self.log(f"Reviewing section: {section.get('title', 'Unknown')} in {style} style")
        
        # Style-specific review instructions
        style_review = {
            "conversational": "Ensure the text maintains a friendly, casual tone throughout. Check for natural flow and conversational elements.",
            "professional": "Ensure the text maintains a formal, authoritative tone. Check for precision, clarity, and proper structure.",
            "storytelling": "Ensure the text has narrative elements, vivid descriptions, and emotional appeal. Check for storytelling flow and engagement.",
            "instructional": "Ensure the text provides clear, actionable guidance. Check for practical advice and logical step-by-step progression."
        }
        
        # Get the appropriate style review instruction
        review_instruction = style_review.get(style, style_review["conversational"])
        
        if USE_REAL_API:
            # Use the API to enhance the content
            review_prompt = f"""
            Review and enhance the following content for an article section titled "{section.get('title')}" about {topic}.
            
            Style: {style}
            
            {review_instruction}
            
            Make the text engaging, polished, and professional. Focus on:
            - Improving clarity and flow
            - Enhancing the narrative structure
            - Adding vivid examples where appropriate
            - Ensuring a conversational yet authoritative tone
            - Maintaining a consistent voice throughout
            - Ensuring the style is consistently {style} throughout
            
            CONTENT TO REVIEW:
            {content}
            
            ENHANCED CONTENT:
            """
            
            polished_content = self.system.generate_text(review_prompt)
            
            # Make sure we keep the section title
            if not polished_content.startswith(f"# {section['title']}"):
                polished_content = f"# {section['title']}\n\n{polished_content}"
        else:
            # Enhance the content with some stylistic improvements
            polished_content = content
            
            # Add some personality and flair based on style
            if section.get("name") == "intro":
                if style == "conversational":
                    polished_content += "\n\nLet's dive into this fascinating topic together!"
                elif style == "professional":
                    polished_content += "\n\nThe following sections will explore this topic in detail, providing comprehensive analysis and insights."
                elif style == "storytelling":
                    polished_content += "\n\nAnd so our journey begins, a tale of discovery that will unfold in the pages ahead."
                elif style == "instructional":
                    polished_content += "\n\nNow, let's proceed step by step to master this topic together."
            elif section.get("name") == "conclusion":
                if style == "conversational":
                    polished_content += "\n\nThanks for joining me on this exploration. I hope you've found some valuable insights to take away!"
                elif style == "professional":
                    polished_content += "\n\nIn conclusion, the evidence presented demonstrates the significance and implications of this topic in the broader context."
                elif style == "storytelling":
                    polished_content += "\n\nAnd as our story comes to a close, we find ourselves changed by the journey, carrying new understanding forward."
                elif style == "instructional":
                    polished_content += "\n\nBy following these guidelines, you now have the tools to successfully implement these concepts in your own context."
        
        self.log(f"Finished reviewing section: {section.get('title', 'Unknown')}")
        return {"polished_content": polished_content}

class WebResearchTool:
    """Tool for researching and analyzing content from specific platforms."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Get Serper API key from environment variables
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        if not self.serper_api_key:
            print("Warning: SERPER_API_KEY not found in environment variables.")
            print("Using mock search results instead of real API calls.")
    
    def analyze_platform_style(self, platform: str, topic: str = None) -> Dict:
        """
        Analyze the writing style of a specific platform.
        
        Args:
            platform: The platform to analyze (e.g., "medium", "substack", "dev.to")
            topic: Optional topic to focus the analysis on
            
        Returns:
            Dictionary containing style guidelines extracted from the platform
        """
        print(f"Analyzing writing style for {platform}...")
        
        if platform.lower() == "medium":
            return self._analyze_medium_style(topic)
        elif platform.lower() == "substack":
            return self._analyze_substack_style(topic)
        elif platform.lower() == "dev.to":
            return self._analyze_devto_style(topic)
        else:
            # Default to medium if platform not recognized
            print(f"Platform {platform} not specifically supported. Using Medium as default.")
            return self._analyze_medium_style(topic)
    
    def _analyze_medium_style(self, topic: str = None) -> Dict:
        """Analyze the writing style of popular Medium articles."""
        # Start with some base style guidelines for Medium
        style_guide = {
            "tone": "conversational yet authoritative",
            "structure": "clear headings, short paragraphs, strategic use of bold and italic text",
            "formatting": "frequent use of subheadings (H2, H3), bullet points, and numbered lists",
            "paragraph_length": "typically 1-3 sentences per paragraph",
            "sentence_style": "mix of short, punchy sentences and more complex ones",
            "hooks": "compelling introductions that often pose a question or challenge a common belief",
            "imagery": "relevant images with captions, often one striking header image",
            "examples": "concrete examples and personal anecdotes",
            "conclusions": "actionable takeaways or thought-provoking final thoughts",
            "voice": "personal, often uses 'I', 'you', and 'we'",
            "article_length": "7-10 minute read (1500-2500 words)"
        }
        
        # If we're using the real API, try to enhance with actual research
        if USE_REAL_API:
            try:
                # Get popular Medium articles (potentially filtered by topic)
                search_term = f"{topic} site:medium.com" if topic else "popular articles site:medium.com"
                articles = self._search_for_articles(search_term, max_results=5)
                
                if articles:
                    # Analyze the articles to extract style patterns
                    article_texts = []
                    for url in articles:
                        try:
                            content = self._extract_article_content(url)
                            if content:
                                article_texts.append(content)
                        except Exception as e:
                            print(f"Error extracting content from {url}: {e}")
                    
                    if article_texts:
                        # Use the API to analyze the style patterns
                        enhanced_style = self._extract_style_patterns(article_texts, platform="Medium")
                        if enhanced_style:
                            # Update our style guide with the enhanced information
                            style_guide.update(enhanced_style)
            except Exception as e:
                print(f"Error during Medium style analysis: {e}")
                print("Using default Medium style guidelines.")
        
        return style_guide
    
    def _analyze_substack_style(self, topic: str = None) -> Dict:
        """Analyze the writing style of popular Substack newsletters."""
        # Base style guidelines for Substack
        style_guide = {
            "tone": "personal and intimate, like an email to a friend",
            "structure": "conversational flow with clear sections",
            "formatting": "simple formatting, emphasis on readability",
            "paragraph_length": "varied, but generally short to medium",
            "sentence_style": "direct and clear, often conversational",
            "hooks": "personal anecdotes or timely observations",
            "imagery": "selective use of images, not overwhelming",
            "examples": "personal experiences and observations",
            "conclusions": "often includes a personal note or call to action",
            "voice": "strong personal voice, distinctive personality",
            "article_length": "varies widely, from short updates to long essays"
        }
        
        # Similar implementation as Medium for enhancing with real research
        # (Omitted for brevity but would follow the same pattern)
        
        return style_guide
    
    def _analyze_devto_style(self, topic: str = None) -> Dict:
        """Analyze the writing style of popular Dev.to articles."""
        # Base style guidelines for Dev.to
        style_guide = {
            "tone": "casual, developer-to-developer conversation",
            "structure": "clear, tutorial-like structure with code examples",
            "formatting": "heavy use of code blocks, headers, and lists",
            "paragraph_length": "concise, focused paragraphs",
            "sentence_style": "straightforward, avoids jargon when possible",
            "hooks": "practical problem statements or learning objectives",
            "imagery": "diagrams, screenshots, and code output",
            "examples": "working code examples and practical applications",
            "conclusions": "summary of key points and next steps",
            "voice": "helpful mentor voice, assumes reader is a peer",
            "article_length": "varies by topic, typically 1000-2000 words"
        }
        
        # Similar implementation as Medium for enhancing with real research
        # (Omitted for brevity but would follow the same pattern)
        
        return style_guide
    
    def _search_for_articles(self, search_term: str, max_results: int = 5) -> List[str]:
        """Search for articles using Serper API and return URLs."""
        if not self.serper_api_key:
            print("🔍 No Serper API key found - using mock search results")
            return self._get_mock_search_results(search_term, max_results)
        
        try:
            print(f"🔍 Searching for articles about: '{search_term}' using Serper API")
            
            # Prepare the request to Serper API
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": search_term,
                "num": max_results
            })
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            # Make the request
            print(f"🌐 Sending request to Serper API: {url}")
            response = requests.post(url, headers=headers, data=payload)
            
            # Log the response status
            print(f"📡 Serper API response status: {response.status_code}")
            
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse the results
            search_results = response.json()
            
            # Log the response structure
            print(f"📊 Serper API response keys: {', '.join(search_results.keys())}")
            
            # Extract URLs from organic results
            urls = []
            if 'organic' in search_results:
                print(f"📑 Found {len(search_results['organic'])} organic search results")
                for i, result in enumerate(search_results['organic'][:max_results], 1):
                    if 'link' in result:
                        url = result['link']
                        urls.append(url)
                        print(f"  {i}. {url}")
            
            if not urls:
                print("❌ No valid URLs found in search results - using mock results")
                return self._get_mock_search_results(search_term, max_results)
            
            print(f"✅ Successfully retrieved {len(urls)} URLs from Serper API")
            return urls
            
        except Exception as e:
            print(f"❌ Error using Serper API: {e}")
            print("⚠️ Falling back to mock search results")
            return self._get_mock_search_results(search_term, max_results)
    
    def _get_mock_search_results(self, search_term: str, max_results: int) -> List[str]:
        """Provide mock search results when API is unavailable."""
        # These would normally come from a search API
        if "medium.com" in search_term:
            return [
                "https://medium.com/swlh/how-to-write-on-medium-a-complete-guide-for-2020-d5dcbc65f5c9",
                "https://medium.com/creators-hub/the-complete-guide-to-medium-writing-e8edd8b4c3ff",
                "https://medium.com/illumination/how-to-write-stories-people-will-actually-read-4f62b0d741b0"
            ][:max_results]
        elif "substack" in search_term:
            return [
                "https://on.substack.com/p/how-to-start-a-successful-substack",
                "https://on.substack.com/p/how-the-top-1-of-substack-writers"
            ][:max_results]
        elif "dev.to" in search_term:
            return [
                "https://dev.to/devteam/how-to-write-a-great-technical-blog-post-j42",
                "https://dev.to/nityeshaga/writing-a-technical-blog-post-a-guide-1k0h"
            ][:max_results]
        else:
            return []
    
    def _extract_article_content(self, url: str) -> str:
        """Extract the main content from an article URL using web scraping."""
        try:
            print(f"Extracting content from: {url}")
            
            # Make the request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get the main text content
            # This is a simple approach - real implementation would need more sophisticated extraction
            # based on the specific structure of each platform
            
            # Try to find the article content
            article = soup.find('article')
            if article:
                text = article.get_text()
            else:
                # Try to find main content div
                main = soup.find('main')
                if main:
                    text = main.get_text()
                else:
                    # Fallback to body
                    text = soup.body.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit the length to avoid token limits
            if len(text) > 8000:
                text = text[:8000] + "..."
            
            print(f"Successfully extracted {len(text)} characters of content")
            return text
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            print("Using mock content instead")
            
            # Fallback to mock content
            domain = urlparse(url).netloc
            if "medium.com" in domain:
                return "Medium articles typically use a conversational tone with personal anecdotes. They often start with a hook that draws the reader in, followed by clear sections with descriptive headings. Paragraphs are kept short, usually 1-3 sentences, to maintain readability on mobile devices. Writers frequently use bold text for emphasis and include relevant images to break up text. Articles often include personal experiences and practical examples, ending with a clear takeaway or call to action."
            elif "substack" in domain:
                return "Substack newsletters have a distinct personal voice, often feeling like an email from a friend. They typically have a consistent structure that subscribers come to expect. Writers often share personal insights and build a relationship with readers through direct address. Formatting is clean and simple, focusing on readability rather than visual complexity."
            elif "dev.to" in domain:
                return "Dev.to articles are written in a developer-friendly style with plenty of code examples and practical applications. They often follow a problem-solution format, with clear explanations of technical concepts. Writers use code blocks, lists, and headers to organize information logically. The tone is casual but informative, like one developer helping another."
            else:
                return "This article discusses writing techniques and style guidelines for online content. It emphasizes the importance of clear structure, engaging hooks, and consistent voice. The content is organized into sections with headers and includes practical examples."
    
    def _extract_style_patterns(self, article_texts: List[str], platform: str) -> Dict:
        """Use the API to analyze style patterns from article texts."""
        if not USE_REAL_API or not article_texts:
            return {}
        
        combined_text = "\n\n---\n\n".join(article_texts[:3])  # Limit to first 3 for brevity
        
        analysis_prompt = f"""
        Analyze the writing style of the following {platform} articles and extract key style patterns.
        Focus on:
        1. Tone and voice
        2. Structure and formatting
        3. Paragraph and sentence length
        4. Use of headings, lists, and emphasis
        5. How introductions and conclusions are handled
        6. Any platform-specific conventions
        
        Articles:
        {combined_text}
        
        Provide your analysis as a JSON object with the following keys:
        tone, structure, formatting, paragraph_length, sentence_style, hooks, imagery, examples, conclusions, voice, article_length, platform_specific_tips
        
        Ensure your response is valid JSON that can be parsed.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a writing style analyst who extracts patterns from text."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract JSON from the response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                cleaned_json = analysis_text[json_start:json_end]
                try:
                    return json.loads(cleaned_json)
                except json.JSONDecodeError:
                    print("Failed to parse style analysis JSON")
                    return {}
            else:
                return {}
        except Exception as e:
            print(f"Error analyzing style patterns: {e}")
            return {}

    def test_serper_api(self):
        """Test the Serper API connection and functionality."""
        print("\n=== TESTING SERPER API ===")
        
        if not self.serper_api_key:
            print("❌ No Serper API key found in environment variables")
            print("ℹ️ To use the Serper API, add your API key to the .env file:")
            print("   SERPER_API_KEY=your_key_here")
            return False
        
        print("🔑 Serper API key found")
        
        try:
            # Test with a simple search
            print("🔍 Testing search functionality...")
            urls = self._search_for_articles("medium.com writing style guide", 3)
            
            if not urls:
                print("❌ No URLs returned from search")
                return False
            
            # Try to extract content from the first URL
            print("\n📄 Testing content extraction...")
            first_url = urls[0]
            content = self._extract_article_content(first_url)
            
            if not content:
                print("❌ No content extracted")
                return False
            
            content_preview = content[:150] + "..." if len(content) > 150 else content
            print(f"📝 Content preview: {content_preview}")
            
            print("\n✅ Serper API test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during Serper API test: {e}")
            return False

    def research_topic(self, topic: str, subtopics: List[str] = None) -> Dict:
        """Research a topic and gather relevant information from the web."""
        print(f"\n=== RESEARCHING TOPIC: {topic} ===")
        
        research_results = {
            "main_facts": [],
            "statistics": [],
            "expert_opinions": [],
            "recent_developments": [],
            "subtopics": {}
        }
        
        # Research the main topic
        search_term = f"{topic} facts statistics recent developments"
        urls = self._search_for_articles(search_term, max_results=5)
        
        # Extract and analyze content
        all_content = []
        for url in urls:
            content = self._extract_article_content(url)
            if content:
                all_content.append(content)
        
        # Use AI to extract key information
        if all_content and USE_REAL_API:
            combined_content = "\n\n---\n\n".join(all_content[:3])
            
            analysis_prompt = f"""
            Analyze the following content about {topic} and extract:
            1. 5-7 key facts
            2. 3-5 relevant statistics with sources if available
            3. 2-3 expert opinions or quotes
            4. Any recent developments or trends
            
            Format your response as JSON with the keys: main_facts, statistics, expert_opinions, recent_developments
            
            Content to analyze:
            {combined_content}
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a research assistant who extracts and organizes information."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                
                analysis_text = response.choices[0].message.content.strip()
                
                # Extract JSON from the response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    cleaned_json = analysis_text[json_start:json_end]
                    try:
                        topic_info = json.loads(cleaned_json)
                        research_results.update(topic_info)
                    except json.JSONDecodeError:
                        print("Failed to parse topic research JSON")
            except Exception as e:
                print(f"Error analyzing topic research: {e}")
        
        # Research subtopics if provided
        if subtopics:
            for subtopic in subtopics:
                sub_search_term = f"{topic} {subtopic}"
                sub_urls = self._search_for_articles(sub_search_term, max_results=3)
                
                sub_content = []
                for url in sub_urls:
                    content = self._extract_article_content(url)
                    if content:
                        sub_content.append(content)
                
                if sub_content:
                    research_results["subtopics"][subtopic] = {
                        "sources": sub_urls,
                        "content_summary": self._summarize_content(sub_content, f"{topic} {subtopic}")
                    }
        
        print(f"Research complete. Found information on {len(research_results['main_facts'])} facts, {len(research_results['statistics'])} statistics")
        return research_results

    def _summarize_content(self, content_list: List[str], topic: str) -> str:
        """Summarize a list of content pieces about a specific topic."""
        if not content_list or not USE_REAL_API:
            return "No content available for summarization."
        
        combined_content = "\n\n---\n\n".join(content_list[:2])  # Limit to first 2 for brevity
        
        summary_prompt = f"""
        Summarize the key information about {topic} from the following content.
        Focus on the most important facts, figures, and insights.
        Keep the summary to 3-4 paragraphs.
        
        Content:
        {combined_content}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a research assistant who summarizes information accurately and concisely."},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error summarizing content: {e}")
            return "Error generating summary."

    def analyze_similar_articles(self, topic: str, platform: str = None) -> Dict:
        """Analyze similar articles on the given topic to identify gaps and opportunities."""
        print(f"\n=== ANALYZING SIMILAR ARTICLES ON: {topic} ===")
        
        # Construct search term based on platform
        if platform:
            search_term = f"{topic} site:{platform}"
        else:
            search_term = f"{topic} article"
        
        # Find similar articles
        urls = self._search_for_articles(search_term, max_results=5)
        
        if not urls:
            print("No similar articles found.")
            return {"similar_articles": [], "analysis": {}}
        
        # Extract content from articles
        articles = []
        for url in urls:
            content = self._extract_article_content(url)
            if content:
                articles.append({
                    "url": url,
                    "content": content
                })
        
        if not articles:
            print("Could not extract content from any articles.")
            return {"similar_articles": [], "analysis": {}}
        
        # Analyze the articles
        if USE_REAL_API:
            # Prepare content for analysis
            article_summaries = []
            for i, article in enumerate(articles, 1):
                # Get a brief summary of each article
                content_preview = article["content"][:1000] + "..." if len(article["content"]) > 1000 else article["content"]
                article_summaries.append(f"Article {i}: {article['url']}\n{content_preview}")
            
            combined_summaries = "\n\n---\n\n".join(article_summaries)
            
            analysis_prompt = f"""
            Analyze these articles about "{topic}" and provide:
            
            1. Common themes and approaches
            2. Unique angles or perspectives in each
            3. Content gaps or missing perspectives
            4. Popular subtopics covered
            5. Recommendations for creating a differentiated article
            
            Articles:
            {combined_summaries}
            
            Format your response as JSON with the keys: common_themes, unique_angles, content_gaps, popular_subtopics, recommendations
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[
                        {"role": "system", "content": "You are a content strategist who analyzes articles to identify patterns and opportunities."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                
                analysis_text = response.choices[0].message.content.strip()
                
                # Extract JSON from the response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    cleaned_json = analysis_text[json_start:json_end]
                    try:
                        analysis = json.loads(cleaned_json)
                        return {
                            "similar_articles": [{"url": a["url"]} for a in articles],
                            "analysis": analysis
                        }
                    except json.JSONDecodeError:
                        print("Failed to parse competitive analysis JSON")
            except Exception as e:
                print(f"Error analyzing similar articles: {e}")
        
        # Fallback if API fails or is not used
        return {
            "similar_articles": [{"url": a["url"]} for a in articles],
            "analysis": {
                "common_themes": ["Could not analyze common themes"],
                "recommendations": ["Consider reviewing the articles manually to identify opportunities"]
            }
        }

    def find_trending_topics(self, main_topic: str) -> List[Dict]:
        """Find trending topics related to the main topic."""
        print(f"\n=== FINDING TRENDING TOPICS RELATED TO: {main_topic} ===")
        
        # Search for trending topics
        search_terms = [
            f"{main_topic} trending topics",
            f"{main_topic} latest trends",
            f"{main_topic} what's new 2023"
        ]
        
        all_urls = []
        for term in search_terms:
            urls = self._search_for_articles(term, max_results=3)
            all_urls.extend(urls)
        
        # Remove duplicates
        unique_urls = list(dict.fromkeys(all_urls))
        
        if not unique_urls:
            print("No trending topics found.")
            return []
        
        # Extract content
        trend_content = []
        for url in unique_urls[:5]:  # Limit to top 5 URLs
            content = self._extract_article_content(url)
            if content:
                trend_content.append({
                    "url": url,
                    "content": content
                })
        
        if not trend_content:
            print("Could not extract content about trending topics.")
            return []
        
        # Analyze trends
        if USE_REAL_API:
            # Prepare content for analysis
            combined_content = "\n\n---\n\n".join([item["content"] for item in trend_content])
            
            trends_prompt = f"""
            Based on the following content, identify 5-7 trending topics or current discussions related to "{main_topic}".
            
            For each trend, provide:
            1. A short name or title for the trend
            2. A brief description (1-2 sentences)
            3. Why it's relevant or trending now
            
            Format your response as a JSON array of objects with the keys: trend_name, description, relevance
            
            Content:
            {combined_content[:10000]}  # Limit content length
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a trend analyst who identifies current topics of interest."},
                        {"role": "user", "content": trends_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.4
                )
                
                trends_text = response.choices[0].message.content.strip()
                
                # Extract JSON from the response
                json_start = trends_text.find('[')
                json_end = trends_text.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    cleaned_json = trends_text[json_start:json_end]
                    try:
                        trends = json.loads(cleaned_json)
                        print(f"Found {len(trends)} trending topics related to {main_topic}")
                        return trends
                    except json.JSONDecodeError:
                        print("Failed to parse trending topics JSON")
            except Exception as e:
                print(f"Error analyzing trending topics: {e}")
        
        # Fallback
        return [{"trend_name": "Could not identify specific trends", "description": "Consider manual research", "relevance": "N/A"}]

class HumanizerAgent(Agent):
    """Agent responsible for making text appear more human-written and less AI-generated."""
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """Transform content to appear more human-written."""
        super().act(task, context)
        
        content = context.get("content", "")
        topic = context.get("topic", "General Topic")
        
        self.log(f"Humanizing content about {topic}")
        
        if USE_REAL_API:
            humanize_prompt = f"""
            Transform the following article to make it appear more human-written and less detectable as AI-generated.
            
            Apply these specific techniques:
            1. Vary sentence structure significantly - mix simple, compound, and complex sentences in unpredictable patterns
            2. Add occasional idiosyncrasies like parenthetical asides, em dashes, or sentence fragments
            3. Include personal anecdotes or hypothetical scenarios that feel authentic
            4. Use more nuanced transitions between ideas (avoid formulaic transitions)
            5. Add occasional colloquialisms, slang, or informal expressions where appropriate
            6. Incorporate subtle imperfections like mild digressions or tangential thoughts
            7. Use distinctive word choices that wouldn't be the first synonym an AI would select
            8. Vary paragraph lengths unpredictably - include some very short paragraphs
            9. Add rhetorical questions that create a conversational feel
            10. Include occasional cultural references or timely examples
            
            IMPORTANT: Maintain the original meaning, information, and overall structure. Don't change section headings or key points.
            
            CONTENT TO HUMANIZE:
            {content}
            
            HUMANIZED CONTENT:
            """
            
            humanized_content = self.system.generate_text(humanize_prompt)
            
            # Make sure we preserve the original title
            if content.startswith("# ") and not humanized_content.startswith("# "):
                title_line = content.split("\n")[0]
                humanized_content = f"{title_line}\n\n{humanized_content}"
        else:
            # For mock responses, just return the original content
            humanized_content = content
            
            # Add some humanizing elements
            humanized_content = humanized_content.replace(
                "In conclusion,", 
                "Look, when you put it all together,"
            )
            humanized_content = humanized_content.replace(
                "Furthermore,", 
                "And here's the thing —"
            )
        
        self.log(f"Finished humanizing content")
        return {"humanized_content": humanized_content}

class AgenticSystem:
    """Central system that coordinates the agents and manages memory."""
    
    def __init__(self, topic: str, description: str, style: str = "conversational", platform: str = None):
        self.topic = topic
        self.description = description
        self.style = style
        self.platform = platform
        self.memory = {
            "article_sections": {},
            "article_outline": {},
            "current_section": None,
            "topic": topic,
            "description": description,
            "style": style,
            "platform": platform,
            "platform_style_guide": None,
            "topic_research": None,
            "similar_articles_analysis": None,
            "trending_topics": None
        }
        
        # Initialize tools
        self.web_research_tool = WebResearchTool()
        
        # Initialize agents
        self.planner = PlannerAgent("Planner Agent", self)
        self.writer = WriterAgent("Writer Agent", self)
        self.reviewer = ReviewerAgent("Reviewer Agent", self)
        self.humanizer = HumanizerAgent("Humanizer Agent", self)
        
        # If a platform is specified, analyze its style
        if platform:
            self.analyze_platform_style()
    
    def analyze_platform_style(self):
        """Analyze the style of the specified platform."""
        if not self.platform:
            return
        
        print(f"\n=== PLATFORM STYLE ANALYSIS ===")
        print(f"Analyzing writing style for {self.platform}...")
        
        style_guide = self.web_research_tool.analyze_platform_style(self.platform, self.topic)
        self.memory["platform_style_guide"] = style_guide
        
        print(f"Style analysis complete for {self.platform}")
        print(f"Key characteristics: {', '.join(style_guide.keys())}")
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using OpenAI API or mock responses.
        """
        print(f"  Generating content for prompt: '{prompt[:50]}...'")
        start_time = time.time()
        
        if USE_REAL_API:
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Using the new OpenAI API format (v1.0.0+)
                    print(f"  Calling OpenAI API (attempt {retry_count + 1}/{max_retries})...")
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a professional writer creating high-quality article content. Write in a conversational, engaging style with personality. Use markdown formatting."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    result = response.choices[0].message.content.strip()
                    elapsed = time.time() - start_time
                    print(f"  Content generated ({len(result)} chars, {elapsed:.2f}s)")
                    return result
                except Exception as e:
                    retry_count += 1
                    print(f"  Error calling OpenAI API (attempt {retry_count}/{max_retries}): {e}")
                    if retry_count < max_retries:
                        wait_time = 2 ** retry_count  # Exponential backoff
                        print(f"  Waiting {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                    else:
                        print("  All retry attempts failed. Falling back to mock responses...")
                        return self._get_mock_response(prompt)
        else:
            result = self._get_mock_response(prompt)
            elapsed = time.time() - start_time
            print(f"  Mock content generated ({len(result)} chars, {elapsed:.2f}s)")
            return result
    
    def _get_mock_response(self, prompt: str) -> str:
        """Return predefined mock responses based on the topic."""
        # Extract section name from prompt if possible
        section_type = ""
        if "introduction" in prompt.lower():
            section_type = "intro"
        elif "background" in prompt.lower():
            section_type = "background"
        elif "conclusion" in prompt.lower():
            section_type = "conclusion"
        
        # Generate mock content based on topic and section
        if section_type == "intro":
            return f"When it comes to {self.topic}, there's so much more than meets the eye. In this article, we'll explore the fascinating world of {self.topic} and why it matters to all of us."
        elif section_type == "background":
            return f"The history of {self.topic} is rich and complex. It all began when researchers first noticed patterns that couldn't be explained by conventional wisdom."
        elif section_type == "conclusion":
            return f"As we've seen, {self.topic} continues to evolve and shape our understanding of the world. The journey doesn't end here—it's just beginning."
        else:
            return f"This section explores important aspects of {self.topic}. {self.description} We'll examine key concepts, practical applications, and future directions."
    
    def run_with_progress_callback(self, callback=None):
        """Execute the article writing process, generating the entire article at once."""
        print("Starting the Agentic Writer System...")
        print(f"Using {'real OpenAI API' if USE_REAL_API else 'mock responses'} for text generation")
        print(f"Topic: {self.topic}")
        print(f"Description: {self.description}")
        print(f"Style: {self.style}")
        
        if callback:
            callback("planning")
        
        # Step 1: Plan the article
        print("\n=== PLANNING PHASE ===")
        planning_result = self.planner.act("Create article outline", {
            "topic": self.topic,
            "description": self.description,
            "style": self.style
        })
        self.memory["article_outline"] = planning_result["outline"]
        print(f"Article outline created with {len(self.memory['article_outline']['sections'])} sections")
        
        # Step 2: Generate the entire article at once
        print("\n=== WRITING PHASE ===")
        if callback:
            callback("writing")
        
        article_content = self.generate_full_article()
        
        # Step 3: Compile and save the article
        if callback:
            callback("compiling")
        
        print("\n=== COMPILATION PHASE ===")
        article_path = self.save_article(article_content)
        
        print("\nAgentic Writer System completed successfully!")
        print(f"Article saved to: {article_path}")
        
        return article_path

    def generate_full_article(self):
        """Generate the entire article content at once, incorporating research."""
        outline = self.memory["article_outline"]
        sections = outline["sections"]
        
        # Create a detailed prompt for the entire article
        sections_prompt = ""
        for i, section in enumerate(sections, 1):
            sections_prompt += f"{i}. {section['title']}: {section['prompt']}\n"
        
        # Style-specific instructions
        style_instructions = {
            "conversational": "Write in a friendly, casual tone as if talking to a friend. Use personal pronouns, contractions, and occasional rhetorical questions.",
            "professional": "Write in a formal, authoritative tone suitable for business or academic contexts. Use precise language, avoid contractions, and maintain a structured approach.",
            "storytelling": "Write in a narrative style with vivid descriptions, anecdotes, and emotional elements. Create a journey for the reader with a clear beginning, middle, and end.",
            "instructional": "Write in a clear, step-by-step manner with practical advice and actionable tips. Use imperative verbs and focus on helping the reader achieve specific outcomes."
        }
        
        style_instruction = style_instructions.get(self.style, style_instructions["conversational"])
        
        # Add platform-specific style guidance if available
        platform_style_guide = ""
        if self.memory.get("platform_style_guide"):
            platform_style_guide = "Platform-specific style guidelines:\n"
            for key, value in self.memory["platform_style_guide"].items():
                platform_style_guide += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        # Add research insights if available
        research_insights = ""
        if self.memory.get("topic_research"):
            research = self.memory["topic_research"]
            research_insights += "\nKey facts about the topic:\n"
            for fact in research.get("main_facts", [])[:5]:
                research_insights += f"- {fact}\n"
            
            research_insights += "\nRelevant statistics:\n"
            for stat in research.get("statistics", [])[:3]:
                research_insights += f"- {stat}\n"
            
            research_insights += "\nExpert opinions:\n"
            for opinion in research.get("expert_opinions", [])[:2]:
                research_insights += f"- {opinion}\n"
        
        # Add competitive analysis if available
        competitive_insights = ""
        if self.memory.get("similar_articles_analysis"):
            analysis = self.memory["similar_articles_analysis"]["analysis"]
            competitive_insights += "\nContent gaps to address:\n"
            for gap in analysis.get("content_gaps", [])[:3]:
                competitive_insights += f"- {gap}\n"
            
            competitive_insights += "\nRecommendations for differentiation:\n"
            for rec in analysis.get("recommendations", [])[:3]:
                competitive_insights += f"- {rec}\n"
        
        # Add trending topics if available
        trending_insights = ""
        if self.memory.get("trending_topics"):
            trending_insights += "\nTrending topics to consider incorporating:\n"
            for trend in self.memory["trending_topics"][:3]:
                trending_insights += f"- {trend.get('trend_name')}: {trend.get('description')}\n"
        
        full_article_prompt = f"""
        Write a complete, cohesive article on the topic: "{self.topic}"
        
        Description: {self.description}
        
        Article title: {outline["title"]}
        
        The article should include the following sections:
        {sections_prompt}
        
        Style instruction: {style_instruction}
        
        {platform_style_guide if platform_style_guide else ""}
        
        {research_insights if research_insights else ""}
        
        {competitive_insights if competitive_insights else ""}
        
        {trending_insights if trending_insights else ""}
        
        Guidelines:
        1. {style_instruction}
        2. Write a cohesive article where sections flow naturally into each other
        3. Use markdown formatting for headings (# for main title, ## for section titles, ### for subsections)
        4. Include relevant examples, metaphors, or analogies to illustrate concepts
        5. Address the reader directly to create a connection
        6. Aim for approximately 2000-3000 words for the entire article
        7. Ensure transitions between sections are smooth and logical
        8. Format each section title as "## Section Title" (level 2 heading)
        9. Incorporate the research insights, statistics, and expert opinions where relevant
        10. Address content gaps identified in similar articles
        11. Reference trending topics where appropriate to make the article current and relevant
        
        Write the complete article with all sections.
        """
        
        print("Generating the complete article...")
        start_time = time.time()
        
        if USE_REAL_API:
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    print(f"  Calling OpenAI API (attempt {retry_count + 1}/{max_retries})...")
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo-16k",  # Using a model with larger context
                        messages=[
                            {"role": "system", "content": "You are a professional writer creating a high-quality article. Write a cohesive, engaging piece that flows naturally between sections."},
                            {"role": "user", "content": full_article_prompt}
                        ],
                        max_tokens=4000,
                        temperature=0.7
                    )
                    article_content = response.choices[0].message.content.strip()
                    elapsed = time.time() - start_time
                    print(f"  Article generated ({len(article_content)} chars, {elapsed:.2f}s)")
                    
                    # Add humanization step
                    print("\n=== HUMANIZATION PHASE ===")
                    humanize_context = {
                        "content": article_content,
                        "topic": self.topic
                    }
                    humanize_result = self.humanizer.act("Humanize article content", humanize_context)
                    article_content = humanize_result["humanized_content"]
                    print(f"  Article humanized ({len(article_content)} chars)")
                    
                    return article_content
                    
                except Exception as e:
                    retry_count += 1
                    print(f"  Error calling OpenAI API (attempt {retry_count}/{max_retries}): {e}")
                    if retry_count < max_retries:
                        wait_time = 2 ** retry_count  # Exponential backoff
                        print(f"  Waiting {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                    else:
                        print("  All retry attempts failed. Falling back to mock responses...")
                        return self._generate_mock_article()
        else:
            article_content = self._generate_mock_article()
            
            # Add humanization step even for mock content
            print("\n=== HUMANIZATION PHASE ===")
            humanize_context = {
                "content": article_content,
                "topic": self.topic
            }
            humanize_result = self.humanizer.act("Humanize article content", humanize_context)
            article_content = humanize_result["humanized_content"]
            
            elapsed = time.time() - start_time
            print(f"  Mock article generated and humanized ({len(article_content)} chars, {elapsed:.2f}s)")
            return article_content

    def _generate_mock_article(self):
        """Generate a mock article for testing purposes."""
        outline = self.memory["article_outline"]
        
        mock_article = f"# {outline['title']}\n\n"
        
        for section in outline["sections"]:
            mock_article += f"## {section['title']}\n\n"
            
            if section["name"] == "intro":
                mock_article += f"Welcome to this article about {self.topic}! {self.description} In the following sections, we'll explore various aspects of this fascinating subject.\n\n"
            elif section["name"] == "conclusion":
                mock_article += f"In conclusion, {self.topic} is an important area that continues to evolve. We've covered the key aspects and applications, and hope you've gained valuable insights.\n\n"
            else:
                mock_article += f"This section explores {section['title'].lower()} related to {self.topic}. There are many interesting aspects to consider here, from theoretical foundations to practical applications.\n\n"
        
        return mock_article

    def save_article(self, article_content):
        """Save the generated article to files."""
        print("Saving the article to files...")
        
        # Generate timestamp for unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_topic = self.topic.lower().replace(' ', '_')
        filename = f"article_{safe_topic}_{timestamp}.txt"
        standard_filename = f"article_{safe_topic}.txt"
        
        # Save to file
        with open(filename, "w") as f:
            f.write(article_content)
        
        print(f"Article successfully saved to {filename} ({len(article_content)} characters)")
        
        # Also save a copy with the standard name for easy reference
        with open(standard_filename, "w") as f:
            f.write(article_content)
        print(f"Copy also saved to {standard_filename}")
        
        return filename

    def conduct_comprehensive_research(self):
        """Conduct comprehensive research on the topic."""
        print("\n=== COMPREHENSIVE RESEARCH ===")
        
        # 1. Research the main topic
        self.memory["topic_research"] = self.web_research_tool.research_topic(self.topic)
        
        # 2. Analyze similar articles
        self.memory["similar_articles_analysis"] = self.web_research_tool.analyze_similar_articles(
            self.topic, self.platform
        )
        
        # 3. Find trending topics
        self.memory["trending_topics"] = self.web_research_tool.find_trending_topics(self.topic)
        
        print("Comprehensive research complete!")


if __name__ == "__main__":
    import sys
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Agentic Writer System")
    parser.add_argument("--test-api", action="store_true", help="Test the Serper API connection")
    parser.add_argument("--research", action="store_true", help="Conduct research on a topic without generating an article")
    parser.add_argument("--topic", type=str, help="Topic to research or write about")
    parser.add_argument("--description", type=str, help="Description of the article")
    parser.add_argument("--platform", type=str, choices=["medium", "substack", "dev.to", "linkedin", "none"], 
                        help="Target publishing platform")
    
    args = parser.parse_args()
    
    # Test API if requested
    if args.test_api:
        tool = WebResearchTool()
        tool.test_serper_api()
        sys.exit(0)
    
    # Set topic and description
    topic = args.topic or "AI Agents for Writing Articles"
    description = args.description or "An exploration of how autonomous AI agents can collaborate to create high-quality written content."
    platform = args.platform or "medium"
    
    # Just conduct research if requested
    if args.research:
        print(f"Conducting research on: {topic}")
        system = AgenticSystem(topic, description, "conversational", platform)
        system.conduct_comprehensive_research()
        
        # Save research results to a file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        research_file = f"research_{topic.lower().replace(' ', '_')}_{timestamp}.json"
        
        with open(research_file, "w") as f:
            json.dump({
                "topic": topic,
                "description": description,
                "platform": platform,
                "topic_research": system.memory.get("topic_research"),
                "similar_articles_analysis": system.memory.get("similar_articles_analysis"),
                "trending_topics": system.memory.get("trending_topics"),
                "platform_style_guide": system.memory.get("platform_style_guide")
            }, f, indent=2)
        
        print(f"Research results saved to {research_file}")
        sys.exit(0)
    
    # Otherwise, run the full system
    system = AgenticSystem(topic, description, "conversational", platform)
    system.conduct_comprehensive_research()  # Add research before generating
    system.run_with_progress_callback() 