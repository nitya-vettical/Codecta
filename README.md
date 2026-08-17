# Codecta — Intelligent Code Reviewer

Codecta is an AI-powered code review application that analyzes user-submitted Python code for **correctness, safety, performance, and code quality**.

It combines traditional program analysis with sandboxed execution and LLM-generated feedback to provide a layered code-review experience.

##  Features

* **AST-based security validation**

  * Blocks unsafe constructs before execution
  * Detects imports and restricted operations
  * Detects obvious infinite loops such as `while True`

* **Sandboxed Python execution**

  * Runs submitted code in a separate process
  * Uses a restricted set of built-ins
  * Captures program output
  * Enforces an execution timeout

* **Execution insights**

  * Execution status
  * Execution time
  * Lines of code
  * Loop-depth heuristic

* **Static code analysis**

  * Undefined-variable detection
  * Unused-variable detection
  * Unreachable-code detection
  * Function-parameter and local-scope awareness

* **LLM-powered review**

  * Identifies potential bugs
  * Suggests readability improvements
  * Highlights performance concerns
  * Recommends coding best practices

* **Interactive web interface**

  * React + Vite frontend
  * Monaco-based code editor
  * Separate Execution, LLM, Static Analysis, and Security views

## Architecture

```text
                    ┌──────────────────┐
                    │   React / Vite   │
                    │   Code Editor    │
                    └────────┬─────────┘
                             │
                             │ POST /review
                             ▼
                    ┌──────────────────┐
                    │   Flask API      │
                    └────────┬─────────┘
                             │
                ┌────────────▼────────────┐
                │    AST Validation       │
                │   Security Checks       │
                └────────────┬────────────┘
                             │
                    Safe code only
                             │
                ┌────────────▼────────────┐
                │   Sandbox Executor      │
                │ Separate Process +      │
                │ Execution Timeout       │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │   Execution Metrics     │
                │ Time / LOC / Loop Hint  │
                └────────────┬────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     ┌─────────────────┐          ┌──────────────────┐
     │ Static Analysis │          │   Groq LLM        │
     │ Python AST      │          │ Code Review       │
     └────────┬────────┘          └────────┬─────────┘
              │                            │
              └──────────────┬─────────────┘
                             ▼
                    ┌──────────────────┐
                    │ JSON Response    │
                    │ → React UI       │
                    └──────────────────┘
```

## Review Pipeline

Codecta processes submitted code through multiple independent layers:

### 1. Request Intake

The Flask backend receives Python source code through:

```text
POST /review
```

Submitted code is treated as untrusted input.

### 2. AST Security Validation

The source code is parsed into a Python Abstract Syntax Tree.

Unsafe constructs are rejected before execution.

If validation fails:

```text
Code → Validator → BLOCKED
```

The sandbox is never started.

### 3. Sandboxed Execution

Validated code is executed in a separate process with:

* restricted built-ins
* isolated process execution
* captured output
* a hard execution timeout

This allows long-running or faulty programs to be terminated without blocking the Flask application.

### 4. Execution Metrics

Codecta calculates lightweight execution insights including:

* execution time
* lines of code
* loop-depth heuristic

The loop-depth value is an approximation intended to provide a quick performance hint rather than an exact Big-O proof.

### 5. Static Analysis

A custom AST-based analyzer checks for common code-quality issues such as:

* variables used before definition
* unused variables
* unreachable code
* function parameters and local scopes

### 6. LLM Review

The submitted source code is sent to a Groq-hosted LLM using:

```text
openai/gpt-oss-20b
```

The LLM produces human-readable feedback covering:

* bugs and logical issues
* performance
* readability
* maintainability
* best practices

The LLM is an **advisory layer**. Its output does not determine whether code is allowed to execute.

## Defense in Depth

Codecta deliberately separates safety decisions from AI-generated suggestions.

```text
                User Code
                    │
                    ▼
            AST Security Layer
                    │
          ┌─────────┴─────────┐
          │                   │
       Unsafe               Safe
          │                   │
       BLOCKED                 ▼
                      Sandboxed Process
                             │
                    ┌────────┴────────┐
                    │                 │
                 Success            Error/
                    │              Timeout
                    │                 │
                    └────────┬────────┘
                             ▼
                     Analysis + LLM
                             │
                             ▼
                         UI Output
```

This prevents an incorrect LLM recommendation from overriding the application's security checks.

## Tested Behavior

The application was tested locally with the following cases:

| Test                      | Expected Behavior                    | Result |
| ------------------------- | ------------------------------------ | ------ |
| Normal Python code        | Successful execution + review        | ✅      |
| `import os`               | Blocked before execution             | ✅      |
| Division by zero          | Runtime error captured               | ✅      |
| `while True`              | Infinite loop detected and blocked   | ✅      |
| Billion-iteration loop    | Sandbox timeout                      | ✅      |
| Valid function parameters | No false undefined-variable warnings | ✅      |
| Undefined variable        | Static analysis warning              | ✅      |
| Unreachable code          | Static analysis warning              | ✅      |

## Project Structure

```text
Codecta/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── test_request.py
│   │
│   ├── llm/
│   │   └── reviewer.py
│   │
│   ├── sandbox/
│   │   ├── executor.py
│   │   ├── validator.py
│   │   └── metrics.py
│   │
│   └── static_analysis/
│       └── analyzer.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── index.html
│
├── .gitignore
└── README.md
```

## Tech Stack

### Backend

* Python
* Flask
* Python AST
* `multiprocessing`
* Groq API
* `requests`

### Frontend

* React
* Vite
* Monaco Editor
* React Markdown

### Development

* Git / GitHub
* Python virtual environment
* npm

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/nitya-vettical/Codecta.git
cd Codecta
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```powershell
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure the Groq API key

Create `.env` from the example:

**Windows:**

```powershell
copy .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Then add:

```text
GROQ_API_KEY=your_api_key_here
```

Do not commit `.env` to Git.

### 4. Start the backend

From `backend/`:

```bash
python app.py
```

The Flask server runs on:

```text
http://127.0.0.1:5000
```

### 5. Start the frontend

Open a new terminal:

```bash
cd Codecta/frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, usually:

```text
http://localhost:5173
```

## Limitations

Codecta is an educational and experimental code-review system rather than a production-grade secure code execution platform.

Current limitations include:

* Python-only execution
* Process isolation is weaker than container or VM isolation
* Memory restrictions are not fully enforced
* Static analysis is intentionally lightweight
* Loop-depth analysis is heuristic
* Security validation cannot guarantee complete protection against every Python attack
* LLM output may contain incorrect or incomplete suggestions

## Future Improvements

Potential improvements include:

* Docker-based sandbox isolation
* Container-level CPU and memory limits
* More sophisticated AST/data-flow analysis
* Support for additional programming languages
* Automated test-case generation
* Code-diff and refactoring suggestions
* Persistent review history
* Authentication and multi-user support
* CI/CD integration

##  Design Goal

Codecta demonstrates how **static analysis, controlled execution, runtime information, and LLM reasoning can complement one another**.

Rather than relying entirely on either traditional rules or AI-generated feedback, Codecta separates these concerns into independent layers and combines their results into a single developer-facing review.
