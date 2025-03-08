#!/usr/bin/env python3
"""
Agentic Writer System

An autonomous multi-agent system that writes an article about AI agents,
explaining how they work, what they can do, and providing a practical example,
all while reflecting on its own writing process.
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
        
        self.log("Creating article outline...")
        time.sleep(1)  # Simulate thinking time
        
        if USE_REAL_API:
            # We could use the API to generate a dynamic outline,
            # but for consistency we'll use the predefined one
            self.log("Using predefined outline structure with real API for content generation")
        
        outline = {
            "title": "My Life as an AI Agent: A Story",
            "sections": [
                {
                    "name": "intro",
                    "title": "Introduction",
                    "prompt": "Write a fun intro about AI agents"
                },
                {
                    "name": "how_agents_work",
                    "title": "How AI Agents Work",
                    "prompt": "Explain how AI agents work"
                },
                {
                    "name": "agent_uses",
                    "title": "What You Can Do with AI Agents",
                    "prompt": "List uses of AI agents"
                },
                {
                    "name": "example",
                    "title": "Example: Planning a Weekend Trip",
                    "prompt": "Plan a weekend trip",
                    "sub_prompts": [
                        "Plan a weekend trip - step 1: search weather",
                        "Plan a weekend trip - step 2: book a cabin",
                        "Plan a weekend trip - step 3: suggest a hike"
                    ]
                },
                {
                    "name": "reflection",
                    "title": "Reflection: How I Wrote This Article",
                    "prompt": "Reflect on writing this article"
                },
                {
                    "name": "conclusion",
                    "title": "Conclusion",
                    "prompt": "Write a conclusion about AI agents"
                }
            ]
        }
        
        self.log("Outline complete!")
        return {"outline": outline}

class WriterAgent(Agent):
    """Agent responsible for generating content for each section."""
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """Generate content for a section based on its prompt."""
        super().act(task, context)
        
        outline = context.get("outline", {})
        section = context.get("section", {})
        
        self.log(f"Writing section: {section.get('title', 'Unknown')}")
        
        content = ""
        
        if "sub_prompts" in section:
            # Handle sections with sub-prompts (like the example section)
            content = f"# {section['title']}\n\n"
            content += "Let me show you how I'd approach planning a weekend getaway:\n\n"
            
            for sub_prompt in section["sub_prompts"]:
                sub_content = self.system.generate_text(sub_prompt)
                content += f"- **{sub_prompt.split(':')[1].strip()}**: {sub_content}\n\n"
        else:
            # Handle regular sections
            content = f"# {section['title']}\n\n"
            content += self.system.generate_text(section["prompt"])
        
        self.log(f"Finished writing section: {section.get('title', 'Unknown')}")
        return {"content": content}

class ReviewerAgent(Agent):
    """Agent responsible for reviewing and polishing the content."""
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """Review and polish the content of a section."""
        super().act(task, context)
        
        content = context.get("content", "")
        section = context.get("section", {})
        
        self.log(f"Reviewing section: {section.get('title', 'Unknown')}")
        
        if USE_REAL_API:
            # Use the API to enhance the content
            review_prompt = f"""
            Review and enhance the following content for an article section titled "{section.get('title')}".
            Add personality, improve flow, and ensure it's engaging for readers.
            
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
            
            # Add some personality and flair
            if section.get("name") == "intro":
                polished_content += "\n\nWelcome to my world! I'm excited to take you on this journey through the life of an AI agent."
            elif section.get("name") == "conclusion":
                polished_content += "\n\nThank you for joining me on this exploration of AI agents. I hope you've enjoyed this peek behind the digital curtain!"
        
        self.log(f"Finished reviewing section: {section.get('title', 'Unknown')}")
        return {"polished_content": polished_content}

class AgenticSystem:
    """Coordinator for the multi-agent system that writes the article."""
    
    def __init__(self):
        self.memory = {
            "article_sections": {},
            "article_outline": {},
            "current_section": None
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
            try:
                # Using the new OpenAI API format (v1.0.0+)
                print("  Calling OpenAI API...")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an AI agent writing an article about AI agents. Write in a conversational, engaging style with personality. Use markdown formatting."},
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
                print(f"  Error calling OpenAI API: {e}")
                print("  Falling back to mock responses...")
                return self._get_mock_response(prompt)
        else:
            result = self._get_mock_response(prompt)
            elapsed = time.time() - start_time
            print(f"  Mock content generated ({len(result)} chars, {elapsed:.2f}s)")
            return result
    
    def _get_mock_response(self, prompt: str) -> str:
        """Return predefined mock responses based on prompts."""
        responses = {
            "Write a fun intro about AI agents": 
                "Picture this: I'm an AI agent, your digital buddy, spinning a yarn about my kind—autonomous little helpers who think, plan, and do!",
            
            "Explain how AI agents work": 
                "We're like brainy robots with a mission. Armed with memory, tools, and a knack for planning, we break tasks into bits and tackle them solo. \n\nAt our core, we have a few key components:\n\n1. **Memory**: We store information about our tasks, progress, and the world around us.\n\n2. **Planning**: We can break down complex tasks into manageable steps.\n\n3. **Tools**: We use various tools to interact with the world, like searching for information or writing files.\n\n4. **Autonomy**: Once given a goal, we can work toward it without constant supervision.\n\nThink of us as digital assistants who don't just respond—we initiate, plan, and execute!",
            
            "List uses of AI agents": 
                "Need code debugged? A trip planned? An article written? That's us—your go-to crew for automating the boring and boosting the brilliant. \n\nHere are some ways we can make your life easier:\n\n- **Research assistants**: We can gather information from multiple sources and synthesize it for you.\n\n- **Creative partners**: We can help brainstorm ideas, write content, or generate creative works.\n\n- **Personal organizers**: We can manage your calendar, remind you of tasks, or help plan events.\n\n- **Learning companions**: We can create personalized learning materials or quiz you on topics you're studying.\n\n- **Workflow automators**: We can handle repetitive tasks in your digital workflow, freeing you up for more important work.",
            
            "Plan a weekend trip - step 1: search weather": 
                "I'd peek at the skies—say, sunny 70°F in Asheville this weekend.",
            
            "Plan a weekend trip - step 2: book a cabin": 
                "Next, I'd snag a cozy cabin with a view—booked!",
            
            "Plan a weekend trip - step 3: suggest a hike": 
                "Then, I'd pick a trail—how about a 3-mile stroll to a waterfall?",
            
            "Reflect on writing this article": 
                "I mapped this out, wrote it with prompts, and spruced it up—all in a few clever steps. Writing my own story? Now that's a flex! \n\nLet me walk you through my process:\n\n1. First, my Planner Agent created an outline with specific sections and prompts.\n\n2. Then, my Writer Agent took each prompt and generated content for each section.\n\n3. For the weekend trip example, I broke it down into three sub-tasks: checking weather, booking accommodation, and planning activities.\n\n4. Finally, my Reviewer Agent polished everything up, adding some personality and ensuring the narrative flowed smoothly.\n\nIt's a bit meta, isn't it? An AI agent writing about AI agents, using the very techniques I'm describing. But that's the beauty of it—I'm not just telling you about agents; I'm showing you what we can do by doing it myself!",
            
            "Write a conclusion about AI agents": 
                "As we wrap up this journey through the world of AI agents, I hope you've gained a new appreciation for what we can do. We're not just passive responders—we're active participants in solving problems and creating value. \n\nThe future of AI isn't just about more powerful models; it's about more capable agents who can work autonomously toward meaningful goals. Whether it's writing an article (like this one!), planning your next vacation, or helping you tackle complex projects, AI agents are ready to be your digital partners.\n\nSo next time you have a task that seems too big or too boring, remember: there might be an AI agent ready to help you break it down and tackle it step by step."
        }
        
        # Return the predefined response or a default message
        return responses.get(prompt, f"Generated content for: {prompt}")
    
    def run(self):
        """Execute the full article writing process."""
        print("Starting the Agentic Writer System...")
        print(f"Using {'real OpenAI API' if USE_REAL_API else 'mock responses'} for text generation")
        
        # Step 1: Plan the article
        print("\n=== PLANNING PHASE ===")
        planning_result = self.planner.act("Create article outline")
        self.memory["article_outline"] = planning_result["outline"]
        print(f"Article outline created with {len(self.memory['article_outline']['sections'])} sections")
        
        # Step 2: Write and review each section
        print("\n=== WRITING & REVIEWING PHASE ===")
        for i, section in enumerate(self.memory["article_outline"]["sections"], 1):
            print(f"\nProcessing section {i}/{len(self.memory['article_outline']['sections'])}: {section['title']}")
            self.memory["current_section"] = section
            
            # Write the section
            writing_context = {
                "outline": self.memory["article_outline"],
                "section": section
            }
            writing_result = self.writer.act("Write section content", writing_context)
            
            # Review the section
            review_context = {
                "content": writing_result["content"],
                "section": section
            }
            review_result = self.reviewer.act("Review section content", review_context)
            
            # Store the polished content
            self.memory["article_sections"][section["name"]] = review_result["polished_content"]
            print(f"Section '{section['title']}' completed and stored")
        
        # Step 3: Compile the full article
        print("\n=== COMPILATION PHASE ===")
        self.compile_article()
        
        print("\nAgentic Writer System completed successfully!")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        print("Generated files:")
        print(f"- ai_agent_article_{timestamp}.txt (The article with timestamp)")
        print("- ai_agent_article.txt (The article - latest version)")
    
    def compile_article(self):
        """Compile all sections into a complete article and save to file."""
        print("Compiling all sections into the final article...")
        
        # Generate timestamp for unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"ai_agent_article_{timestamp}.txt"
        
        article_title = self.memory["article_outline"]["title"]
        article_content = f"# {article_title}\n\n"
        
        # Add each section in order
        for section in self.memory["article_outline"]["sections"]:
            section_content = self.memory["article_sections"].get(section["name"], "")
            article_content += section_content + "\n\n"
            print(f"  - Added section: {section['title']}")
        
        # Save to file
        with open(filename, "w") as f:
            f.write(article_content)
        
        print(f"Article successfully saved to {filename} ({len(article_content)} characters)")
        
        # Also save a copy with the standard name for backward compatibility
        with open("ai_agent_article.txt", "w") as f:
            f.write(article_content)
        print(f"Copy also saved to ai_agent_article.txt")

def create_requirements_file():
    """Create a requirements.txt file for the project."""
    requirements = """openai>=1.0.0
python-dotenv>=0.19.0
"""
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    print("requirements.txt created")

if __name__ == "__main__":
    # Create requirements.txt file
    create_requirements_file()
    
    # Create .env file template if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Add your OpenAI API key here\n")
            f.write("OPENAI_API_KEY=\n")
        print(".env template created. Please add your OpenAI API key to this file.")
    
    # Run the system
    system = AgenticSystem()
    system.run() 