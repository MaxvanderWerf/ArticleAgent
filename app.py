#!/usr/bin/env python3
"""
Agentic Writer System - Web UI

A simple web interface for the Agentic Writer System that allows users to
generate articles on any topic with different styles.
"""

from flask import Flask, render_template, request, redirect, url_for, session
import markdown
import os
import time
from agentic_writer import AgenticSystem

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Available writing styles
WRITING_STYLES = {
    "conversational": "Friendly and casual, like talking to a friend",
    "professional": "Formal and authoritative, suitable for business or academic contexts",
    "storytelling": "Narrative-driven with anecdotes and vivid descriptions",
    "instructional": "Clear, step-by-step guidance with practical advice"
}

# Available publishing platforms
PUBLISHING_PLATFORMS = {
    "medium": "Medium.com - Popular blogging platform with a wide audience",
    "substack": "Substack - Newsletter platform with a subscription model",
    "dev.to": "Dev.to - Community for developers with technical content",
    "linkedin": "LinkedIn Articles - Professional content for your network",
    "none": "No specific platform - General purpose article"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the main page with the form for article generation."""
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '').strip()
        description = request.form.get('description', '').strip()
        style = request.form.get('style', 'conversational')
        platform = request.form.get('platform', 'none')
        
        # Validate inputs
        if not topic:
            return render_template('index.html', 
                                  error="Please enter a topic", 
                                  styles=WRITING_STYLES,
                                  platforms=PUBLISHING_PLATFORMS,
                                  topic=topic,
                                  description=description)
        
        # Store in session for the results page
        session['topic'] = topic
        session['description'] = description
        session['style'] = style
        session['platform'] = platform
        
        # Redirect to the processing page
        return redirect(url_for('process_article'))
    
    # GET request - show the form
    return render_template('index.html', styles=WRITING_STYLES, platforms=PUBLISHING_PLATFORMS)

@app.route('/processing')
def process_article():
    """Show a processing page and start the article generation."""
    topic = session.get('topic')
    description = session.get('description')
    style = session.get('style')
    
    if not topic:
        return redirect(url_for('index'))
    
    # Start the article generation process
    return render_template('processing.html', 
                          topic=topic,
                          description=description,
                          style=WRITING_STYLES.get(style, ""))

@app.route('/generate', methods=['POST'])
def generate():
    """API endpoint to generate the article."""
    topic = session.get('topic')
    description = session.get('description')
    style = session.get('style', 'conversational')
    
    if not topic:
        return {"error": "No topic specified"}, 400
    
    try:
        # Create the system with the selected style
        system = AgenticSystem(topic, description, style)
        
        # Generate the article
        article_path = system.run_with_progress_callback(progress_callback)
        
        # Store the article path in the session
        session['article_path'] = article_path
        
        return {"success": True, "redirect": url_for('show_article')}
    except Exception as e:
        return {"error": str(e)}, 500

def progress_callback(phase, section=None, progress=None, total=None):
    """Callback function to update progress (not used in this simple version)."""
    # In a more advanced implementation, this could update a progress bar
    # using websockets or server-sent events
    pass

@app.route('/article')
def show_article():
    """Display the generated article."""
    article_path = session.get('article_path')
    
    if not article_path or not os.path.exists(article_path):
        return redirect(url_for('index'))
    
    # Read the article content
    with open(article_path, 'r') as f:
        article_content = f.read()
    
    # Convert markdown to HTML
    article_html = markdown.markdown(article_content)
    
    return render_template('article.html', 
                          article_html=article_html,
                          topic=session.get('topic'),
                          description=session.get('description'),
                          style=WRITING_STYLES.get(session.get('style'), ""))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True) 