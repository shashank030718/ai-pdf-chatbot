
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_URL = "/api";
const MAX_FILE_SIZE = 10 * 1024 * 1024;

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [uploadedFilename, setUploadedFilename] = useState("");

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    setSelectedFile(null);
    setUploadMessage("");
    setUploadError("");

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadError("Please select a PDF file.");
      event.target.value = "";
      return;
    }

    if (file.size === 0 || file.size > MAX_FILE_SIZE) {
      setUploadError(
        file.size === 0
          ? "This file is empty."
          : "PDF size must be 10 MB or less."
      );
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  }

  async function handleUpload() {
    if (!selectedFile || uploading || loading) return;

    setUploading(true);
    setUploadMessage("");
    setUploadError("");
    setError("");
    setAnswer("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setUploadedFilename(data.filename);
      setUploadMessage(`${data.chunks} text chunks indexed successfully.`);
      setSelectedFile(null);
    } catch (err) {
      setUploadError(err.message || "Could not upload the PDF.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(event) {
    event.preventDefault();

    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || loading || uploading) return;

    setLoading(true);
    setAnswer("");
    setError("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmedQuestion }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not generate an answer.");
      }

      setAnswer(data.answer);
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="topbar">
        <a className="brand" href="/" aria-label="PDF AI home">
          <span className="brand-icon">P</span>
          <span>PDF<span className="brand-accent"> AI</span></span>
        </a>
        <span className="topbar-label">DOCUMENT ASSISTANT</span>
      </header>

      <section className="workspace">
        <div className="page-heading">
          <span className="eyebrow">YOUR AI READING SPACE</span>
          <h1>Chat with your PDF<span>.</span></h1>
          <p>Upload a document. Ask anything.</p>
        </div>

        <section className="panel upload-panel">
          <div className="panel-heading">
            <div className="step-icon">01</div>
            <div>
              <h2>Your document</h2>
              <p>PDF format · Maximum 10 MB</p>
            </div>
          </div>

          <label className="dropzone" htmlFor="pdf-file">
            <span className="pdf-icon">PDF</span>
            <span className="dropzone-copy">
              <strong>
                {selectedFile ? selectedFile.name : "Choose a PDF to upload"}
              </strong>
              <small>
                {selectedFile
                  ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB`
                  : "Select a file from your computer"}
              </small>
            </span>
            <span className="browse-label">Browse</span>
          </label>

          <input
            id="pdf-file"
            className="file-input"
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            disabled={uploading || loading}
          />

          <button
            className="primary-button upload-button"
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || uploading || loading}
          >
            {uploading ? "Processing document..." : "Upload document"}
            {!uploading && <span aria-hidden="true">↑</span>}
          </button>

          {uploading && (
            <p className="notice" role="status">
              Extracting text and building the search index...
            </p>
          )}

          {uploadMessage && (
            <p className="notice success" role="status">
              <span>✓</span> {uploadMessage}
            </p>
          )}

          {uploadError && (
            <p className="notice error" role="alert">{uploadError}</p>
          )}

          {uploadedFilename && (
            <div className="active-file">
              <span className="active-dot" />
              <span className="active-file-name">{uploadedFilename}</span>
              <span className="active-label">Ready</span>
            </div>
          )}
        </section>

        <section className="panel question-panel">
          <div className="panel-heading">
            <div className="step-icon">02</div>
            <div>
              <h2>Ask your document</h2>
              <p>Get answers based on its content</p>
            </div>
          </div>

          <form onSubmit={handleAsk}>
            <label className="sr-only" htmlFor="question">
              Your question
            </label>
            <textarea
              id="question"
              className="question-input"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="What would you like to know?"
              rows={3}
              maxLength={2000}
              required
            />

            <div className="question-footer">
              <span className="character-count">
                {question.length}/2000
              </span>
              <button
                className="primary-button ask-button"
                type="submit"
                disabled={loading || uploading || !question.trim()}
              >
                {loading ? "Thinking..." : "Ask AI"}
                {!loading && <span aria-hidden="true">↗</span>}
              </button>
            </div>
          </form>

          {loading && (
            <p className="notice" role="status">
              Searching your document...
            </p>
          )}

          {error && <p className="notice error" role="alert">{error}</p>}

          {answer && (
            <section className="answer-panel" aria-live="polite">
              <div className="answer-heading">
                <span className="answer-sparkle">✳</span>
                <h2>Answer</h2>
              </div>
              <div className="markdown-answer">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
            </section>
          )}
        </section>

        <footer className="page-footer">
          Built with React · FastAPI · FAISS · Gemini
        </footer>
      </section>
    </main>
  );
}

export default App;
