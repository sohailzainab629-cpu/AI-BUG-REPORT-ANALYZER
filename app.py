
import os
import traceback
from typing import TypedDict, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

load_dotenv()

app = FastAPI(title="AI Bug Report Analyzer")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please configure it in your .env file."
    )

model = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=API_KEY,
)


# --------------------------------------------------
# 2. Structured Output Schemas
# --------------------------------------------------

class BugAnalysis(BaseModel):
    title: str = Field(description="Short, clear bug title")
    affected_feature: str = Field(description="Affected application feature")
    issue_summary: str = Field(description="Summary of the reported issue")


class SeverityResult(BaseModel):
    severity: Literal["Critical", "High", "Medium", "Low"]
    severity_reason: str


class RootCauseResult(BaseModel):
    possible_causes: list[str]


class FinalBugReport(BaseModel):
    title: str
    affected_feature: str
    issue_summary: str
    severity: Literal["Critical", "High", "Medium", "Low"]
    severity_reason: str
    possible_causes: list[str]
    original_description: str
    investigation_note: str


# --------------------------------------------------
# 3. LangGraph State
# --------------------------------------------------

class BugState(TypedDict, total=False):
    bug_description: str
    title: str
    affected_feature: str
    issue_summary: str
    severity: str
    severity_reason: str
    possible_causes: list[str]
    final_report: dict


# --------------------------------------------------
# 4. Node 1: Bug Analysis
# --------------------------------------------------

def bug_analysis_node(state: BugState):
    print("[Node 1] Analyzing bug description...")

    analyzer = model.with_structured_output(BugAnalysis)

    result = analyzer.invoke([
        (
            "system",
            "Analyze the software bug. Extract a concise title, affected "
            "feature, and issue summary. Do not invent missing information."
        ),
        ("human", state["bug_description"]),
    ])

    return {
        "title": result.title,
        "affected_feature": result.affected_feature,
        "issue_summary": result.issue_summary,
    }


# --------------------------------------------------
# 5. Node 2: Severity Detection
# --------------------------------------------------

def severity_detection_node(state: BugState):
    print("[Node 2] Detecting severity...")

    detector = model.with_structured_output(SeverityResult)

    result = detector.invoke([
        (
            "system",
            "Classify bug severity using these guidelines:\n"
            "Critical: severe security issue, major outage, or major data loss.\n"
            "High: an important feature is unusable for affected users.\n"
            "Medium: partial functionality is affected or a workaround exists.\n"
            "Low: cosmetic or minor issue.\n"
            "Use the description and explain uncertainty if evidence is limited."
        ),
        (
            "human",
            f"Description: {state['bug_description']}\n"
            f"Title: {state['title']}\n"
            f"Feature: {state['affected_feature']}\n"
            f"Summary: {state['issue_summary']}"
        ),
    ])

    return {
        "severity": result.severity,
        "severity_reason": result.severity_reason,
    }


# --------------------------------------------------
# 6. Node 3: Root Cause Suggestion
# --------------------------------------------------

def root_cause_node(state: BugState):
    print("[Node 3] Suggesting possible root causes...")

    analyzer = model.with_structured_output(RootCauseResult)

    result = analyzer.invoke([
        (
            "system",
            "Suggest 2 to 4 plausible technical causes. These are hypotheses, "
            "not confirmed facts. Base them on the supplied bug description."
        ),
        (
            "human",
            f"Description: {state['bug_description']}\n"
            f"Title: {state['title']}\n"
            f"Feature: {state['affected_feature']}\n"
            f"Summary: {state['issue_summary']}"
        ),
    ])

    return {"possible_causes": result.possible_causes}


# --------------------------------------------------
# 7. Node 4: Format Final Report
# --------------------------------------------------

def format_report_node(state: BugState):
    print("[Node 4] Formatting final bug report...")

    formatter = model.with_structured_output(FinalBugReport)

    result = formatter.invoke([
        (
            "system",
            "Create a clear structured bug report using the supplied data. "
            "Preserve the existing severity and possible causes. Do not "
            "invent facts. Clearly state that possible causes need testing."
        ),
        (
            "human",
            f"Original description: {state['bug_description']}\n"
            f"Title: {state['title']}\n"
            f"Affected feature: {state['affected_feature']}\n"
            f"Issue summary: {state['issue_summary']}\n"
            f"Severity: {state['severity']}\n"
            f"Severity reason: {state['severity_reason']}\n"
            f"Possible causes: {state['possible_causes']}"
        ),
    ])

    return {"final_report": result.model_dump()}


# --------------------------------------------------
# 8. Build LangGraph Workflow
# --------------------------------------------------

builder = StateGraph(BugState)

builder.add_node("bug_analysis", bug_analysis_node)
builder.add_node("severity_detection", severity_detection_node)
builder.add_node("root_cause_suggestion", root_cause_node)
builder.add_node("format_report", format_report_node)

builder.add_edge(START, "bug_analysis")
builder.add_edge("bug_analysis", "severity_detection")
builder.add_edge("severity_detection", "root_cause_suggestion")
builder.add_edge("root_cause_suggestion", "format_report")
builder.add_edge("format_report", END)

bug_graph = builder.compile()


# --------------------------------------------------
# 9. Frontend Route
# --------------------------------------------------

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


# --------------------------------------------------
# 10. Request Validation
# --------------------------------------------------

class BugRequest(BaseModel):
    description: str = Field(min_length=10, max_length=10000)


# --------------------------------------------------
# 11. Analyze Bug API
# --------------------------------------------------

@app.post("/analyze")
def analyze_bug(request: BugRequest):
    description = request.description.strip()

    if len(description) < 10:
        raise HTTPException(
            status_code=422,
            detail="Please provide a bug description of at least 10 characters.",
        )

    try:
        print("\n" + "=" * 50)
        print("New bug analysis request received")
        print(f"Gemini model: {MODEL_NAME}")

        result = bug_graph.invoke({
            "bug_description": description
        })

        report = result.get("final_report")

        if not report:
            raise ValueError("LangGraph finished without producing a report.")

        print("Bug report generated successfully.")
        print("=" * 50 + "\n")

        return {"report": report}

    except Exception as exc:
        print("\nBUG ANALYSIS FAILED")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error details: {exc}")
        traceback.print_exc()
        print("=" * 50 + "\n")

        raise HTTPException(
            status_code=500,
            detail=(
                f"Bug analysis failed ({type(exc).__name__}): {str(exc)}"
            ),
        ) from exc


# --------------------------------------------------
# 12. Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "AI Bug Report Analyzer",
        "model": MODEL_NAME,
    }

