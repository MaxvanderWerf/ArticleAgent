# Agentic AI Article Writer

## Project Vision

This project demonstrates an autonomous multi-agent AI system that writes an article about itself. The system showcases how AI agents can collaborate to create content, explain concepts, and reflect on their own processes.

The core idea is to build an agentic AI system that:

- **Writes a Story**: Produces a Medium-style article titled "My Life as an AI Agent: A Story," explaining AI agents in an engaging, narrative style.
- **Is Truly Agentic**: Operates autonomously with distinct agents (Planner, Writer, Reviewer) that collaborate to create the article.
- **Showcases Capabilities**: Includes sections on how AI agents work, their practical uses, an example task (planning a weekend trip), and a meta-reflection on its own writing process.
- **Uses Multiple Prompts**: Each section is driven by unique prompts, simulating a multi-agent workflow.
- **Demonstrates Tools**: Integrates basic tool-like functionality to extend beyond simple text generation.
- **Outputs Files**: Generates articles with metadata in an organized folder structure.

This isn't just about explaining AI agents; it's about proving they can create something tangible and creative, reflecting an innovative spin on the concept of agentic AI.

## System Architecture

The system consists of four specialized agents:

1. **Planner Agent**: Creates an article outline with sections and assigns prompts.
2. **Writer Agent**: Generates content for each section using predefined prompts.
3. **Reviewer Agent**: Polishes the text for readability and adds personality.
4. **Humanizer Agent**: Adds a human touch to make the content feel more authentic.

These agents are coordinated by a central `AgenticSystem` class that manages the workflow and memory.

## Project Structure

```
ArticleAgent/
├── articles/              # Generated articles
│   └── metadata/          # Article metadata in JSON format
├── src/                   # Source code
│   ├── agents/            # Agent implementations
│   │   ├── base.py        # Base Agent class
│   │   ├── planner.py     # Planner Agent
│   │   ├── writer.py      # Writer Agent
│   │   ├── reviewer.py    # Reviewer Agent
│   │   └── humanizer.py   # Humanizer Agent
│   ├── tools/             # Tool implementations
│   │   └── web_research.py # Web Research Tool
│   ├── utils/             # Utility modules
│   │   ├── config.py      # Configuration settings
│   │   ├── file_manager.py # File management utilities
│   │   └── llm.py         # LLM interaction utilities
│   ├── agentic_system.py  # Main system class
│   └── __init__.py        # Package initialization
├── templates/             # Web UI templates
│   ├── index.html         # Home page
│   ├── processing.html    # Processing page
│   └── article.html       # Article display page
├── app.py                 # Web application
├── main.py                # Command-line interface
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

## Setup and Usage

### Requirements
- Python 3.x
- Dependencies listed in requirements.txt

### API Integration
To use the OpenAI API instead of mock responses:
1. Create a `.env` file in the project directory
2. Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`
3. Optionally, add a Serper API key for web research: `SERPER_API_KEY=your_serper_key_here`

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ArticleAgent.git
cd ArticleAgent

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Command-Line Usage
```bash
# Generate an article
python main.py --topic "AI Agents" --description "How AI agents collaborate" --style conversational --platform medium

# List available writing styles
python main.py --list-styles

# List available publishing platforms
python main.py --list-platforms

# List previously generated articles
python main.py --list-articles
```

### Web Interface
```bash
# Start the web server
python app.py

# Open your browser and navigate to http://localhost:5000
```

## Output

The system produces articles in the `articles` directory with corresponding metadata in `articles/metadata`. Each article includes:

- The full article text in Markdown format
- A JSON metadata file with:
  - Topic, description, style, and platform
  - Generation date and word count
  - Title and other article metadata
  - Generation process details (platform style, research summary, outline, improvements)

## API Setup

This project uses two external APIs:

1. **OpenAI API** - For generating article content
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Get your API key from the dashboard
   - Add it to your .env file as `OPENAI_API_KEY=your_key_here`

2. **Serper API** (optional) - For web research on platform-specific writing styles
   - Sign up at [Serper.dev](https://serper.dev/)
   - Get your API key from the dashboard
   - Add it to your .env file as `SERPER_API_KEY=your_key_here`

If you don't provide API keys, the system will use mock responses instead.

## Future Enhancements

- Integration with other LLM APIs (Anthropic, etc.)
- More sophisticated tool use (web search, data analysis)
- Enhanced inter-agent communication
- Ability to incorporate feedback and revise content
- Export to different formats (HTML, PDF, etc.)
- Support for more publishing platforms and writing styles

---

This project demonstrates the creative potential of AI agents as autonomous content creators, not just tools for human use. It represents a vision of AI systems that can reflect on their own capabilities and communicate them effectively to humans.
