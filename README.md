# AI Bug Report Analyzer

An AI-powered application that analyzes software bug descriptions written in natural language and generates structured bug reports using **Google Gemini, LangGraph, and FastAPI**.

## Project Overview

The AI Bug Report Analyzer helps developers understand and organize software bug reports. Users describe a problem in simple English, and the application analyzes it through a four-node LangGraph workflow to generate a readable report.

The generated report includes the bug title, affected feature, issue summary, severity level, possible root causes, original description, and an investigation note.

## Objectives

- Analyze software bugs described in natural language.
- Extract important information from bug descriptions.
- Classify bugs by severity.
- Suggest possible technical root causes.
- Generate structured bug reports automatically.
- Demonstrate an AI workflow using LangGraph and Gemini.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Google Gemini | Natural-language bug analysis |
| LangGraph | Workflow orchestration |
| LangChain Google GenAI | Gemini model integration |
| FastAPI | Backend API |
| Pydantic | Input validation and structured output |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | API requests and report display |
| python-dotenv | Environment variable management |

## Workflow Architecture

The application follows a sequential workflow consisting of four LangGraph nodes.

```text
User Input
    |
    v
Bug Description
    |
    v
Node 1: Bug Analysis
    |
    |-- Bug Title
    |-- Affected Feature
    |-- Issue Summary
    |
    v
Node 2: Severity Detection
    |
    |-- Critical
    |-- High
    |-- Medium
    |-- Low
    |
    v
Node 3: Root Cause Suggestion
    |
    |-- Possible Technical Causes
    |
    v
Node 4: Format Report
    |
    v
Structured Bug Report
    |
    v
END
```

### Node 1: Bug Analysis

Analyzes the user's description and extracts:

- Bug title
- Affected feature
- Issue summary

### Node 2: Severity Detection

Classifies the bug into one of four severity levels:

- **Critical:** Severe security issues, major outages, or significant data loss.
- **High:** Important functionality is unusable for affected users.
- **Medium:** Partial functionality is affected or a workaround exists.
- **Low:** Minor cosmetic or low-impact issues.

The classification depends on the information available in the description.

### Node 3: Root Cause Suggestion

Suggests possible technical explanations, such as API failures, frontend state issues, authentication problems, or routing errors.

These suggestions are hypotheses and must be verified through investigation and testing.

### Node 4: Format Report

Combines the analysis results into a structured JSON report that the frontend can display in a readable format.

## Project Structure

```text
AI-Bug-Report-Analyzer/
|
|-- app.py
|-- requirements.txt
|-- .env
|-- .env.example
|-- .gitignore
|
|-- templates/
|   |-- index.html
|
|-- static/
    |-- style.css
    |-- script.js
```

### File Descriptions

- `app.py`: Defines the FastAPI application, Gemini integration, LangGraph state, four workflow nodes, and API endpoints.
- `requirements.txt`: Contains the Python dependencies.
- `.env`: Stores the Gemini API key and model configuration.
- `.env.example`: Provides a template for required environment variables without exposing secrets.
- `.gitignore`: Prevents sensitive files and virtual environments from being committed.
- `templates/index.html`: Defines the web interface.
- `static/style.css`: Styles the application.
- `static/script.js`: Sends bug descriptions to the API and displays generated reports.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sohailzainab629-cpu/AI-Bug-Report-Analyzer.git
cd AI-Bug-Report-Analyzer
```

If the project has not been pushed to GitHub yet, open the existing project folder instead.

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
py -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API Key

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Replace the placeholder with your own API key.

**Security:** Never upload your `.env` file or expose your API key in source code.

### 5. Run the Application

```powershell
python -m uvicorn app:app --reload
```

The application will run locally at:

- **Web Application:** http://127.0.0.1:8000
- **Swagger API Documentation:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health

Keep the terminal open while using the application.

## API Documentation

### POST `/analyze`

Accepts a natural-language bug description and returns a structured bug report.

**Request Body**

```json
{
  "description": "When a user logs in with valid credentials, the page keeps loading and the dashboard never opens."
}
```

**Example Response**

```json
{
  "report": {
    "title": "Login page keeps loading",
    "affected_feature": "Login",
    "issue_summary": "The dashboard does not open after valid login credentials are submitted.",
    "severity": "High",
    "severity_reason": "Users cannot access the dashboard through the login flow.",
    "possible_causes": [
      "The authentication API request may be hanging.",
      "The frontend loading state may not be reset.",
      "A routing or session-handling issue may prevent navigation."
    ],
    "original_description": "When a user logs in with valid credentials, the page keeps loading and the dashboard never opens.",
    "investigation_note": "Possible causes are hypotheses and require testing."
  }
}
```

The example is illustrative. Actual output may vary depending on the bug description and Gemini's response.

### GET `/health`

Checks whether the application is running.

Example response:

```json
{
  "status": "ok",
  "application": "AI Bug Report Analyzer",
  "model": "gemini-3.8-flash"
}
```

## How to Use the Application

1. Start the FastAPI server.
2. Open the web application in your browser.
3. Enter a software bug description in the text area.
4. Click **Analyze Bug**.
5. Wait for the LangGraph workflow to execute.
6. Review the generated bug title, affected feature, summary, severity, possible causes, and investigation note.
7. Use the Copy Report feature to copy the generated report.

## Example Bug Description

```text
When a user enters the correct email and password on the login page
and clicks the Login button, the page keeps loading and does not open
the dashboard. Sometimes, refreshing the page fixes the issue.
```

The application analyzes this description and generates a structured bug report.

## Error Handling and Validation

The application includes:

- Input validation using Pydantic.
- A minimum description length of 10 characters.
- A maximum description length of 10,000 characters.
- Error handling for failed analysis requests.
- Terminal logging to help identify errors during workflow execution.
- A health-check endpoint.

Gemini availability, API quotas, network connectivity, and model access may affect whether an analysis succeeds.

## Limitations

- Root cause suggestions are not verified diagnoses.
- Severity classifications depend on the information supplied by the user.
- The application does not automatically inspect source code or reproduce bugs.
- Reports are not persisted in a database.
- Results depend on the availability and behavior of the configured Gemini model.

## Future Improvements

- Save generated reports in a database.
- Add bug reproduction steps and expected versus actual results.
- Support report export to PDF.
- Add report history and search.
- Integrate with GitHub Issues or other issue-tracking systems.
- Improve automated testing and model error handling.

## Conclusion

The AI Bug Report Analyzer demonstrates how generative AI can help organize software bug reports. By combining Gemini, LangGraph, and FastAPI, the application converts natural-language descriptions into structured reports through a clear four-node workflow.

This project provides practical experience with LLM integration, workflow orchestration, structured output, API development, and frontend-backend communication.

## Author

**Zainab Sohail**

AI and Data Science Student  
Saylani Mass IT Training (SMIT)

## License

This project was developed for educational and learning purposes.
