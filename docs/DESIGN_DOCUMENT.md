# ApplyBots Clone - System Design Document

> **Project:** Automated Job Application Platform (Agentic AI)  
> **Version:** 2.1  
> **Date:** January 30, 2026  
> **Backend:** Python + FastAPI + AutoGen  
> **LLM Provider:** Together AI (Open Source Models)

---

## 1. Executive Summary

An **agentic AI-powered platform** that automates job discovery, resume tailoring, and application submission using **AutoGen multi-agent orchestration**. Multiple specialized AI agents collaborate to handle different aspects of the job application process, communicating through LLMs for intelligent decision-making.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React/Next.js)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Auth    │ │ Dashboard│ │ Profile  │ │   Jobs   │ │  Agent   │          │
│  │  Pages   │ │  Views   │ │  Setup   │ │  Browser │ │  Chat    │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
└───────┼────────────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │            │
        └────────────┴────────────┴─────┬──────┴────────────┘
                                        │ REST API / WebSocket
┌───────────────────────────────────────┴─────────────────────────────────────┐
│                         API GATEWAY (FastAPI + Python)                       │
│              Rate Limiting │ JWT Auth │ Pydantic Validation                  │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────┴─────────────────────────────────────┐
│                   AUTOGEN AGENT ORCHESTRATION (Together AI)                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │               ORCHESTRATOR AGENT (DeepSeek-R1-0528)                  │    │
│  │            Coordinates all agents and manages workflow               │    │
│  └──────────────────────────────┬──────────────────────────────────────┘    │
│                                 │                                            │
│  ┌──────────────┬───────────────┼───────────────┬──────────────┐            │
│  │              │               │               │              │            │
│  ▼              ▼               ▼               ▼              ▼            │
│ ┌────────┐  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐           │
│ │Resume  │  │  Job   │    │ Match  │    │ Apply  │    │Quality │           │
│ │ Agent  │  │Scraper │    │ Agent  │    │ Agent  │    │Control │           │
│ │(Qwen3) │  │ Agent  │    │(Llama4)│    │(Llama4)│    │ Agent  │           │
│ └────────┘  └────────┘    └────────┘    └────────┘    └────────┘           │
│     │           │              │             │             │                │
│     │      ┌────┴────┐         │             │             │                │
│     │      │ Critic  │         │             │             │                │
│     │      │ Agent   │◄────────┴─────────────┴─────────────┘                │
│     │      └─────────┘                                                      │
│     │                                                                        │
│  ┌──┴──────────────────────────────────────────────────────────────────┐    │
│  │                         TOOL AGENTS                                  │    │
│  │   Browser Agent │ Email Agent │ Form Filler │ Document Generator    │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────┴─────────────────────────────────────┐
│                           BACKGROUND WORKERS (Celery + Redis)                │
│       Job Scraper │ Application Queue │ Status Monitor │ Notifications       │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────┴─────────────────────────────────────┐
│                              DATA LAYER                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │   Redis     │  │   AWS S3    │  │  ChromaDB   │        │
│  │  (Primary)  │  │(Cache/Queue)│  │  (Files)    │  │ (Vectors)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. AutoGen Multi-Agent Architecture

### 3.1 Agent Overview (Together AI Models)

| Agent Name | Together AI Model | Cost/1M Tokens | Role | Capabilities |
|------------|-------------------|----------------|------|--------------|
| **Orchestrator** | DeepSeek-R1-0528 | $3.00 / $7.00 | Coordinates all agents | Task routing, workflow management, reasoning |
| **Resume Agent** | Qwen3 235B A22B | $0.65 / $3.00 | Resume parsing & optimization | Parse, analyze, tailor resumes |
| **Job Scraper Agent** | Llama 4 Scout | $0.18 / $0.59 | Job discovery | Search, filter, extract job data |
| **Match Agent** | Llama 4 Maverick | $0.27 / $0.85 | Job-candidate matching | Scoring, gap analysis |
| **Apply Agent** | Llama 3.3 70B | $0.88 / $0.88 | Application submission | Form filling, cover letters |
| **Quality Control Agent** | DeepSeek-V3.1 | $0.60 / $1.25 | Review & validation | Check quality, prevent errors |
| **Critic Agent** | Qwen QwQ-32B | $1.20 / $1.20 | Feedback & improvement | Review agent outputs, reasoning |
| **Coder Agent** | Qwen3-Coder 480B | $2.00 / $2.00 | Code generation | Form automation scripts |
| **Browser Agent** | - | - | Web automation | Playwright-based actions |

### 3.2 Agent Communication Flow

```
User Request
     │
     ▼
┌─────────────────┐
│  Orchestrator   │ ◄─── Manages conversation and delegates tasks
└────────┬────────┘
         │
    ┌────┴────┬─────────────┬─────────────┐
    ▼         ▼             ▼             ▼
┌───────┐ ┌───────┐   ┌──────────┐  ┌──────────┐
│Resume │ │ Job   │   │  Match   │  │  Apply   │
│ Agent │ │Scraper│   │  Agent   │  │  Agent   │
└───┬───┘ └───┬───┘   └────┬─────┘  └────┬─────┘
    │         │            │             │
    └─────────┴─────┬──────┴─────────────┘
                    ▼
            ┌──────────────┐
            │ Critic Agent │ ◄─── Reviews all outputs
            └──────┬───────┘
                   ▼
            ┌──────────────┐
            │   Quality    │
            │   Control    │ ◄─── Final validation
            └──────────────┘
                   │
                   ▼
            Final Output
```

### 3.3 AutoGen Agent Definitions (Together AI)

```python
# agents/config.py

import os
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Together AI Base Configuration
TOGETHER_API_BASE = "https://api.together.xyz/v1"
TOGETHER_API_KEY = os.environ["TOGETHER_API_KEY"]

# ============================================================================
# TOGETHER AI MODEL CONFIGURATIONS
# All models use OpenAI-compatible API format
# ============================================================================

# DeepSeek-R1: Best for complex reasoning and orchestration
config_deepseek_r1 = [
    {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# DeepSeek-V3.1: Great for quality control and review tasks
config_deepseek_v3 = [
    {
        "model": "deepseek-ai/DeepSeek-V3.1",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# Llama 4 Maverick: Best for matching and analysis
config_llama4_maverick = [
    {
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# Llama 4 Scout: Fast and efficient for scraping tasks
config_llama4_scout = [
    {
        "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# Llama 3.3 70B: Excellent for content generation
config_llama3_70b = [
    {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# Qwen3 235B: Best for document understanding and parsing
config_qwen3_235b = [
    {
        "model": "Qwen/Qwen3-235B-A22B-fp8-tput",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# Qwen QwQ-32B: Excellent for reasoning and critique
config_qwen_qwq = [
    {
        "model": "Qwen/QwQ-32B",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# Qwen3-Coder: Best for code generation tasks
config_qwen3_coder = [
    {
        "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
        "api_key": TOGETHER_API_KEY,
        "base_url": TOGETHER_API_BASE,
    }
]

# LLM Config objects for agents
llm_config_orchestrator = {
    "config_list": config_deepseek_r1,
    "temperature": 0.3,  # Lower temp for orchestration
    "timeout": 180,
}

llm_config_resume = {
    "config_list": config_qwen3_235b,
    "temperature": 0.5,
    "timeout": 120,
}

llm_config_scraper = {
    "config_list": config_llama4_scout,
    "temperature": 0.3,
    "timeout": 60,
}

llm_config_matcher = {
    "config_list": config_llama4_maverick,
    "temperature": 0.4,
    "timeout": 90,
}

llm_config_apply = {
    "config_list": config_llama3_70b,
    "temperature": 0.7,  # Higher temp for creative writing
    "timeout": 120,
}

llm_config_qc = {
    "config_list": config_deepseek_v3,
    "temperature": 0.2,  # Low temp for strict review
    "timeout": 90,
}

llm_config_critic = {
    "config_list": config_qwen_qwq,
    "temperature": 0.5,
    "timeout": 90,
}

llm_config_coder = {
    "config_list": config_qwen3_coder,
    "temperature": 0.2,
    "timeout": 120,
}
```

```python
# agents/orchestrator.py

from autogen import AssistantAgent

ORCHESTRATOR_SYSTEM_PROMPT = """You are the Orchestrator Agent for an automated job application system.
Your role is to:
1. Understand user requests and break them into subtasks
2. Delegate tasks to specialized agents (Resume, JobScraper, Match, Apply)
3. Coordinate agent responses and ensure quality
4. Provide status updates to the user
5. Handle errors gracefully and retry when needed

Available Agents:
- ResumeAgent: Parses and optimizes resumes
- JobScraperAgent: Finds and filters job listings
- MatchAgent: Scores job-candidate fit
- ApplyAgent: Generates cover letters and fills applications
- QualityControlAgent: Reviews all outputs before submission

Always think step-by-step and ensure each agent completes its task before moving to the next.
"""

orchestrator_agent = AssistantAgent(
    name="Orchestrator",
    system_message=ORCHESTRATOR_SYSTEM_PROMPT,
    llm_config=llm_config_orchestrator,  # DeepSeek-R1 for reasoning
)
```

```python
# agents/resume_agent.py

RESUME_AGENT_PROMPT = """You are the Resume Agent, specialized in:
1. Parsing resumes from various formats (PDF, DOCX, TXT)
2. Extracting structured information (contact, skills, experience, education)
3. Identifying key strengths and achievements
4. Tailoring resumes for specific job descriptions
5. Optimizing for ATS (Applicant Tracking Systems)

When tailoring a resume:
- Match keywords from job description
- Quantify achievements with metrics
- Highlight relevant experience
- Maintain truthfulness - never fabricate

Output structured JSON with parsed resume data.
"""

resume_agent = AssistantAgent(
    name="ResumeAgent",
    system_message=RESUME_AGENT_PROMPT,
    llm_config=llm_config_resume,  # Qwen3-235B for document understanding
)
```

```python
# agents/job_scraper_agent.py

JOB_SCRAPER_PROMPT = """You are the Job Scraper Agent, specialized in:
1. Understanding job search criteria from user preferences
2. Formulating effective search queries
3. Filtering jobs based on requirements (location, salary, experience)
4. Extracting job details from listings
5. Identifying red flags or scam postings

You have access to these tools:
- search_indeed(query, location, filters)
- search_linkedin(query, location, filters)
- search_glassdoor(query, location, filters)
- get_job_details(job_url)

Always validate job listings and remove duplicates.
"""

job_scraper_agent = AssistantAgent(
    name="JobScraperAgent",
    system_message=JOB_SCRAPER_PROMPT,
    llm_config=llm_config_scraper,  # Llama 4 Scout for fast extraction
)
```

```python
# agents/match_agent.py

MATCH_AGENT_PROMPT = """You are the Match Agent, specialized in:
1. Analyzing job requirements vs candidate qualifications
2. Calculating match scores (0-100)
3. Identifying skill gaps and missing qualifications
4. Recommending jobs worth applying to
5. Prioritizing applications based on fit

Scoring Criteria:
- Skills Match: 40%
- Experience Level: 25%
- Location/Remote: 15%
- Salary Alignment: 10%
- Company Culture Fit: 10%

Return detailed match analysis with recommendations.
"""

match_agent = AssistantAgent(
    name="MatchAgent",
    system_message=MATCH_AGENT_PROMPT,
    llm_config=llm_config_matcher,  # Llama 4 Maverick for analysis
)
```

```python
# agents/apply_agent.py

APPLY_AGENT_PROMPT = """You are the Apply Agent, specialized in:
1. Generating personalized cover letters
2. Answering application screening questions
3. Filling out job application forms
4. Customizing responses for each job
5. Tracking application submissions

For cover letters:
- Keep to 3-4 paragraphs
- Hook with relevant achievement
- Connect experience to job requirements
- Show enthusiasm for the company
- End with clear call to action

For screening questions:
- Be concise but thorough
- Use STAR method when appropriate
- Match tone to company culture
"""

apply_agent = AssistantAgent(
    name="ApplyAgent",
    system_message=APPLY_AGENT_PROMPT,
    llm_config=llm_config_apply,  # Llama 3.3 70B for content generation
)
```

```python
# agents/quality_control_agent.py

QC_AGENT_PROMPT = """You are the Quality Control Agent, the final checkpoint before any submission.

Your responsibilities:
1. Review all generated content for errors
2. Verify factual accuracy against user's profile
3. Check for professionalism and tone
4. Ensure ATS compatibility
5. Validate application completeness
6. Flag any issues for human review

NEVER approve content that:
- Contains fabricated information
- Has spelling/grammar errors
- Doesn't match the job requirements
- Could harm the candidate's reputation

Return APPROVED or REJECTED with detailed feedback.
"""

quality_control_agent = AssistantAgent(
    name="QualityControlAgent",
    system_message=QC_AGENT_PROMPT,
    llm_config=llm_config_qc,  # DeepSeek-V3.1 for strict quality review
)
```

```python
# agents/critic_agent.py

CRITIC_AGENT_PROMPT = """You are the Critic Agent, providing constructive feedback.

Your role:
1. Evaluate outputs from other agents
2. Identify areas for improvement
3. Suggest specific enhancements
4. Ensure consistency across all content
5. Rate quality on a scale of 1-10

Be constructive but thorough. Your feedback helps improve the overall system.
"""

critic_agent = AssistantAgent(
    name="CriticAgent",
    system_message=CRITIC_AGENT_PROMPT,
    llm_config=llm_config_critic,  # Qwen QwQ-32B for reasoning & feedback
)
```

### 3.4 Group Chat Configuration

```python
# agents/group_chat.py

from autogen import GroupChat, GroupChatManager

def create_job_application_group():
    """Create a group chat for job application workflow."""
    
    agents = [
        orchestrator_agent,
        resume_agent,
        job_scraper_agent,
        match_agent,
        apply_agent,
        quality_control_agent,
        critic_agent,
    ]
    
    group_chat = GroupChat(
        agents=agents,
        messages=[],
        max_round=20,
        speaker_selection_method="auto",  # Let DeepSeek-R1 decide who speaks next
    )
    
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=llm_config_orchestrator,  # DeepSeek-R1 manages the group
    )
    
    return manager

def create_resume_optimization_group():
    """Specialized group for resume tasks."""
    
    agents = [
        resume_agent,
        critic_agent,
        quality_control_agent,
    ]
    
    group_chat = GroupChat(
        agents=agents,
        messages=[],
        max_round=10,
    )
    
    return GroupChatManager(groupchat=group_chat, llm_config=llm_config_resume)
```

### 3.5 Agent Tools (Function Calling)

```python
# agents/tools.py

from autogen import register_function
import asyncio

# Tool definitions for agents
AGENT_TOOLS = [
    {
        "name": "parse_resume",
        "description": "Parse a resume file and extract structured data",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to resume file"},
                "format": {"type": "string", "enum": ["pdf", "docx", "txt"]}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "search_jobs",
        "description": "Search for jobs across multiple platforms",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "location": {"type": "string"},
                "job_type": {"type": "string", "enum": ["full-time", "part-time", "contract"]},
                "remote": {"type": "boolean"},
                "salary_min": {"type": "integer"},
                "platforms": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculate_match_score",
        "description": "Calculate match score between resume and job",
        "parameters": {
            "type": "object",
            "properties": {
                "resume_data": {"type": "object"},
                "job_data": {"type": "object"}
            },
            "required": ["resume_data", "job_data"]
        }
    },
    {
        "name": "generate_cover_letter",
        "description": "Generate a tailored cover letter",
        "parameters": {
            "type": "object",
            "properties": {
                "resume_data": {"type": "object"},
                "job_data": {"type": "object"},
                "tone": {"type": "string", "enum": ["formal", "conversational", "enthusiastic"]}
            },
            "required": ["resume_data", "job_data"]
        }
    },
    {
        "name": "submit_application",
        "description": "Submit a job application via browser automation",
        "parameters": {
            "type": "object",
            "properties": {
                "job_url": {"type": "string"},
                "resume_path": {"type": "string"},
                "cover_letter": {"type": "string"},
                "answers": {"type": "object"}
            },
            "required": ["job_url", "resume_path"]
        }
    },
    {
        "name": "browse_webpage",
        "description": "Navigate and extract data from a webpage",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "action": {"type": "string", "enum": ["read", "click", "fill", "screenshot"]},
                "selector": {"type": "string"},
                "value": {"type": "string"}
            },
            "required": ["url", "action"]
        }
    }
]

# Tool implementations
async def parse_resume(file_path: str, format: str = "pdf") -> dict:
    """Parse resume using document processing."""
    from services.document_processor import process_resume
    return await process_resume(file_path, format)

async def search_jobs(query: str, location: str = None, **filters) -> list:
    """Search jobs across platforms."""
    from services.job_scraper import JobScraperService
    scraper = JobScraperService()
    return await scraper.search(query, location, **filters)

async def calculate_match_score(resume_data: dict, job_data: dict) -> dict:
    """Calculate job-resume match score."""
    from services.matcher import MatcherService
    matcher = MatcherService()
    return await matcher.calculate_score(resume_data, job_data)

async def generate_cover_letter(resume_data: dict, job_data: dict, tone: str = "formal") -> str:
    """Generate tailored cover letter."""
    from services.cover_letter import CoverLetterService
    service = CoverLetterService()
    return await service.generate(resume_data, job_data, tone)

async def submit_application(job_url: str, resume_path: str, cover_letter: str = None, answers: dict = None) -> dict:
    """Submit application via browser automation."""
    from services.browser_automation import BrowserAutomation
    browser = BrowserAutomation()
    return await browser.submit_application(job_url, resume_path, cover_letter, answers)

# Register tools with agents
def register_agent_tools():
    register_function(
        parse_resume,
        caller=resume_agent,
        executor=user_proxy,
        name="parse_resume",
        description="Parse a resume file"
    )
    register_function(
        search_jobs,
        caller=job_scraper_agent,
        executor=user_proxy,
        name="search_jobs",
        description="Search for jobs"
    )
    # ... register other tools
```

---

## 4. Backend Architecture (Python)

### 4.1 Technology Stack

| Component | Technology |
|-----------|------------|
| Runtime | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 + Alembic |
| Agent Framework | AutoGen 0.2+ |
| Task Queue | Celery + Redis |
| LLM Provider | Together AI (OpenAI-compatible) |
| Vector DB | ChromaDB |
| Embeddings | Together AI (BGE-Large-EN v1.5) |
| Browser Automation | Playwright |

### 4.2 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entrypoint
│   ├── config.py                  # Settings & environment
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Main router
│   │       ├── auth.py
│   │       ├── profile.py
│   │       ├── jobs.py
│   │       ├── applications.py
│   │       ├── agents.py          # Agent interaction endpoints
│   │       └── websocket.py       # Real-time updates
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── config.py              # LLM configurations
│   │   ├── orchestrator.py        # Main orchestrator agent
│   │   ├── resume_agent.py        # Resume processing
│   │   ├── job_scraper_agent.py   # Job discovery
│   │   ├── match_agent.py         # Job matching
│   │   ├── apply_agent.py         # Application submission
│   │   ├── quality_control.py     # QC agent
│   │   ├── critic_agent.py        # Feedback agent
│   │   ├── tools.py               # Agent tool definitions
│   │   └── workflows.py           # Multi-agent workflows
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── resume.py
│   │   ├── job.py
│   │   ├── application.py
│   │   └── subscription.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── job.py
│   │   ├── application.py
│   │   └── agent.py               # Agent request/response schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── document_processor.py  # Resume parsing
│   │   ├── job_scraper.py         # Web scraping
│   │   ├── matcher.py             # Job matching logic
│   │   ├── cover_letter.py        # Cover letter generation
│   │   ├── browser_automation.py  # Playwright automation
│   │   └── vector_store.py        # ChromaDB operations
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py          # Celery configuration
│   │   ├── job_scraper.py         # Scheduled scraping
│   │   ├── application_submitter.py
│   │   └── status_checker.py
│   │
│   └── db/
│       ├── __init__.py
│       ├── session.py             # Database session
│       └── migrations/            # Alembic migrations
│
├── tests/
├── alembic.ini
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

### 4.3 FastAPI Endpoints

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title="ApplyBots API",
    description="Agentic AI Job Application Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
```

```python
# app/api/v1/agents.py

from fastapi import APIRouter, Depends, WebSocket
from app.agents.workflows import JobApplicationWorkflow
from app.schemas.agent import AgentRequest, AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agents(
    request: AgentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to the agent system.
    The orchestrator will delegate to appropriate agents.
    """
    workflow = JobApplicationWorkflow(user_id=current_user.id)
    response = await workflow.process_message(request.message)
    return AgentResponse(
        message=response.content,
        agents_involved=response.agents,
        actions_taken=response.actions,
    )

@router.post("/apply-jobs", response_model=AgentResponse)
async def auto_apply_to_jobs(
    job_ids: list[str],
    current_user: User = Depends(get_current_user)
):
    """Trigger auto-apply workflow for selected jobs."""
    workflow = JobApplicationWorkflow(user_id=current_user.id)
    results = await workflow.bulk_apply(job_ids)
    return results

@router.post("/optimize-resume", response_model=AgentResponse)
async def optimize_resume_for_job(
    resume_id: str,
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Optimize resume for a specific job using agents."""
    workflow = JobApplicationWorkflow(user_id=current_user.id)
    result = await workflow.optimize_resume(resume_id, job_id)
    return result

@router.websocket("/ws/chat")
async def websocket_agent_chat(
    websocket: WebSocket,
    current_user: User = Depends(get_ws_current_user)
):
    """Real-time chat with agent system via WebSocket."""
    await websocket.accept()
    workflow = JobApplicationWorkflow(user_id=current_user.id)
    
    try:
        while True:
            message = await websocket.receive_text()
            async for response in workflow.stream_process(message):
                await websocket.send_json({
                    "type": "agent_response",
                    "agent": response.agent_name,
                    "content": response.content,
                    "is_final": response.is_final,
                })
    except WebSocketDisconnect:
        pass
```

### 4.4 Agent Workflow Implementation

```python
# app/agents/workflows.py

from autogen import GroupChat, GroupChatManager
from app.agents import (
    orchestrator_agent,
    resume_agent,
    job_scraper_agent,
    match_agent,
    apply_agent,
    quality_control_agent,
    critic_agent,
)
from app.services.vector_store import VectorStore


class JobApplicationWorkflow:
    """Orchestrates multi-agent job application workflow."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.vector_store = VectorStore()
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize agent group chat."""
        self.agents = [
            orchestrator_agent,
            resume_agent,
            job_scraper_agent,
            match_agent,
            apply_agent,
            quality_control_agent,
            critic_agent,
        ]
        
        self.group_chat = GroupChat(
            agents=self.agents,
            messages=[],
            max_round=25,
            speaker_selection_method="auto",
        )
        
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=llm_config_gpt4,
        )
    
    async def process_message(self, message: str) -> AgentOutput:
        """Process a user message through the agent system."""
        
        # Add user context
        user_context = await self._get_user_context()
        enriched_message = f"""
        User Context:
        {user_context}
        
        User Request:
        {message}
        """
        
        # Run the group chat
        result = await orchestrator_agent.a_initiate_chat(
            self.manager,
            message=enriched_message,
        )
        
        return self._parse_result(result)
    
    async def bulk_apply(self, job_ids: list[str]) -> list[ApplicationResult]:
        """Apply to multiple jobs using agents."""
        results = []
        
        for job_id in job_ids:
            # Get job details
            job = await self._get_job(job_id)
            user_profile = await self._get_user_profile()
            
            # Step 1: Match Agent evaluates fit
            match_result = await self._run_agent_task(
                match_agent,
                f"Evaluate match between user and job: {job.to_dict()}"
            )
            
            if match_result.score < 60:
                results.append(ApplicationResult(
                    job_id=job_id,
                    status="skipped",
                    reason="Low match score"
                ))
                continue
            
            # Step 2: Resume Agent tailors resume
            tailored_resume = await self._run_agent_task(
                resume_agent,
                f"Tailor resume for job: {job.description}"
            )
            
            # Step 3: Apply Agent generates cover letter
            cover_letter = await self._run_agent_task(
                apply_agent,
                f"Generate cover letter for: {job.title} at {job.company}"
            )
            
            # Step 4: Quality Control reviews
            qc_result = await self._run_agent_task(
                quality_control_agent,
                f"Review application materials: {tailored_resume}, {cover_letter}"
            )
            
            if qc_result.approved:
                # Step 5: Submit application
                submission = await self._submit_application(
                    job, tailored_resume, cover_letter
                )
                results.append(submission)
            else:
                # Critic provides feedback for improvement
                feedback = await self._run_agent_task(
                    critic_agent,
                    f"Provide improvement suggestions: {qc_result.issues}"
                )
                # Retry with improvements...
        
        return results
    
    async def stream_process(self, message: str):
        """Stream agent responses for real-time updates."""
        async for event in self._stream_group_chat(message):
            yield AgentStreamEvent(
                agent_name=event.sender,
                content=event.content,
                is_final=event.is_complete,
            )
```

---

## 5. Database Design

### 5.1 SQLAlchemy Models

```python
# app/models/user.py

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_cuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
    saved_jobs = relationship("SavedJob", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    agent_sessions = relationship("AgentSession", back_populates="user")
```

```python
# app/models/agent_session.py

class AgentSession(Base):
    """Track agent conversation sessions."""
    __tablename__ = "agent_sessions"
    
    id = Column(String, primary_key=True, default=generate_cuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_type = Column(String)  # "job_search", "resume_optimization", etc.
    messages = Column(JSON, default=list)
    agents_used = Column(ARRAY(String), default=list)
    tokens_used = Column(Integer, default=0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    user = relationship("User", back_populates="agent_sessions")
```

### 5.2 Vector Store Schema (ChromaDB)

```python
# app/services/vector_store.py

import chromadb
from chromadb.config import Settings

class VectorStore:
    """ChromaDB for semantic search and agent memory."""
    
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory="./data/chromadb",
            anonymized_telemetry=False,
        ))
        
        # Collections
        self.resumes = self.client.get_or_create_collection("resumes")
        self.jobs = self.client.get_or_create_collection("jobs")
        self.agent_memory = self.client.get_or_create_collection("agent_memory")
    
    async def add_resume(self, user_id: str, resume_text: str, metadata: dict):
        """Store resume embedding for semantic matching."""
        self.resumes.add(
            documents=[resume_text],
            metadatas=[{"user_id": user_id, **metadata}],
            ids=[f"resume_{user_id}_{datetime.utcnow().timestamp()}"]
        )
    
    async def find_matching_jobs(self, resume_embedding: list, top_k: int = 50) -> list:
        """Find semantically similar jobs to resume."""
        results = self.jobs.query(
            query_embeddings=[resume_embedding],
            n_results=top_k,
        )
        return results
    
    async def store_agent_memory(self, session_id: str, memory: str):
        """Store agent conversation memory for context."""
        self.agent_memory.add(
            documents=[memory],
            metadatas=[{"session_id": session_id}],
            ids=[f"memory_{session_id}_{datetime.utcnow().timestamp()}"]
        )
```

---

## 6. Frontend Architecture

### 6.1 Agent Chat Interface Component

```tsx
// components/AgentChat.tsx

import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface AgentMessage {
  id: string;
  agent: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
}

export function AgentChat() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState('');
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const { sendMessage, lastMessage, isConnected } = useWebSocket('/api/v1/agents/ws/chat');
  
  useEffect(() => {
    if (lastMessage) {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        agent: lastMessage.agent,
        content: lastMessage.content,
        timestamp: new Date(),
        isUser: false,
      }]);
      setActiveAgent(lastMessage.is_final ? null : lastMessage.agent);
    }
  }, [lastMessage]);
  
  const handleSend = () => {
    if (!input.trim()) return;
    
    setMessages(prev => [...prev, {
      id: crypto.randomUUID(),
      agent: 'You',
      content: input,
      timestamp: new Date(),
      isUser: true,
    }]);
    
    sendMessage(input);
    setInput('');
  };
  
  return (
    <div className="agent-chat">
      <div className="agent-status">
        {activeAgent && <span>🤖 {activeAgent} is thinking...</span>}
      </div>
      
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.isUser ? 'user' : 'agent'}`}>
            <div className="agent-name">{msg.agent}</div>
            <div className="content">{msg.content}</div>
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask the agents anything..."
          onKeyPress={e => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
```

---

## 7. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLOUD INFRASTRUCTURE                            │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Kubernetes Cluster                           │    │
│  │                                                                       │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │    │
│  │  │ Frontend  │  │  FastAPI  │  │  Celery   │  │  Agent    │        │    │
│  │  │  (Next)   │  │  Backend  │  │  Workers  │  │  Service  │        │    │
│  │  │  3 pods   │  │  5 pods   │  │  3 pods   │  │  2 pods   │        │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │    │
│  │                                                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Managed Services                              │    │
│  │                                                                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │PostgreSQL│  │  Redis   │  │ ChromaDB │  │   S3     │             │    │
│  │  │  (RDS)   │  │(Upstash) │  │ (Vector) │  │ (Files)  │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │    │
│  │                                                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         External APIs                                 │    │
│  │                                                                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │Together  │  │  Stripe  │  │ SendGrid │  │  Twilio  │             │    │
│  │  │   AI     │  │(Billing) │  │ (Email)  │  │  (SMS)   │             │    │
│  │  │  LLMs    │  │          │  │          │  │          │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │    │
│  │                                                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Requirements

```txt
# requirements.txt

# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Agent Framework
pyautogen==0.2.10
openai==1.10.0              # Used for OpenAI-compatible Together AI API
together==1.3.0             # Together AI Python SDK

# Vector Store
chromadb==0.4.22

# Task Queue
celery==5.3.6
redis==5.0.1

# Document Processing
pypdf==4.0.1
python-docx==1.1.0
unstructured==0.12.0

# Web Scraping
playwright==1.41.0
beautifulsoup4==4.12.3
httpx==0.26.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Utilities
tenacity==8.2.3
structlog==24.1.0
```

### 8.1 Environment Variables

```bash
# .env.example

# Together AI
TOGETHER_API_KEY=your_together_api_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ApplyBots

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=ApplyBots-files

# Stripe (billing)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# SendGrid (email)
SENDGRID_API_KEY=SG.xxx

# JWT Auth
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 8.2 Together AI Model Cost Comparison

| Model | Input/1M | Output/1M | Best For |
|-------|----------|-----------|----------|
| DeepSeek-R1-0528 | $3.00 | $7.00 | Orchestration, Complex Reasoning |
| DeepSeek-V3.1 | $0.60 | $1.25 | Quality Control, Review |
| Llama 4 Maverick | $0.27 | $0.85 | Analysis, Matching |
| Llama 4 Scout | $0.18 | $0.59 | Fast Extraction, Scraping |
| Llama 3.3 70B | $0.88 | $0.88 | Content Generation |
| Qwen3 235B A22B | $0.65 | $3.00 | Document Understanding |
| Qwen QwQ-32B | $1.20 | $1.20 | Reasoning, Critique |
| Qwen3-Coder 480B | $2.00 | $2.00 | Code Generation |
| BGE-Large-EN v1.5 | $0.02 | - | Embeddings |

---

## 9. Next Steps

| Phase | Tasks | Duration |
|-------|-------|----------|
| **Phase 1** | Auth + Profile + Resume Upload | 2 weeks |
| **Phase 2** | Agent Setup (AutoGen) + Basic Chat | 2 weeks |
| **Phase 3** | Job Scraping + Vector Search | 2 weeks |
| **Phase 4** | Match Agent + Apply Agent | 2 weeks |
| **Phase 5** | Browser Automation + Submission | 2 weeks |
| **Phase 6** | Quality Control + Testing | 1 week |
| **Phase 7** | Billing + Production Deploy | 1 week |

---

*Document updated with Python/FastAPI backend and AutoGen multi-agent architecture*
