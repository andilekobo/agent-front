import "./index.css";

function App() {
  return (
    <div className="app">
      {/* Background */}
      <div className="background" />

      {/* Main content */}
      <main className="page">

        {/* Navbar */}
        <nav className="navbar">
          <div className="logo">CareerOps</div>

          <div className="nav-links right-links">
            <a href="#">Book a demo</a>
            <a href="#">Pricing</a>
            <a href="#">Login</a>
            <button className="free-btn">Start for FREE</button>
          </div>
        </nav>

        {/* Hero */}
        <section className="hero">
          <div className="agent-header">CareerOps</div>

          <div className="agent-subtitle">Job Application</div>

          {/* Agent prompt */}
          <div className="agent-box">
            <textarea
              placeholder="Type your request..."
            />

            <div className="agent-controls">
              <div className="left-controls">
                <button className="icon-btn">◉</button>
                <button className="icon-btn">ϟ</button>
              </div>

              <button className="send-btn">
                ➤
              </button>
            </div>
          </div>

          <div className="powered-by">
            Powered by Claude · Anthropic
          </div>
        </section>

      </main>
    </div>
  );
}

export default App;