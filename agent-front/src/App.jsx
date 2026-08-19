import { useEffect, useState } from "react";
import "./index.css";

const API_URL = "http://127.0.0.1:8000/agent";
const suggestionPrompts = [
  "Find software developer jobs in Johannesburg",
  "Show me junior product management roles in Cape Town",
  "Help me prepare for data analyst interviews",
];
const initialMessage = {
  id: 1,
  role: "assistant",
  text: "Hi, I’m CareerOps. Tell me the kind of role, location, or skills you’re targeting, and I’ll help you narrow it down.",
  jobs: [],
};

function escapeHtml(value = "") {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderInlineMarkdown(value = "") {
  let html = escapeHtml(value);

  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');

  return html;
}

function renderMarkdown(text = "") {
  if (!text) return "";

  const lines = text.split(/\n/);
  const html = [];
  let paragraph = [];
  let listType = null;
  let listItems = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      html.push(`<p>${renderInlineMarkdown(paragraph.join(" "))}</p>`);
      paragraph = [];
    }
  };

  const flushList = () => {
    if (!listType || !listItems.length) return;
    html.push(`<${listType}>${listItems.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("")}</${listType}>`);
    listItems = [];
    listType = null;
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    if (/^#{1,3}\s+/.test(line)) {
      flushParagraph();
      flushList();
      const level = line.match(/^#+/)[0].length;
      const content = line.replace(/^#{1,3}\s+/, "");
      html.push(`<h${Math.min(level, 3)}>${renderInlineMarkdown(content)}</h${Math.min(level, 3)}>`);
      continue;
    }

    if (/^[-*]\s+/.test(line)) {
      flushParagraph();
      if (listType !== "ul") {
        flushList();
        listType = "ul";
      }
      listItems.push(line.replace(/^[-*]\s+/, ""));
      continue;
    }

    if (/^\d+\.\s+/.test(line)) {
      flushParagraph();
      if (listType !== "ol") {
        flushList();
        listType = "ol";
      }
      listItems.push(line.replace(/^\d+\.\s+/, ""));
      continue;
    }

    if (/^>\s+/.test(line)) {
      flushParagraph();
      flushList();
      html.push(`<blockquote>${renderInlineMarkdown(line.replace(/^>\s+/, ""))}</blockquote>`);
      continue;
    }

    paragraph.push(line);
  }

  flushParagraph();
  flushList();

  return html.join("");
}

function extractJobsFromResponse(text = "") {
  if (!text) return [];

  const cleanText = text.replace(/\r/g, "");
  const jobBlocks = [...cleanText.matchAll(/Job\s+\d+:\s*[\s\S]*?(?=\n\s*Job\s+\d+:|$)/g)];

  return jobBlocks
    .map((match) => match[0])
    .map((block) => {
      const title = block.match(/Title:\s*(.+?)(?:\n|$)/)?.[1]?.trim();
      const company = block.match(/Company:\s*(.+?)(?:\n|$)/)?.[1]?.trim();
      const location = block.match(/Location:\s*(.+?)(?:\n|$)/)?.[1]?.trim();
      const salaryMin = block.match(/Salary minimum:\s*(.+?)(?:\n|$)/)?.[1]?.trim();
      const salaryMax = block.match(/Salary maximum:\s*(.+?)(?:\n|$)/)?.[1]?.trim();
      const employmentType = block.match(/Employment type:\s*(.+?)(?:\n|$)/)?.[1]?.trim();
      const matchScore = block.match(/Match score:\s*(.+?)(?:%|\n|$)/)?.[1]?.trim();
      const url = block.match(/Apply URL:\s*(.+?)(?:\n|$)/)?.[1]?.trim();
      const matchedSkills = block.match(/Matched skills:\s*(.+?)(?:\n|$)/)?.[1]?.trim();

      return {
        title: title || "Role not listed",
        company: company || "Company not listed",
        location: location || "Location not listed",
        salary: formatSalaryRange(salaryMin, salaryMax),
        matchScore: matchScore || "N/A",
        employmentType: employmentType || "Not specified",
        url: url || "#",
        matchedSkills: matchedSkills || "",
      };
    })
    .filter((job) => job.title || job.company || job.url);
}

function stripJobBlocksFromResponse(text = "") {
  if (!text) return "";

  return text
    .replace(/\r/g, "")
    .replace(/\n\s*Job\s+\d+:\s*[\s\S]*?(?=\n\s*Job\s+\d+:|$)/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function formatSalaryRange(minimum, maximum) {
  if (!minimum && !maximum) return "Salary not listed";

  const formatZar = (value) => {
    const numericValue = Number(value);
    if (!Number.isFinite(numericValue)) return value || "Not listed";
    return new Intl.NumberFormat("en-ZA", {
      style: "currency",
      currency: "ZAR",
      maximumFractionDigits: 0,
    }).format(numericValue);
  };

  if (minimum && maximum) {
    return `${formatZar(minimum)} - ${formatZar(maximum)}`;
  }

  if (minimum) {
    return `${formatZar(minimum)}+`;
  }

  return `Up to ${formatZar(maximum)}`;
}

function FrontendPage({ route, navigate }) {
  const [submitted, setSubmitted] = useState(false);
  const pageConfig = {
    "#demo": {
      eyebrow: "Talk to CareerOps",
      title: "Book a demo",
      description: "See how CareerOps can help your team find, develop, and retain great talent.",
      button: "Request Demo",
    },
    "#pricing": {
      eyebrow: "Plans for every stage",
      title: "Choose your CareerOps plan",
      description: "Start with the essentials and add the tools your career journey needs.",
      button: "Get started",
    },
    "#login": {
      eyebrow: "Welcome back",
      title: "Log in to CareerOps",
      description: "Continue working toward your next career move.",
      button: "Log in",
    },
    "#start": {
      eyebrow: "Start your journey",
      title: "Create your CareerOps account",
      description: "Get practical career guidance, job discovery, and skill support in one place.",
      button: "Start for Free",
    },
  };
  const config = pageConfig[route] || pageConfig["#demo"];

  if (route === "#pricing") {
    return (
      <section className="frontend-page pricing-page">
        <div className="frontend-heading">
          <p className="eyebrow">{config.eyebrow}</p>
          <h1>{config.title}</h1>
          <p>{config.description}</p>
        </div>
        <div className="pricing-grid">
          {[
            { name: "Free", price: "R0", features: ["Career assistant chat", "Basic job search", "Skill recommendations"], action: "Start free" },
            { name: "Pro", price: "R149", features: ["Everything in Free", "Personalized job matching", "Interview preparation"], action: "Choose Pro", featured: true },
            { name: "Business", price: "R499", features: ["Everything in Pro", "Team career insights", "Priority support"], action: "Choose Business" },
          ].map((plan) => (
            <article className={`plan-card ${plan.featured ? "featured" : ""}`} key={plan.name}>
              {plan.featured && <span className="plan-badge">Most popular</span>}
              <h2>{plan.name}</h2>
              <p className="plan-price">{plan.price}<small>{plan.name === "Free" ? " forever" : " / month"}</small></p>
              <ul>{plan.features.map((feature) => <li key={feature}>{feature}</li>)}</ul>
              <button type="button" className="page-button" onClick={() => navigate("#start")}>{plan.action}</button>
            </article>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="frontend-page form-page">
      <div className="frontend-heading">
        <p className="eyebrow">{config.eyebrow}</p>
        <h1>{config.title}</h1>
        <p>{config.description}</p>
      </div>
      {submitted ? (
        <div className="success-message">
          <strong>{route === "#login" ? "You are ready to log in." : "Thanks, you are all set."}</strong>
          <p>This frontend flow is ready. Backend account and booking connections can be added later.</p>
          <button type="button" className="text-button" onClick={() => navigate("#chat")}>Back to chat</button>
        </div>
      ) : (
        <form className="frontend-form" onSubmit={(event) => { event.preventDefault(); setSubmitted(true); }}>
          {route === "#demo" && <>
            <label>Name<input required name="name" type="text" /></label>
            <label>Email<input required name="email" type="email" /></label>
            <label>Company <span>(optional)</span><input name="company" type="text" /></label>
            <div className="form-row"><label>Preferred date<input required name="date" type="date" /></label><label>Preferred time<input required name="time" type="time" /></label></div>
            <label>Message<textarea name="message" rows="4" /></label>
          </>}
          {route === "#login" && <>
            <label>Email<input required name="email" type="email" /></label>
            <label>Password<input required name="password" type="password" /></label>
            <button type="button" className="text-button form-link">Forgot password?</button>
          </>}
          {route === "#start" && <>
            <label>Name<input required name="name" type="text" /></label>
            <label>Email<input required name="email" type="email" /></label>
            <label>Password<input required name="password" type="password" /></label>
          </>}
          <button type="submit" className="page-button">{config.button}</button>
          {route === "#login" && <p className="form-footer">Don&apos;t have an account? <button type="button" className="text-button" onClick={() => navigate("#start")}>Start for Free</button></p>}
        </form>
      )}
    </section>
  );
}

function App() {
  const [route, setRoute] = useState(window.location.hash || "#chat");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([initialMessage]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const handleHashChange = () => setRoute(window.location.hash || "#chat");
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (nextRoute) => {
    window.location.hash = nextRoute;
  };

  const handleNewChat = () => {
    setMessages([initialMessage]);
    setInput("");
    setError("");
  };

  const addAssistantMessage = (text) => {
    const jobs = extractJobsFromResponse(text);
    const safeText = stripJobBlocksFromResponse(text);

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: Date.now() + Math.random(),
        role: "assistant",
        text: safeText || "CareerOps returned no response.",
        jobs,
      },
    ]);
  };

  const sendMessage = async (nextMessage = input) => {
    const trimmed = nextMessage.trim();

    if (!trimmed || isLoading) return;

    const userMessage = {
      id: Date.now() + Math.random(),
      role: "user",
      text: trimmed,
      jobs: [],
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: trimmed }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || `Backend returned ${response.status}`);
      }

      const backendResponse = data.response || "CareerOps returned no response.";
      addAssistantMessage(backendResponse);
    } catch (fetchError) {
      console.error("CareerOps error:", fetchError);
      setError(`Unable to reach the CareerOps backend. ${fetchError.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-shell">
      <div className="background" />

      <aside className="sidebar">
        <div>
          <div className="brand-block">
            <div className="brand-mark">C</div>
            <div className="brand-copy">
              <span>CareerOps</span>
              <small>AI Career Assistant</small>
            </div>
          </div>

          <button type="button" className="new-chat-button" onClick={handleNewChat}>
            <span aria-hidden="true">+</span>
            New Chat
          </button>

          <nav className="side-nav" aria-label="Main navigation">
            <a className={`nav-item ${route === "#chat" ? "active" : ""}`} href="#chat">
              <span className="nav-icon" aria-hidden="true">⌂</span>
              Home
            </a>
            <a className="nav-item" href="#chat">
              <span className="nav-icon" aria-hidden="true">⌕</span>
              Job Search
            </a>
            <a className="nav-item" href="#chat">
              <span className="nav-icon" aria-hidden="true">✦</span>
              Career Skills
            </a>
          </nav>
        </div>

        <div className="sidebar-bottom">
          <nav className="utility-nav" aria-label="Account navigation">
            <a className={route === "#demo" ? "active" : ""} href="#demo">Book a Demo</a>
            <a className={route === "#pricing" ? "active" : ""} href="#pricing">Pricing</a>
            <a className={route === "#login" ? "active" : ""} href="#login">Login</a>
          </nav>
          <a className="sidebar-cta" href="#start">Start for Free <span aria-hidden="true">-&gt;</span></a>
          <div className="temporary-notice">
            <strong><span aria-hidden="true">!</span> Chats aren&apos;t saved</strong>
            <p>This conversation is temporary and won&apos;t be available when you return.</p>
          </div>
        </div>
      </aside>

      <main className="page-shell" id="chat">
        {route === "#chat" ? (
          <>
        <header className="mobile-topbar">
          <div className="brand-block">
            <div className="brand-mark">C</div>
            <span>CareerOps</span>
          </div>
        </header>

        <section className="chat-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">CareerOps</p>
              <h1>How can we help you today?</h1>
              <p className="panel-subtitle">Find the right role, build your skills, and move forward with confidence.</p>
            </div>
            <span className="status-pill"><span className="status-dot" /> Online</span>
          </div>

          <div className="message-list" aria-live="polite">
            {messages.map((message) => (
              <div key={message.id} className={`message-row ${message.role}`}>
                <div className={`message-bubble ${message.role}`}>
                  {message.role === "assistant" && message.jobs.length > 0 && (
                    <div className="job-grid">
                      {message.jobs.map((job) => (
                        <article className="job-card" key={`${message.id}-${job.title}-${job.company}`}>
                          <div className="job-header-row">
                            <div>
                              <h3>{job.title}</h3>
                              <p className="company-name">{job.company}</p>
                            </div>
                            <span className="match-pill">{job.matchScore}% match</span>
                          </div>

                          <div className="job-meta">
                            <span>{job.location}</span>
                            <span>{job.employmentType}</span>
                          </div>

                          <div className="salary-row">
                            <strong>Salary</strong>
                            <span>{job.salary}</span>
                          </div>

                          {job.matchedSkills && (
                            <p className="skill-summary">Recommended skills: {job.matchedSkills}</p>
                          )}

                          <div className="job-footer">
                            <a className="job-link" href={job.url} target="_blank" rel="noreferrer">
                              Apply now
                            </a>
                          </div>
                        </article>
                      ))}
                    </div>
                  )}

                  {message.text && (
                    <div
                      className="markdown-body"
                      dangerouslySetInnerHTML={{ __html: renderMarkdown(message.text) }}
                    />
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message-row assistant">
                <div className="message-bubble assistant loading-bubble" aria-live="polite">
                  <div className="typing-indicator" aria-label="CareerOps is responding">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="error-banner" role="alert">
                {error}
              </div>
            )}
          </div>

          <div className="composer">
            <div className="suggestion-row">
              {suggestionPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  className="suggestion-pill"
                  onClick={() => setInput(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>

            <div className="input-shell">
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask CareerOps about your next role, salary expectations, or skill gaps..."
                rows={4}
                disabled={isLoading}
              />

              <div className="composer-actions">
                <div className="assistant-badges">
                  <span>Career fit</span>
                  <span>Skills</span>
                  <span>Applications</span>
                </div>

                <button
                  type="button"
                  className="send-button"
                  onClick={() => sendMessage()}
                  disabled={isLoading || !input.trim()}
                >
                  {isLoading ? "Working..." : "Send"}
                </button>
              </div>
            </div>
          </div>
        </section>
          </>
        ) : (
          <FrontendPage route={route} navigate={navigate} />
        )}
      </main>
    </div>
  );
}

export default App;