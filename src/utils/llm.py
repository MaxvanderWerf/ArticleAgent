"""
LLM utility module for the Agentic Writer System.
Handles interactions with OpenAI API and provides mock responses when needed.
"""

import json
import time
import openai
import hashlib
from typing import Dict, List, Optional
import random
import re
from datetime import datetime

from src.utils.config import OPENAI_API_KEY, USE_REAL_API, DEFAULT_MODEL

# Initialize the OpenAI client if API key is available
client = None
if USE_REAL_API:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Simple in-memory cache for LLM responses
_response_cache = {}

def _log(message: str):
    """
    Log a message with timestamp.
    
    Args:
        message: The message to log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [LLM] {message}")

def generate_text(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.7) -> str:
    """
    Generate text using OpenAI API or mock responses.
    
    Args:
        prompt: The prompt to send to the model
        model: The model to use (default: gpt-4)
        temperature: Controls randomness (0-1)
        
    Returns:
        Generated text response
    """
    # Create a cache key based on the prompt and parameters
    cache_key = hashlib.md5(f"{prompt}|{model}|{temperature}".encode()).hexdigest()
    
    # Check if we have a cached response
    if cache_key in _response_cache:
        _log(f"Using cached response for prompt: {prompt[:50]}...")
        return _response_cache[cache_key]
    
    start_time = time.time()
    _log(f"Generating text with model {model}, prompt: {prompt[:50]}...")
    
    if USE_REAL_API and client:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )
            result = response.choices[0].message.content.strip()
        except Exception as e:
            _log(f"Error calling OpenAI API: {e}")
            _log("Falling back to mock response...")
            result = _get_mock_response(prompt)
    else:
        result = _get_mock_response(prompt)
    
    # Cache the response
    _response_cache[cache_key] = result
    
    elapsed = time.time() - start_time
    _log(f"Text generation completed in {elapsed:.2f} seconds, {len(result)} chars")
    
    return result

def _get_mock_response(prompt: str) -> str:
    """
    Generate a mock response for testing without API access.
    
    Args:
        prompt: The prompt that would be sent to the API
        
    Returns:
        A mock text response
    """
    # Add a small delay to simulate API call
    time.sleep(0.5)
    
    # Simple mock responses based on prompt keywords
    if "outline" in prompt.lower():
        return """
# AI Agents: The Future of Automation

## Introduction
- What are AI agents and why they matter
- The evolution of AI from tools to agents

## How AI Agents Work
- The architecture of an AI agent
- Decision-making capabilities
- Learning and adaptation

## Real-World Applications
- Business process automation
- Personal assistants
- Creative collaborators

## Challenges and Limitations
- Current technological constraints
- Ethical considerations
- The human-agent relationship

## The Future of AI Agents
- Emerging trends and research
- Predictions for the next decade

## Conclusion
- Summary of key points
- Call to action for readers
"""
    elif "research" in prompt.lower():
        return """
AI agents are software entities that can perceive their environment, make decisions, and take actions to achieve specific goals. Unlike traditional AI systems that perform specific tasks, agents operate with some degree of autonomy and can adapt to changing circumstances.

Key characteristics of AI agents include:
1. Autonomy - They can operate without direct human intervention
2. Reactivity - They respond to changes in their environment
3. Proactivity - They can take initiative to achieve goals
4. Social ability - They can interact with other agents or humans

Recent developments in large language models (LLMs) have accelerated the capabilities of AI agents, enabling more sophisticated reasoning, planning, and natural language understanding.
"""
    elif "section" in prompt.lower():
        # Generate a section based on the heading in the prompt
        heading_match = re.search(r'heading "([^"]+)"', prompt)
        heading = heading_match.group(1) if heading_match else "AI Agents"
        
        return f"""
{heading} represents a significant advancement in artificial intelligence technology. Unlike traditional AI systems that are designed for specific tasks, AI agents can operate with greater autonomy and adaptability.

The key difference lies in their ability to perceive their environment, make decisions based on that information, and take actions to achieve specific goals. This creates a more dynamic and responsive system that can handle complex, changing situations.

Modern AI agents typically combine several technologies:
1. Machine learning models for understanding and generating content
2. Decision-making frameworks for choosing actions
3. Memory systems for maintaining context and learning from past experiences
4. Communication interfaces for interacting with humans and other systems

These components work together to create systems that can assist with a wide range of tasks, from simple automation to complex creative and analytical work.
"""
    elif "introduction" in prompt.lower():
        return """
In the rapidly evolving landscape of artificial intelligence, AI agents have emerged as one of the most promising developments. These intelligent systems are transforming how we interact with technology, automating complex tasks, and augmenting human capabilities in unprecedented ways.

AI agents differ from traditional software in their ability to operate autonomously, make decisions, and adapt to changing circumstances. They represent a shift from tools that require explicit instructions to assistants that can understand context, anticipate needs, and take initiative.

This article explores the fascinating world of AI agents - what they are, how they work, their current applications, and the future possibilities they present. Whether you're a technology enthusiast, a business professional looking to leverage AI, or simply curious about the future of automation, understanding AI agents is essential for navigating our increasingly AI-driven world.
"""
    elif "conclusion" in prompt.lower():
        return """
As we've explored throughout this article, AI agents represent a significant evolution in how we interact with and benefit from artificial intelligence. By combining autonomy, adaptability, and specialized capabilities, these systems are transforming everything from personal productivity to enterprise operations.

The journey of AI agents is just beginning. As underlying technologies like large language models, reinforcement learning, and multimodal AI continue to advance, we can expect agents to become more capable, more intuitive, and more integrated into our daily lives and work.

However, this progress must be balanced with thoughtful consideration of the ethical implications, transparency requirements, and human oversight needed to ensure these systems serve humanity's best interests. The most successful implementations will likely be those that augment human capabilities rather than simply replacing them.

For individuals and organizations looking to benefit from this technology, now is the time to start exploring use cases, experimenting with available tools, and developing strategies for integration. The future belongs to those who can effectively collaborate with these digital partners.

AI agents may have begun as a technological innovation, but their ultimate impact will be measured by how they help us solve problems, enhance creativity, and improve the quality of our lives and work.
"""
    elif "improve" in prompt.lower():
        # For review improvements, return the same text with minor modifications
        article_match = re.search(r'ARTICLE:\s*(.*?)(?:\s*IMPROVED ARTICLE:|$)', prompt, re.DOTALL)
        if article_match:
            article = article_match.group(1).strip()
            # Make some simple improvements
            improved = article.replace("very ", "").replace("really ", "")
            improved = improved.replace("in order to", "to")
            improved = improved.replace(".", ".\n\n")
            return improved
        return "Improved version of the article with better readability, engagement, and coherence."
    else:
        # Generic response for other prompts
        return f"This is a mock response for: {prompt[:50]}...\n\nIn a real environment, this would be generated by the OpenAI API with much more relevant and detailed content based on your specific prompt." 