export default function Help() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-xl font-bold" data-testid="help-title">
        Help
      </h1>
      <section className="mt-4">
        <h2 className="font-semibold">What is this?</h2>
        <p className="mt-1 text-sm text-zinc-400">
          classroom-mcp manages students, classes, courses, courseware, teaching agents and progress for distance
          learning. 45 MCP tools (roster, grading, AI syllabus generation) plus this REST dashboard on port 11105.
          Optional bridge to learnbot-mcp on 11101 for lesson content.
        </p>
      </section>
      <section className="mt-4">
        <h2 className="font-semibold">API / ports</h2>
        <ul className="mt-1 list-disc pl-5 text-sm text-zinc-400">
          <li>
            Backend <code className="font-mono">11105</code>: <code className="font-mono">/api/health</code>,{" "}
            <code className="font-mono">/api/status</code>, <code className="font-mono">/api/students</code>,{" "}
            <code className="font-mono">/api/classes</code>, <code className="font-mono">/api/assignments</code>,{" "}
            <code className="font-mono">/api/courses</code>, <code className="font-mono">/api/progress</code>,{" "}
            <code className="font-mono">/api/tools</code>, <code className="font-mono">/api/logs</code>
          </li>
          <li>
            Frontend dev <code className="font-mono">11106</code> (<code className="font-mono">bun run dev</code> in{" "}
            <code className="font-mono">web_sota/</code>, proxies <code className="font-mono">/api</code> to 11105)
          </li>
        </ul>
      </section>
      <section className="mt-4">
        <h2 className="font-semibold">Fixing common errors</h2>
        <ul className="mt-1 list-disc pl-5 text-sm text-zinc-400">
          <li>
            <code className="font-mono">GET / 404</code> — frontend not built. Run{" "}
            <code className="font-mono">bun run build</code> in <code className="font-mono">web_sota/</code> so{" "}
            <code className="font-mono">web_sota/dist/</code> exists.
          </li>
          <li>Blank email overwriting students — fixed in 0.2.0 (blank stores NULL).</li>
          <li>
            learnbot bridge failing — check <code className="font-mono">LEARNBOT_URL</code> points at a live
            learnbot-mcp (default <code className="font-mono">http://127.0.0.1:11101</code>).
          </li>
        </ul>
      </section>
      <section className="mt-4">
        <h2 className="font-semibold">FAQ</h2>
        <p className="mt-1 text-sm text-zinc-400">
          MCP server (stdio): <code className="font-mono">uv run python -m classroom_mcp</code>. REST daemon:{" "}
          <code className="font-mono">uv run python -m classroom_mcp.api</code> or{" "}
          <code className="font-mono">.\start.ps1</code>. Tests:{" "}
          <code className="font-mono">uv run pytest tests\ -q</code>.
        </p>
      </section>
    </div>
  );
}
