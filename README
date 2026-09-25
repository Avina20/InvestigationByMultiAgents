# Multi-Agent AI Research System
Orchestrate multiple specialized AI agents that work together as a pipeline searching the web, scraping content, writing reports, and reviewing them automatically

- Multi-agent pipeline with LangChain
- Search Agent that retrieves live, reliable web data
- Reader Agent that scrapes and extracts deep content from URLs
- Writer Chains to generate structured, detailed research reports
- Critic Chains to automatically review and score AI-generated output
- Shared pipeline where agents pass state to each other through 
- Streamlit UI for the multi-agent system

## Local setup

### 1. Create and activate a virtual environment

From the project directory, run:

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configure API keys

Create a file named `.env` in the project root and add your API keys:

```dotenv
TAVILY_API_KEY=your_tavily_api_key
GEMINI_API_KEY=your_gemini_api_key
```

The application uses Tavily for web search and Google Gemini for the agent and report generation. Keep `.env` private and do not commit it.

### 4. Start the application

```bash
python -m streamlit run app.py
```

Streamlit will print a local URL, normally `http://localhost:8501`, in the terminal. Open that URL in your browser.

To run the pipeline without the web interface instead:

```bash
python pipeline.py
```


![alt text](<ss investigation.png>)