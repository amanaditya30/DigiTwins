# Placement Twin AI 🎓🤖
### *A Production-Grade Multi-Agent AI Career Mentor and Digital Twin Builder*

Placement Twin AI is an autonomous, agentic career mentoring platform. By analyzing a student's projects, resume, skills, academic records, and target company profiles, the system constructs a **Digital Twin** of the student. From there, it conducts mock interviews, performs ATS compliance reviews, identifies skill gaps, logs DSA progress, and schedules daily study roadmaps dynamically.

---

## 🛠️ Technology Stack
*   **Frontend:** Streamlit (UI rendering, radar plotting, interactive chat logs, files ingestion)
*   **Backend:** FastAPI (JWT security, REST APIs, asynchronous background workflows)
*   **Multi-Agent Framework:** LangGraph (StateGraph coordination)
*   **Vector Database (RAG):** ChromaDB (Local persistent client)
*   **RAG LLM & Orchestration:** LangChain (Recursive text splitting, System/Human message generation)
*   **SQL Database:** SQLModel / SQLAlchemy (SQLite default for quick local runs, postgres compatible)

---

## 📋 Resume-Worthy Project Description (Recruiter-Ready)

**Placement Twin AI — Full-Stack AI Engineer / Senior Architect**
*   **Architected and Built** an autonomous, multi-agent AI career mentor that models a student's professional profile ("Digital Twin") to deliver personalized learning paths, resume audits, and mock interview preparations.
*   **Designed a Multi-Agent system** utilizing **LangGraph** to coordinate 9 specialized agents (Profile, Resume ATS, Skill Gap, Projects, Roadmap, DSA, Job Matcher, and Motivation) running within an event-driven directed acyclic graph (DAG).
*   **Implemented a RAG (Retrieval-Augmented Generation)** pipeline using **ChromaDB** and **LangChain** to parse and index syllabus guidelines, CS fundamentals (OS, DBMS, CN), and company-specific interview transcripts with custom recursive chunking.
*   **Developed an interactive Mock Interview interface** using Streamlit chat elements, streaming turn-by-turn evaluations from the backend LLM, and generating detailed scorecard logs storing transcript metrics in an SQL database.
*   **Created a unified dashboard interface** visualizing student sub-scores (DSA, projects, resume compatibility, interview performance) using responsive radar charts and custom HTML glassmorphism styling.
*   **Configured robust developer fallbacks** including a standalone offline `MockLLM` router and `FallbackEmbeddings` to guarantee fully functional local runs even without active internet or third-party API credentials.

---

## 📁 System Folder Structure
```
placement-twin-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # User JWT signin & signup
│   │   │   │   ├── profile.py       # Profiles & Resume parser (pypdf)
│   │   │   │   ├── roadmap.py       # DSA logs & roadmap plans
│   │   │   │   ├── project.py       # Code base audits & recommendations
│   │   │   │   ├── interview.py     # Turn-by-turn mock sessions
│   │   │   │   ├── planner.py       # Checklists & motivation
│   │   │   │   └── rag.py           # RAG document administration
│   │   │   └── api.py               # Aggregates sub-routers
│   │   ├── core/
│   │   │   ├── config.py            # Reads .env variables
│   │   │   ├── security.py          # Hashing & JWT tokens
│   │   │   └── database.py          # Engine & SQLModel creations
│   │   ├── models/
│   │   │   ├── domain.py            # DB schema definitions
│   │   │   └── schemas.py           # Pydantic payloads
│   │   ├── services/
│   │   │   ├── agents/
│   │   │   │   ├── llm.py           # OpenAI/Groq/MockLLM setup
│   │   │   │   ├── state.py         # LangGraph state variables
│   │   │   │   ├── graph.py         # LangGraph DAG compiler
│   │   │   │   └── nodes/
│   │   │   │       └── agent_nodes.py # 9 individual agent nodes
│   │   │   └── rag/
│   │   │       ├── vector_store.py  # Chroma client initializer
│   │   │       └── pipeline.py      # Documents chunking & seeds
│   │   └── main.py                  # API gateway entry point
│   ├── requirements.txt             # Backend dependencies
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app.py                       # User portal entry & credentials forms
│   ├── pages/
│   │   ├── 1_Dashboard.py           # Radar plots & planners
│   │   ├── 2_Resume_Reviewer.py     # ATS reviews & cover letters creator
│   │   ├── 3_Roadmap_&_DSA.py       # Weekly schedules & DSA history
│   │   ├── 4_Mock_Interview.py      # Interactive text mock round
│   │   ├── 5_Project_Analyzer.py    # Audits & documentation templates creator
│   │   └── 6_Job_Matcher.py         # Pastes postings & checks alignment
│   ├── utils/
│   │   └── api_client.py            # Server requests wrapper
│   ├── requirements.txt             # UI client dependencies
│   └── Dockerfile
├── README.md
└── docker-compose.yml
```

---

## 💾 Database Schema Reference
The system utilizes the following SQLModel relationships (SQLite/PostgreSQL compatible):
*   `User`: Keeps credential names, emails, and bcrypt-hashed password values.
*   `Profile`: Connects 1-to-1 with a user. Stores skills list, target companies, and parsed resume contents.
*   `DSAProgress`: Maps 1-to-many. Logs question difficulty, topic tag, and solved timestamps.
*   `MockInterview`: Maps 1-to-many. Stores complete conversation JSON transcripts, recruiters' advice, and scores.
*   `Project`: Maps 1-to-many. Holds suggestions, code audit grades, and interview questions.
*   `Roadmap`: 1-to-1 user mapping. Holds weekly roadmap lists.
*   `DailyPlan`: Records checkmark variables for daily task items.
*   `ReadinessScore`: Aggregates resume, DSA, project, and mock grades with written explanations.

---

## 🚀 Deployment Guide (Run Locally)

### Option A: Running with Docker Compose (Recommended)
This compiles the backend, frontend, and a PostgreSQL database inside Docker containers.

1. Make sure you have Docker and Docker Compose installed.
2. In the root directory, create a `.env` in `backend/` or let compose default to env files.
3. Build and launch services:
   ```bash
   docker-compose up --build
   ```
4. Access portals:
   *   **FastAPI API Swagger Documentation:** `http://127.0.0.1:8000/docs`
   *   **Streamlit Portal:** `http://127.0.0.1:8501`

### Option B: Local Python Run (No Docker)
You can run locally using two terminal sessions.

#### 1. Setup Backend
```bash
cd backend
python -m venv venv
# On windows:
venv\Scripts\activate
# On linux/mac:
source venv/bin/activate

pip install -r requirements.txt
# Copy example configuration
cp .env.example .env
```
Fill out `OPENAI_API_KEY` or `GROQ_API_KEY` in `.env` if you want live LLM calls, otherwise keep them empty to let the offline `MockLLM` generate mock profiles out-of-the-box.

Launch backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

#### 2. Setup Frontend (Second Terminal)
```bash
cd frontend
python -m venv venv
# Activate virtual environment
venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Open `http://127.0.0.1:8501` to view your placement twin career mentor portal.

---

## 🔮 Future Enhancements
*   **Audio/Voice Interviews:** Integrate WebRTC or speech-to-text models to support mock voice interviews.
*   **GitHub API Scrapers:** Integrate OAuth to query GitHub APIs directly and inspect repository commits.
*   **Multi-Modal Profile Ingestion:** Ingest video profiles or cert image credentials.
*   **Deployment Staging:** Push server image to ECS/Cloud Run and frontend on ECS or Streamlit Cloud.
