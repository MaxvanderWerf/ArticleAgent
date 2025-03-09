# Agentic AI Article Writer

## Project Vision

This project demonstrates an autonomous multi-agent AI system that writes an article about itself. The system showcases how AI agents can collaborate to create content, explain concepts, and reflect on their own processes.

The core idea is to build an agentic AI system that:

- **Writes a Story**: Produces a Medium-style article titled "My Life as an AI Agent: A Story," explaining AI agents in an engaging, narrative style.
- **Is Truly Agentic**: Operates autonomously with distinct agents (Planner, Writer, Reviewer) that collaborate to create the article.
- **Showcases Capabilities**: Includes sections on how AI agents work, their practical uses, an example task (planning a weekend trip), and a meta-reflection on its own writing process.
- **Uses Multiple Prompts**: Each section is driven by unique prompts, simulating a multi-agent workflow.
- **Demonstrates Tools**: Integrates basic tool-like functionality to extend beyond simple text generation.
- **Outputs Files**: Generates ai_agent_article.txt (the article) and timestamped versions for tracking changes.

This isn't just about explaining AI agents; it's about proving they can create something tangible and creative, reflecting an innovative spin on the concept of agentic AI.

## System Architecture

The system consists of three specialized agents:

1. **Planner Agent**: Creates an article outline with sections and assigns prompts.
2. **Writer Agent**: Generates content for each section using predefined prompts.
3. **Reviewer Agent**: Polishes the text for readability and adds personality.

These agents are coordinated by a central `AgenticSystem` class that manages the workflow and memory.

## Setup and Usage

### Requirements
- Python 3.x
- OpenAI Python package (optional, for API integration)
- python-dotenv (optional, for API key management)

### API Integration
To use the OpenAI API instead of mock responses:
1. Create a `.env` file in the project directory
2. Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`
3. Install required packages: `pip install openai python-dotenv`

### Running the System
1. Clone this repository
2. Install dependencies (if using API): `pip install -r requirements.txt`
3. Run the script:
   ```
   python agentic_writer.py
   ```
4. The system will generate:
   - `ai_agent_article_TIMESTAMP.txt`: The complete article with timestamp
   - `ai_agent_article.txt`: The latest version of the article

### Extending the System
The current implementation can use either mock responses or the OpenAI API. To extend it:
- Add more sophisticated tools for research, fact-checking, etc.
- Implement more complex agent interactions and memory structures
- Try different LLM providers or models

## Output

The system produces an article with the following sections:
- Introduction
- How AI Agents Work
- What You Can Do with AI Agents
- Example: Planning a Weekend Trip
- Reflection: How I Wrote This Article
- Conclusion

Each section is written in a narrative, conversational style that makes the concept of AI agents accessible and engaging.

## Future Enhancements

- Integration with other LLM APIs (Anthropic, etc.)
- More sophisticated tool use (web search, data analysis)
- Enhanced inter-agent communication
- Ability to incorporate feedback and revise content
- Export to different formats (Markdown, HTML, etc.)

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

If you don't provide a Serper API key, the system will use mock search results instead.

---

This project demonstrates the creative potential of AI agents as autonomous content creators, not just tools for human use. It represents a vision of AI systems that can reflect on their own capabilities and communicate them effectively to humans.
