import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export default function Dashboard() {
  const [stats, setStats] = useState({
    students: 0,
    classes: 0,
    assignments: 0,
    courses: 0,
  });
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.students(), api.classes(), api.assignments(), api.courses()])
      .then(([s, c, a, co]) =>
        setStats({
          students: s.count,
          classes: c.count,
          assignments: a.count,
          courses: co.count,
        }),
      )
      .catch((e: Error) => setError(e.message));
  }, []);

  const cards = [
    { label: "Students", value: stats.students, to: "/roster" },
    { label: "Classes", value: stats.classes, to: "/classes" },
    { label: "Assignments", value: stats.assignments, to: "/classes" },
    { label: "Courses", value: stats.courses, to: "/courses" },
  ];

  return (
    <div>
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
        <h1 className="text-2xl font-bold" data-testid="dashboard-hero">
          classroom-mcp
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          Roster, classes, courses and progress — managed over MCP, visible here.
        </p>
        <Link
          to="/roster"
          className="mt-4 inline-block rounded bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400"
          data-testid="dashboard-cta"
        >
          Open roster
        </Link>
      </div>
      {error && <p className="mt-4 text-sm text-red-400">Backend error: {error}</p>}
      <div className="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {cards.map((c) => (
          <Link
            key={c.label}
            to={c.to}
            className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 hover:border-zinc-600"
            data-testid={`kpi-${c.label.toLowerCase()}`}
          >
            <div className="text-3xl font-bold">{c.value}</div>
            <div className="text-sm text-zinc-400">{c.label}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
