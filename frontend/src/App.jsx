import { useState } from "react";
import Editor from "@monaco-editor/react";
import ReactMarkdown from "react-markdown";

function App() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("execution");

  const handleReview = async () => {
    if (!code.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:5000/review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: "Failed to connect to backend" });
    } finally {
      setLoading(false);
    }
  };

  const renderTabContent = () => {
    if (!result) return null;

    if (activeTab === "execution") {
      if (result.allowed === false) {
        return (
          <div className="blocked-state">
            <h4>🚫 Execution Blocked</h4>
            <p>{result.reason}</p>
          </div>
        );
      }

      const exec = result.execution;


      return (
        <div className="exec-section">
          <div className="exec-meta">
            <span className={`status ${exec.status}`}>
              Status: {exec.status}
            </span>
            <span>⏱ {exec.execution_time_ms} ms</span>
            <span>📄 {exec.lines_of_code} lines</span>
            <span>📊 {exec.loop_depth_hint}</span>
          </div>

          {exec.output && (
            <>
              <h4>Output</h4>
              <pre className="exec-box">{exec.output}</pre>
            </>
          )}

          {exec.error && (
            <>
              <h4>Error</h4>
              <pre className="exec-error">{exec.error}</pre>
            </>
          )}
        </div>
      );
    }

    if (activeTab === "llm") {
      // If code was blocked, LLM review is intentionally skipped
      if (result.allowed === false) {
        return (
          <div className="blocked-state">
            <h4>🚫 LLM Review Skipped</h4>
            <p>Code was blocked during validation.</p>
          </div>
        );
      }

      if (!result.llm_review) {
        return <p>No LLM feedback available.</p>;
      }

      return (
        <div className="llm-section">
          <ReactMarkdown>{result.llm_review}</ReactMarkdown>
        </div>
      );
    }


    if (activeTab === "static") {
      // If code was blocked, static validation is what failed
      if (result.allowed === false) {
        return (
          <div className="blocked-state">
            <h4>🚨 Static Analysis Failed</h4>
            <p>{result.reason}</p>
          </div>
        );
      }

      const staticData = result.static_analysis;

      if (!staticData) {
         return <p>No static analysis data returned.</p>;
      }

      return (
        <div className="static-section">
          <h4>Complexity</h4>
          <p>Estimated Loop Depth: {result.execution?.loop_depth_hint}</p>

          <h4>Unused Variables</h4>
          {staticData.unused_variables && staticData.unused_variables.length > 0 ? (
             <ul>
               {staticData.unused_variables.map((v, i) => <li key={i}>{v}</li>)}
             </ul>
          ) : (
             <p>No unused variables detected.</p>
          )}
          
          <h4>Issues</h4>
          {staticData.issues && staticData.issues.length > 0 ? (
             <ul>
               {staticData.issues.map((issue, i) => <li key={i}>{issue}</li>)}
             </ul>
          ) : (
             <p>No static issues detected.</p>
          )}
        </div>
      );
    }


    if (activeTab === "security") {
      const blocked = result.allowed === false;

      return (
        <div className="security-section">
          <div className={`security-status ${blocked ? "blocked" : "safe"}`}>
            {blocked ? "❌ BLOCKED" : "✅ SAFE"}
          </div>

          {blocked && result.reason && (
            <pre className="security-reason">{result.reason}</pre>
          )}

          {!blocked && (
            <p>No unsafe constructs detected during validation.</p>
          )}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Codecta</h1>
        <span className="tagline">Intelligent Code Reviewer</span>
      </header>

      <main className="main">
        {/* LEFT */}
        <section className="editor">
          <h2>Code Input</h2>

          <div className="code-editor-container" style={{ height: "400px", border: "1px solid #2a2f3a", borderRadius: "6px", overflow: "hidden" }}>
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || "")}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                padding: { top: 16 }
              }}
            />
          </div>

          <button
            className="review-btn"
            onClick={handleReview}
            disabled={loading || !code.trim()}
          >
            {loading ? "Reviewing…" : "Review Code"}
          </button>
        </section>

        {/* RIGHT */}
        <section className="results">
          <h2>Review Output</h2>

          <div className="tabs">
            {["execution", "llm", "static", "security"].map((tab) => (
              <button
                key={tab}
                className={`tab-btn ${activeTab === tab ? "active" : ""}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab.toUpperCase()}
              </button>
            ))}
          </div>

          {!result && !loading && (
            <div className="placeholder">
              Paste code on the left and click <strong>Review Code</strong>
            </div>
          )}

          {result && <div className="result-box">{renderTabContent()}</div>}

          {loading && <div className="loading-overlay">Reviewing code…</div>}
        </section>
      </main>
    </div>
  );
}

export default App;
