from flask import Flask, request, jsonify, render_template
import os
from langchain.llms import HuggingFaceEndpoint
from langchain.utilities import WikipediaAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
from langchain_experimental.tools import PythonREPLTool
from langchain.agents import Tool, initialize_agent
import huggingface_hub  # Ensure this is imported

# Set up Flask application
app = Flask(__name__)

# Set up HuggingFace API key and model
api_key = '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'
llm = HuggingFaceEndpoint(
    huggingfacehub_api_token=api_key, 
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
    temperature=0.8,
    max_length=150
)

# Initialize Wikipedia and DuckDuckGo tools
wikipedia = WikipediaAPIWrapper()
search = DuckDuckGoSearchRun()

# Initialize Python REPL Tool
python_tool = Tool(
    name="Python",
    func=PythonREPLTool().run,
    description="Run Python code"
)

# Initialize Wikipedia and DuckDuckGo tools for the agent
wikipedia_tool = Tool(
    name='wikipedia',
    func=wikipedia.run,
    description="Useful for when you need to look up a topic, country, or person on Wikipedia"
)

duckduckgo_tool = Tool(
    name='DuckDuckGo Search',
    func=search.run,
    description="Useful for when you need to do a search on the internet to find information that another tool can't find. Be specific with your input."
)

# Create a list of tools
tools = [python_tool, wikipedia_tool, duckduckgo_tool]

# Initialize the zero-shot agent
zero_shot_agent = initialize_agent(
    agent="zero-shot-react-description",
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=3
)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query', '')
    if not query_text:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        response = zero_shot_agent.run(query_text)
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
