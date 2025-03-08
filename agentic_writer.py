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

class AgenticSystem:
    """Coordinator for the multi-agent system that writes the article."""
    
    def __init__(self, topic: str, description: str, style: str = "conversational"):
        self.topic = topic
        self.description = description
        self.style = style
        self.memory = {
            "article_sections": {},
            "article_outline": {},
            "current_section": None,
            "topic": topic,
            "description": description,
            "style": style
        }
        
        # Initialize agents
        self.planner = PlannerAgent("Planner Agent", self)
        self.writer = WriterAgent("Writer Agent", self)
        self.reviewer = ReviewerAgent("Reviewer Agent", self)
    
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
        """Execute the full article writing process with progress updates."""
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
        total_sections = len(self.memory["article_outline"]["sections"])
        print(f"Article outline created with {total_sections} sections")
        
        # Step 2: Write and review each section
        print("\n=== WRITING & REVIEWING PHASE ===")
        for i, section in enumerate(self.memory["article_outline"]["sections"], 1):
            if callback:
                callback("writing", section=section["title"], progress=i, total=total_sections)
            
            progress = f"[{i}/{total_sections}]"
            progress_percent = int((i / total_sections) * 100)
            progress_bar = "=" * (progress_percent // 5) + ">" + " " * (20 - (progress_percent // 5))
            print(f"\n{progress} [{progress_bar}] {progress_percent}% - Processing: {section['title']}")
            
            self.memory["current_section"] = section
            
            # Write the section
            writing_context = {
                "outline": self.memory["article_outline"],
                "section": section,
                "topic": self.topic,
                "description": self.description,
                "style": self.style
            }
            writing_result = self.writer.act("Write section content", writing_context)
            
            # Review the section
            review_context = {
                "content": writing_result["content"],
                "section": section,
                "topic": self.topic,
                "description": self.description,
                "style": self.style
            }
            review_result = self.reviewer.act("Review section content", review_context)
            
            # Store the polished content
            self.memory["article_sections"][section["name"]] = review_result["polished_content"]
            print(f"{progress} Section '{section['title']}' completed and stored")
        
        # Step 3: Compile the full article
        if callback:
            callback("compiling")
        
        print("\n=== COMPILATION PHASE ===")
        article_path = self.compile_article()
        
        print("\nAgentic Writer System completed successfully!")
        print(f"Article saved to: {article_path}")
        
        return article_path
    
    def compile_article(self):
        """Compile all sections into a complete article and save to file."""
        print("Compiling all sections into the final article...")
        
        # Generate timestamp for unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_topic = self.topic.lower().replace(' ', '_')
        filename = f"article_{safe_topic}_{timestamp}.txt"
        standard_filename = f"article_{safe_topic}.txt"
        
        article_title = self.memory["article_outline"]["title"]
        article_content = f"# {article_title}\n\n"
        
        # Add each section in order
        for section in self.memory["article_outline"]["sections"]:
            section_content = self.memory["article_sections"].get(section["name"], "")
            
            # Check if the section content already has the title with markdown formatting
            # If so, we don't need to add it again
            if not section_content.startswith(f"# {section['title']}"):
                article_content += f"# {section['title']}\n\n"
            
            article_content += section_content + "\n\n"
            print(f"  - Added section: {section['title']}")
        
        # Save to file
        with open(filename, "w") as f:
            f.write(article_content)
        
        print(f"Article successfully saved to {filename} ({len(article_content)} characters)")
        
        # Also save a copy with the standard name for easy reference
        with open(standard_filename, "w") as f:
            f.write(article_content)
        print(f"Copy also saved to {standard_filename}")
        
        return filename


if __name__ == "__main__":
    # Define the topic and description for the article
    article_topic = "AI Agents for Writing Articles"
    article_description = "An exploration of how autonomous AI agents can collaborate to create high-quality written content, explaining their capabilities, workflow, and practical applications."
    
    # Run the system
    system = AgenticSystem(article_topic, article_description)
    system.run_with_progress_callback() 