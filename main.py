#!/usr/bin/env python3
"""
Agentic Writer System - Command Line Interface

A command-line interface for the Agentic Writer System that allows users to
generate articles on any topic with different styles.
"""

import argparse
import sys
from src.agentic_system import AgenticSystem
from src.utils.config import WRITING_STYLES, PUBLISHING_PLATFORMS
from src.utils.file_manager import get_article_history

def progress_callback(phase, section=None, progress=None, total=None):
    """
    Callback function for progress updates.
    Displays progress in the console.
    
    Args:
        phase: Current phase of the generation process
        section: Optional section being processed
        progress: Optional progress value
        total: Optional total value
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    if section:
        print(f"[{timestamp}] [{phase.upper()}] {section} - {progress}/{total}")
    else:
        print(f"[{timestamp}] [{phase.upper()}] {progress}/{total}")
    
    # Flush stdout to ensure progress is displayed immediately
    sys.stdout.flush()

def list_articles():
    """
    List all previously generated articles.
    """
    articles = get_article_history()
    
    if not articles:
        print("No articles have been generated yet.")
        return
    
    print("\nPreviously Generated Articles:")
    print("------------------------------")
    
    for i, article in enumerate(articles):
        print(f"{i+1}. {article['topic']} ({article['platform']}) - {article['timestamp']}")
    
    print()

def list_styles():
    """
    List all available writing styles.
    """
    print("\nAvailable Writing Styles:")
    print("-----------------------")
    
    for style, description in WRITING_STYLES.items():
        print(f"{style}: {description}")
    
    print()

def list_platforms():
    """
    List all available publishing platforms.
    """
    print("\nAvailable Publishing Platforms:")
    print("-----------------------------")
    
    for platform, description in PUBLISHING_PLATFORMS.items():
        print(f"{platform}: {description}")
    
    print()

def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Generate articles using the Agentic Writer System")
    
    # Main arguments
    parser.add_argument("--topic", "-t", help="The main topic of the article")
    parser.add_argument("--description", "-d", help="Additional description or context")
    parser.add_argument("--style", "-s", default="conversational", 
                       choices=list(WRITING_STYLES.keys()),
                       help="The writing style to use")
    parser.add_argument("--platform", "-p", default="none",
                       choices=list(PUBLISHING_PLATFORMS.keys()),
                       help="The target publishing platform")
    
    # Utility commands
    parser.add_argument("--list-articles", action="store_true", help="List previously generated articles")
    parser.add_argument("--list-styles", action="store_true", help="List available writing styles")
    parser.add_argument("--list-platforms", action="store_true", help="List available publishing platforms")
    
    args = parser.parse_args()
    
    # Handle utility commands
    if args.list_articles:
        list_articles()
        return
    
    if args.list_styles:
        list_styles()
        return
    
    if args.list_platforms:
        list_platforms()
        return
    
    # Check if we have a topic
    if not args.topic:
        parser.print_help()
        print("\nError: --topic is required to generate an article")
        return
    
    # Create the agentic system
    system = AgenticSystem(
        topic=args.topic,
        description=args.description or "",
        style=args.style,
        platform=args.platform
    )
    
    # Generate the article with progress updates
    print(f"\nGenerating article about '{args.topic}'...")
    print(f"Style: {args.style}")
    print(f"Platform: {args.platform}")
    print("\nProgress:")
    
    article = system.run_with_progress_callback(progress_callback)
    
    print("\nArticle generation complete!")
    print("The article has been saved to the 'articles' directory.")
    
    # Print a preview
    preview_length = min(500, len(article))
    print(f"\nPreview:\n{article[:preview_length]}...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 