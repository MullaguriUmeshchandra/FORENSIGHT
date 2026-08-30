# AI Forensics Timeline Reconstruction — Full-Stack Application (Phase 1, 2 & 3)

A digital forensics software application built with a **FastAPI** backend, **PostgreSQL / SQLite** database, **Neo4j** graph integration, and a **React (Vite + Tailwind CSS)** enterprise dashboard. 

The system ingests digital evidence logs, computes SHA-256 custody hashes, standardizes timestamps to UTC, reconstructs chronological event timelines, mathematically calculates unexplained time deltas, detects multi-source contradictions, formulates defensible recommendations using Isolation Forest anomaly detection, visualizes artifact knowledge graphs, and compiles ReportLab PDF reports.

---

## 🛡️ Core Principles & Design

- **Zero Event Fabrication**: Every timeline event originates directly from verified primary or corroborated artifact telemetry.
- **Defensible Forensic Language**: Unexplained transitions and missing evidence are phrased factually without speculation (e.g. *"No supporting artifact was identified to establish a file deletion event during the unexplained interval."*).
- **Enterprise UI Design**: Modeled after professional forensic suites with a dark navy sidebar, crisp white cards, light background (`#f8fafc`), clean typography, and status badges (`CONFIRMED`, `INFERRED`, `MISSING`, `CONTRADICTION`).
- **No Mock Data**: Every stat card, timeline event, gap, contradiction, recommendation, activity log, and report is dynamically computed and fetched from the FastAPI backend database.

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn
- **Relational Database**: PostgreSQL / SQLite via SQLAlchemy 2.0 ORM
- **Graph Database**: Neo4j (Cypher queries & node-link graph visualization with resilient in-memory fallback)
- **AI & Data Analysis**: Pandas, NumPy, Scikit-learn (Isolation Forest anomaly detection)
- **PDF Report Generation**: ReportLab document compilation engine
- **Authentication**: JWT (HS256) with direct bcrypt password hashing & Role-Based Access Control (`Admin`, `Investigator`, `Viewer`)

### Frontend
- **Framework**: React 18, Vite 5, React Router v6
- **Styling**: Tailwind CSS v3, PostCSS, Lucide React icons
- **Graph Visualization**: D3.js (Force-directed knowledge graph layout)
- **HTTP Client**: Centralized Axios client (`src/services/api.js`) with Bearer token interceptors

---

## 📁 Directory Structure

```text
CyberFornesics Project/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifespan hooks
│   │   ├── api/                     # REST API routers (/auth, /cases, /evidence, /timeline, /gaps, /contradictions, /recommendations, /investigation, /reports, /dashboard)
│   │   ├── models/                  # SQLAlchemy ORM models (User, Case, Evidence, Artifact, TimelineEvent, Gap, Contradiction, Recommendation, Report, ActivityLog)
│   │   ├── schemas/                 # Pydantic request/response validation schemas
│   │   ├── services/                # Business logic, normalization, timeline & report services
│   │   ├── processors/              # CSV, JSON, LOG, TXT, XML evidence parsers
│   │   ├── ml/                      # Gap calculation & Isolation Forest anomaly scoring
│   │   ├── graph/                   # Neo4j driver client & graph relationship service
│   │   ├── auth/                    # JWT tokens, bcrypt security & dependencies
│   │   ├── database/                # SQLAlchemy database engine & session maker
│   │   └── utils/                   # Hasher, timestamp parser, structured logger
│   ├── requirements.txt             # Backend dependencies
│   ├── Dockerfile                   # Backend Docker containerization
│   └── tests/                       # Pytest automated test suite (16 modules)
├── frontend/
│   ├── index.html                   # Vite HTML entrypoint
│   ├── package.json                 # Frontend React dependencies
│   ├── vite.config.js               # Vite configuration & proxy settings
│   ├── tailwind.config.js           # Tailwind theme configuration
│   └── src/
│       ├── main.jsx                 # React root renderer
│       ├── App.jsx                  # Main App router & ProtectedLayout
│       ├── index.css                # Tailwind directives
│       ├── context/                 # AuthContext & CaseContext
│       ├── services/                # Centralized Axios API client (src/services/api.js)
│       ├── components/              # Sidebar, Topbar, MetricCard, StatusBadge, Modal, LoadingState, ErrorState, EmptyState, KnowledgeGraph, InvestigationSteps, RecentActivityList, GapSummaryTable, EvidenceSourceGrid
│       └── pages/                   # LoginPage, DashboardPage, EvidencePage, TimelinePage, GapsPage, RecommendationsPage, InvestigationPage, ReportsPage, SettingsPage
├── data/
│   ├── samples/                     # Fictional forensic evidence CSV files
│   └── seed_sample_case.py          # Automated CASE-001 seeding & analysis script
├── docker-compose.yml               # Multi-container orchestration (PostgreSQL, Neo4j, Backend)
├── .env.example                     # Environment configuration template
└── README.md
```

---

## 🚀 How to Run the Application

### 1. Start the Backend API Server
```powershell
& "backend\.venv\Scripts\uvicorn.exe" app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
- **Backend API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **OpenAPI Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Start the React Frontend Development Server
```powershell
$env:Path = "C:\Users\prade\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.19.0-win-x64;$env:Path"
cd frontend
npm.cmd run dev
```
- **Frontend App**: [http://localhost:5173](http://localhost:5173)

### 3. Seed Demonstration Scenario (CASE-001)
To seed and analyze the sample case with pre-loaded evidence files:
```powershell
& "backend\.venv\Scripts\python.exe" data\seed_sample_case.py
```

### 4. Run Pytest Test Suite
```powershell
& "backend\.venv\Scripts\pytest.exe" backend\tests -v
```

---

## 🔐 Credentials & Access

| Role | Username | Password | Access Privileges |
|---|---|---|---|
| **Investigator** | `investigator` | `Investigator123!` | Upload evidence, rebuild timeline, generate reports |
| **Admin** | `admin` | `Admin123!` | Full administrative control, delete cases/evidence |
| **Viewer** | `viewer` | `Viewer123!` | Read-only access to timelines, graphs, reports |

---

## 🌐 End-to-End Workflow Demonstration

1. **Sign In**: Navigate to `http://localhost:5173/login` and log in as `investigator` / `Investigator123!`.
2. **Dashboard**: View live metrics (Evidence Sources, Artifacts Processed, Gaps Detected, Recommendations, Reports Generated) and recent audit logs.
3. **Evidence Upload**: Go to `/evidence`, drag and drop `sample_system_logs.csv` or select source type, upload file, and watch real-time SHA-256 calculation and artifact normalization.
4. **Timeline**: Navigate to `/timeline` to inspect the chronologically ordered sequence. Observe the **13-minute unexplained time gap** highlighted between 10:28 UTC and 10:41 UTC. Click any event to view the forensic trace modal.
5. **Gap & Contradiction Analysis**: Go to `/gaps` and `/investigation` to inspect mathematically computed gap severities and cross-source evidence conflicts.
6. **Knowledge Graph**: On `/investigation`, interact with the D3 force-directed node-link graph connecting Cases, Evidence, Artifacts, Devices, and Events. Click any node to inspect properties.
7. **Report Compilation & PDF Download**: Go to `/reports`, click "Generate New Report", choose PDF or Markdown format, preview findings, and download the report file.
