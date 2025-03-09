"""
Configuration module for the Agentic Writer System.
Handles environment variables, API keys, and other settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Feature flags
USE_REAL_API = bool(OPENAI_API_KEY)
USE_REAL_SEARCH = bool(SERPER_API_KEY)

# File paths
ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "articles")
METADATA_DIR = os.path.join(ARTICLES_DIR, "metadata")

# Ensure directories exist
os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# Model settings
DEFAULT_MODEL = "gpt-4"
FALLBACK_MODEL = "gpt-3.5-turbo"

# Writing styles
WRITING_STYLES = {
    "conversational": "Friendly and casual, like talking to a friend",
    "professional": "Formal and authoritative, suitable for business or academic contexts",
    "storytelling": "Narrative-driven with anecdotes and vivid descriptions",
    "instructional": "Clear, step-by-step guidance with practical advice"
}

# Publishing platforms
PUBLISHING_PLATFORMS = {
    "medium": "Medium.com - Popular blogging platform with a wide audience",
    "substack": "Substack - Newsletter platform with a subscription model",
    "dev.to": "Dev.to - Community for developers with technical content",
    "linkedin": "LinkedIn Articles - Professional content for your network",
    "none": "No specific platform - General purpose article"
} 