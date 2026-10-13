import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function SettingsPage() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .status()
      .then((d) => setStatus(d as unknown as Record<string, unknown>))
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <div>
      <h1 className="text-xl font-bold" data-testid="settings-title">
        Settings
      </h1>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      {status ? (
        <dl className="mt-4 max-w-md space-y-2 text-sm" data-testid="settings-health">
          {Object.entries(status).map(([k, v]) => (
            <div key={k} className="flex justify-between border-b border-zinc-800 py-1">
              <dt className="text-zinc-400">{k}</dt>
              <dd className="font-mono">{String(v)}</dd>
            </div>
          ))}
        </dl>
      ) : (
        !error && <p className="mt-4 text-sm text-zinc-500">Loading…</p>
      )}
      <p className="mt-6 text-sm text-zinc-500">
        Configure via <code className="font-mono">.env</code> (see <code className="font-mono">.env.example</code>):{" "}
        <code className="font-mono">LEARNBOT_URL</code> for the learnbot-mcp lesson bridge, ports in{" "}
        <code className="font-mono">config</code>.
      </p>
    </div>
  );
}
