function App() {
  return (
    <div className="min-h-screen bg-obsidian text-primary flex items-center justify-center p-16">
      <div className="max-w-4xl w-full space-y-8">
        <div>
          <p className="section-label">00 — Theme Smoke Test</p>
          <h1 className="mt-2 text-4xl font-bold text-primary">VeloIQ</h1>
          <p className="mt-2 text-secondary">TÜV Rheinland Standards Automation Platform</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-surface border border-divider rounded p-6">
            <p className="section-label">Theme palette</p>
            <div className="mt-4 grid grid-cols-5 gap-2">
              <div className="h-10 bg-obsidian border border-divider" title="obsidian" />
              <div className="h-10 bg-surface border border-divider" title="surface" />
              <div className="h-10 bg-elevated" title="elevated" />
              <div className="h-10 bg-void border border-divider" title="void" />
              <div className="h-10 bg-divider" title="divider" />
            </div>
            <div className="mt-2 grid grid-cols-3 gap-2">
              <div className="h-10 bg-accent" title="accent" />
              <div className="h-10 bg-warn" title="warn" />
              <div className="h-10 bg-danger" title="danger" />
            </div>
          </div>

          <div className="bg-surface border border-divider rounded p-6">
            <p className="section-label">Confidence pills</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="pill text-accent bg-accent/10">0.984 · AUTO MATCH</span>
              <span className="pill text-warn bg-warn/10">0.840 · EXPERT REVIEW</span>
              <span className="pill text-danger bg-danger/10">0.620 · MANUAL TRIAGE</span>
            </div>
            <p className="section-label mt-6">Typography</p>
            <div className="mt-4 space-y-2">
              <p className="text-primary text-lg">Off-white heading — DM Sans</p>
              <p className="text-secondary">Warm gray body text — DM Sans 400</p>
              <p className="font-mono text-secondary">0.840 · TC-44210 · 2026-04-06</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
