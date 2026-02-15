# 🚀 Proactive Onboarding Engine (POE)

> **Go from "New Hire" to "Top Performer" in record time.**

**Proactive Onboarding Engine (POE)** uses agentic RAG to automate personalized learning paths. By synthesizing internal documentation with external insights, it minimizes ramp-up time tailored to your role and prior knowledge. Focus on high-impact work while POE handles your curriculum. Accelerate your productivity and hit the ground running.

<img src="./docs/assets/chatwindow-ui-screenshot.png" alt="UI Screenshot for chatbot" />

---

<img src="./docs/assets/roadmap-ui-screenshot.png" alt="UI Screenshot for chatbot" />

---

<img src="./docs/assets/chatwindow-with-questions.png" alt="UI screenshot with AI Generate Questions" >

---

## ✨ Key Features

- **Proactive Curriculum Generation:** No more waiting for a mentor. POE builds your 30-day plan the moment you join.
- **Dual-Source Intelligence:** Combines private company wiki data (via `pgvector`) with public tutorials (YouTube & DuckDuckGo).
- **Knowledge Gap Analysis:** Adjusts the learning curve based on your seniority—skipping the basics for seniors and deep-diving for juniors.
- **Agentic Orchestration:** Uses **LangGraph** to coordinate specialized agents for retrieval, web-search, and curriculum architecture.
- **Task-Oriented Milestones:** Every plan includes actionable milestones like "Submit your first PR" or "Deploy to Staging."

---

## 🏗️ System Architecture

POE operates as a multi-agent system where a **Supervisor** orchestrates the flow of information between internal knowledge bases and the open web.

```mermaid
graph TD;
    A[User Input: Role & Seniority] --> B{LangGraph Supervisor};
    B --> C[Internal RAG Agent];
    B --> D[External Search Agent];
    C --> E[(Postgres + pgvector)];
    D --> F[YouTube/DuckDuckGo API];
    E --> G[Context Aggregator];
    F --> G;
    G --> H[GPT-5-Nano Architect];
    H --> I[30-Day Structured Curriculum];
    I --> J[Frontend Dashboard];

```

---

## 🛠️ Tech Stack

| Component            | Technology                       |
| -------------------- | -------------------------------- |
| **LLM Engine**       | OpenAI `gpt-5-nano`              |
| **Agent Framework**  | LangGraph                        |
| **Backend**          | FastAPI (Python)                 |
| **Database**         | Postgres with `pgvector`         |
| **Package Manager**  | `uv`                             |
| **Search Tools**     | DuckDuckGo, YouTube Video Search |
| **Containerization** | Podman                           |
| **Auth**             | JWT (JSON Web Tokens)            |

---

## 📂 Project Structure

This is a mono-repo designed for seamless deployment and development.

```text
proactive-onboarding-engine/
├── backend/          # FastAPI, LangGraph Agents, and pgvector logic
│   ├── app/          # Core application logic
│   ├── data/         # Ingestion scripts for internal docs
│   └── main.py       # API Entry point
├── frontend/         # React/Next.js UI Dashboard
│   ├── components/   # Interactive timeline and task lists
│   └── pages/        # Onboarding views
├── docker-compose.yml# Multi-container orchestration
└── README.md         # You are here

```

---

## 🚀 Getting Started

### Prerequisites

- **uv** (Python package manager)
- **Podman** or Docker
- OpenAI API Key

### Backend Setup

1. Navigate to the backend folder:

```bash
cd backend

```

2. Install dependencies using `uv`:

```bash
uv sync

```

3. Set up your environment variables in a `.env` file:

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/poe_db

```

4. Run the development server:

```bash
uv run uvicorn app.main:app --reload

```

### Frontend Setup

1. Navigate to the frontend folder and install dependencies:

```bash
cd frontend
npm install
npm run dev

```

---

## 💡 How it Works (The "Proactive" Logic)

Unlike traditional search engines, POE doesn't just return links. It:

1. **Identifies the Persona:** Determines if you are a "Junior Python Dev" or a "Senior DevOps Architect."
2. **Retrieves Tasks:** Searches internal docs for _how_ your specific team works.
3. **Fills Knowledge Gaps:** Finds the best external video tutorials for tools you haven't used before.
4. **Synthesizes:** Uses `gpt-5-nano` to create a logical sequence of learning, ensuring Day 1 doesn't overwhelm you with Day 30 concepts.

---

### ⚠️ THIS REPO IS UNDER DEVELOPMENT ⚠️
