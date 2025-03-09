#!/usr/bin/env python3
"""
Agentic Writer System - Web UI

A simple web interface for the Agentic Writer System that allows users to
generate articles on any topic with different styles.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import markdown
import os
import time
from src.agentic_system import AgenticSystem
from src.utils.config import WRITING_STYLES, PUBLISHING_PLATFORMS
from src.utils.file_manager import get_article_history

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Home page with article generation form.
    """
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '')
        description = request.form.get('description', '')
        style = request.form.get('style', 'conversational')
        platform = request.form.get('platform', 'none')
        
        if not topic:
            return render_template('index.html', 
                                  error="Please enter a topic",
                                  styles=WRITING_STYLES,
                                  platforms=PUBLISHING_PLATFORMS)
        
        # Store in session for the processing page
        session['topic'] = topic
        session['description'] = description
        session['style'] = style
        session['platform'] = platform
        
        # Redirect to processing page
        return redirect(url_for('process_article'))
    
    # GET request - show the form
    return render_template('index.html', 
                          styles=WRITING_STYLES,
                          platforms=PUBLISHING_PLATFORMS)

@app.route('/processing')
def process_article():
    """
    Processing page that shows progress while generating the article.
    """
    # Check if we have the necessary session data
    if 'topic' not in session:
        return redirect(url_for('index'))
    
    return render_template('processing.html',
                          topic=session.get('topic', ''),
                          description=session.get('description', ''),
                          style=session.get('style', 'conversational'),
                          platform=session.get('platform', 'none'))

@app.route('/generate', methods=['POST'])
def generate():
    """
    API endpoint that generates the article and returns progress updates.
    """
    # Get data from session
    topic = session.get('topic', '')
    description = session.get('description', '')
    style = session.get('style', 'conversational')
    platform = session.get('platform', 'none')
    
    if not topic:
        return jsonify({'error': 'No topic provided'}), 400
    
    # Create the agentic system
    system = AgenticSystem(topic, description, style, platform)
    
    # Start the generation process in a separate thread
    import threading
    thread = threading.Thread(target=system.run_with_progress_callback, 
                             args=(progress_callback,))
    thread.daemon = True
    thread.start()
    
    # Return initial response
    return jsonify({
        'status': 'started',
        'message': f'Generating article about {topic}'
    })

def progress_callback(phase, section=None, progress=None, total=None):
    """
    Callback function for progress updates.
    In a real app, this would update a database or use websockets.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    if section:
        print(f"[{timestamp}] Progress: {phase} - {section} - {progress}/{total}")
    else:
        print(f"[{timestamp}] Progress: {phase} - {progress}/{total}")

@app.route('/article')
def show_article():
    """
    Page that displays the generated article.
    """
    # In a real app, we would retrieve the article from a database
    # For now, we'll just get the most recent article from the articles directory
    
    articles = get_article_history()
    
    if not articles:
        return render_template('article.html', 
                              title="No Article Found",
                              content="<p>No articles have been generated yet.</p>",
                              metadata={})
    
    # Get the most recent article
    latest_article = articles[0]
    
    # Read the article file
    from src.utils.config import ARTICLES_DIR
    article_path = os.path.join(ARTICLES_DIR, latest_article["article_file"])
    
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        content = "Error: Could not read article file."
    
    # Read the metadata file
    from src.utils.config import METADATA_DIR
    metadata_path = os.path.join(METADATA_DIR, latest_article["metadata_file"])
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            import json
            metadata = json.load(f)
    except:
        metadata = {}
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content)
    
    return render_template('article.html',
                          title=metadata.get('title', 'Generated Article'),
                          content=html_content,
                          metadata=metadata)

@app.route('/api/progress')
def get_progress():
    """
    API endpoint that returns the current progress.
    In a real app, this would retrieve progress from a database or cache.
    """
    # Mock progress data
    progress_data = {
        'phase': 'writing',
        'section': 'How AI Agents Work',
        'progress': 2,
        'total': 5,
        'message': 'Writing content for section 2 of 5'
    }
    
    return jsonify(progress_data)

@app.route('/api/articles')
def list_articles():
    """
    API endpoint that returns a list of generated articles.
    """
    articles = get_article_history()
    return jsonify(articles)

if __name__ == '__main__':
    app.run(debug=True) 