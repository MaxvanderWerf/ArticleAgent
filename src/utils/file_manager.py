"""
File management utilities for the Agentic Writer System.
Handles saving articles and metadata.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

from src.utils.config import ARTICLES_DIR, METADATA_DIR

def generate_filename(topic: str, platform: str = None) -> str:
    """
    Generate a standardized filename for an article based on topic and platform.
    
    Args:
        topic: The main topic of the article
        platform: Optional publishing platform
        
    Returns:
        A standardized filename
    """
    # Clean the topic to create a valid filename
    clean_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
    clean_topic = clean_topic.lower().replace(" ", "_")
    
    # Truncate if too long
    if len(clean_topic) > 50:
        clean_topic = clean_topic[:50]
    
    # Add platform if specified
    if platform and platform.lower() != "none":
        clean_topic = f"{clean_topic}_{platform.lower()}"
    
    return f"article_{clean_topic}"

def save_article(content: str, metadata: Dict[str, Any]) -> Dict[str, str]:
    """
    Save an article and its metadata to the appropriate directories.
    
    Args:
        content: The article content
        metadata: Dictionary containing article metadata
        
    Returns:
        Dictionary with paths to the saved files
    """
    # Generate base filename
    base_filename = generate_filename(metadata.get("topic", "untitled"), 
                                     metadata.get("platform"))
    
    # Add timestamp for versioned file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_filename = f"{base_filename}_{timestamp}.txt"
    latest_filename = f"{base_filename}.txt"
    
    # Save the article content (both timestamped and latest versions)
    timestamped_path = os.path.join(ARTICLES_DIR, timestamped_filename)
    latest_path = os.path.join(ARTICLES_DIR, latest_filename)
    
    with open(timestamped_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Save metadata
    metadata_filename = f"{base_filename}_{timestamp}.json"
    metadata_path = os.path.join(METADATA_DIR, metadata_filename)
    
    # Add file information to metadata
    metadata["timestamp"] = timestamp
    metadata["article_file"] = timestamped_filename
    metadata["generation_time"] = datetime.now().isoformat()
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    return {
        "article_path": timestamped_path,
        "latest_path": latest_path,
        "metadata_path": metadata_path
    }

def get_article_history(topic: str = None, platform: str = None) -> list:
    """
    Get a list of previously generated articles, optionally filtered by topic or platform.
    
    Args:
        topic: Optional topic to filter by
        platform: Optional platform to filter by
        
    Returns:
        List of dictionaries with article information
    """
    articles = []
    
    # Get all metadata files
    metadata_files = [f for f in os.listdir(METADATA_DIR) if f.endswith(".json")]
    
    for metadata_file in metadata_files:
        metadata_path = os.path.join(METADATA_DIR, metadata_file)
        
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                
            # Apply filters if specified
            if topic and topic.lower() not in metadata.get("topic", "").lower():
                continue
                
            if platform and platform.lower() != metadata.get("platform", "").lower():
                continue
                
            # Add to results
            article_info = {
                "topic": metadata.get("topic", "Unknown"),
                "platform": metadata.get("platform", "None"),
                "timestamp": metadata.get("timestamp", "Unknown"),
                "article_file": metadata.get("article_file", ""),
                "metadata_file": metadata_file
            }
            
            articles.append(article_info)
                
        except Exception as e:
            print(f"Error reading metadata file {metadata_file}: {e}")
    
    # Sort by timestamp (newest first)
    articles.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return articles 