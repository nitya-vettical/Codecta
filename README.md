# Codecta — Intelligent Code Reviewer

Codecta is an intelligent backend system that reviews user-submitted Python code for
**correctness, safety, performance, and best practices**.

It combines:
- Static analysis (AST-based)
- Secure sandboxed execution
- Execution insights
- LLM-powered code review

Codecta is designed to resemble how real-world developer tools reason about code,
while ensuring untrusted code is handled safely.

---

## Why Codecta?

Modern code review tools either:
- rely purely on static rules, or
- blindly trust AI-generated feedback

Codecta bridges this gap by:
- validating code safety before execution
- executing code in a controlled sandbox
- surfacing runtime insights
- augmenting analysis with an LLM reviewer

---

## Key Capabilities

- Static safety validation using Python AST
- Sandboxed execution with strict time limits
- Restricted execution environment
- Runtime insights (execution time, loop depth, LOC)
- LLM-based human-readable code review

---

## High-Level Architecture

Codecta processes code in **clearly separated stages**:

1. Request handling
2. Static validation
3. Sandbox execution
4. Execution insights
5. LLM review

Each stage is isolated to ensure safety, clarity, and extensibility.

## Architecture Flow

Codecta follows a strict, layered processing pipeline to ensure safety and clarity.

### 1. Request Intake
The backend receives Python source code via a REST API.
The code is treated as untrusted input from the start.

### 2. Static Validation (AST-Based)
Before any execution, the code is parsed into an Abstract Syntax Tree (AST).
Unsafe constructs such as imports, dynamic execution, reflection, and infinite loops
are detected and blocked at this stage.

If validation fails, execution is skipped entirely.

### 3. Sandboxed Execution
Validated code is executed inside a restricted sandbox:
- Runs in a separate OS process
- Enforces a hard execution timeout
- Uses a limited set of safe built-ins
- Captures standard output safely

This prevents untrusted code from affecting the host system.

### 4. Execution Insights
After execution, Codecta computes lightweight runtime insights:
- Execution time
- Lines of code
- Loop nesting depth (Big-O style hint)

These insights help reason about performance characteristics.

### 5. LLM-Based Code Review
Finally, the original source code is reviewed by an LLM.
The model provides human-readable feedback on:
- potential bugs
- readability
- maintainability
- performance concerns

LLM output does not influence execution or safety decisions.

## Project Structure

backend/
├── app.py # Flask API entry point
│
├── sandbox/ # Secure execution layer
│ ├── executor.py # Process-based sandbox execution
│ ├── validator.py # AST-based static safety validation
│ └── metrics.py # Execution insights (loop depth, etc.)
│
├── llm/ # LLM integration
│ └── reviewer.py # AI-powered code review
│
├── test_request.py # Local API testing script
│
└── venv/ # Python virtual environment

## Tech Stack

- **Language:** Python 3
- **API Framework:** Flask
- **Static Analysis:** Python AST
- **Sandboxing:** multiprocessing (process isolation)
- **LLM Provider:** Groq (LLaMA 3)
- **Testing:** Python `requests`
- **Environment Management:** venv

Each component is intentionally decoupled to keep the system
safe, testable, and extensible.

## Getting Started

Follow these instructions to run the project locally.

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd intelligent-code-reviewer
```

### 2. Backend Setup
The backend requires Python 3.
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set up your environment variables:
1. Copy `.env.example` to `.env`.
2. Add your Groq API key to the `.env` file.
```bash
cp .env.example .env
```

Start the backend server:
```bash
python app.py
```
The backend should now run on `http://localhost:5000`.

### 3. Frontend Setup
The frontend uses Vite and React. In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
The frontend should now run on the port provided by Vite (usually `http://localhost:5173`).

## Safety and Design Decisions

Codecta is designed with a defense-in-depth approach when handling untrusted code.

### Static Safety Before Execution
All submitted code is validated using Python's Abstract Syntax Tree (AST)
before any execution occurs. This allows Codecta to block unsafe constructs
such as imports, dynamic execution, reflection, and infinite loops
without running the code.

### Process-Based Isolation
Code execution occurs in a separate OS process using Python's
`multiprocessing` module. This ensures that misbehaving code can be
terminated safely without affecting the main application.

### Restricted Execution Environment
User code executes with a tightly controlled set of built-in functions.
Access to file I/O, networking, environment variables, and system calls
is intentionally unavailable.

### Hard Time Limits
Each execution is subject to a strict timeout. If the code exceeds
the allowed runtime, the process is terminated immediately.

### LLM as an Advisory Layer
The LLM-based code review is intentionally isolated from safety decisions.
LLM output is treated as advisory feedback only and does not influence
validation or execution logic.

This separation prevents hallucinations or incorrect suggestions
from impacting system safety.

## Limitations and Future Improvements

Codecta is intentionally scoped as a backend-focused system.
Some limitations are acknowledged by design.

### Current Limitations
- The sandbox is Python-specific and does not yet support other languages
- Memory limits are best-effort and platform-dependent
- Static analysis rules are conservative and may block some valid programs
- Execution insights are heuristic-based, not exact complexity analysis

### Future Improvements
- Docker-based sandboxing for stronger isolation
- Per-execution memory limits enforced at the container level
- Support for additional programming languages
- More granular static analysis rules
- Before-and-after refactoring previews
- Frontend UI for interactive code review

These improvements are intentionally deferred to keep the current system
focused, understandable, and secure.
