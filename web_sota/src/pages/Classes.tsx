import { Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { type Assignment, type ClassItem, type Course, api } from "../lib/api";

export default function Classes({ coursesOnly = false }: { coursesOnly?: boolean }) {
  const [classes, setClasses] = useState<ClassItem[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(() => {
    api
      .classes()
      .then((d) => setClasses(d.classes))
      .catch((e: Error) => setError(e.message));
    api
      .courses()
      .then((d) => setCourses(d.courses))
      .catch((e: Error) => setError(e.message));
    api
      .assignments()
      .then((d) => setAssignments(d.assignments))
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const create = () => {
    setError("");
    api
      .classCreate({ name })
      .then((r) => {
        if (!r.success) setError(r.error ?? "Create failed");
        setName("");
        refresh();
      })
      .catch((e: Error) => setError(e.message));
  };

  const remove = (id: number) => {
    api
      .classDelete(id)
      .then(() => refresh())
      .catch((e: Error) => setError(e.message));
  };

  return (
    <div>
      <h1 className="text-xl font-bold" data-testid="classes-title">
        {coursesOnly ? "Courses" : "Classes & Assignments"}
      </h1>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}

      {!coursesOnly && (
        <>
          <div className="mt-4 flex gap-2">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Class name"
              className="rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
              data-testid="class-name"
            />
            <button
              type="button"
              onClick={create}
              disabled={!name.trim()}
              className="flex items-center gap-1 rounded bg-amber-500 px-3 py-2 text-sm font-semibold text-black disabled:opacity-40"
              data-testid="class-add"
            >
              <Plus size={16} /> Add class
            </button>
          </div>
          {classes.length === 0 ? (
            <p className="mt-6 text-sm text-zinc-500" data-testid="classes-empty">
              No classes yet.
            </p>
          ) : (
            <ul className="mt-4 space-y-2" data-testid="classes-list">
              {classes.map((c) => (
                <li
                  key={c.id}
                  className="flex items-center justify-between rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm"
                >
                  <span>
                    {c.name}
                    {c.subject && <span className="text-zinc-500"> — {c.subject}</span>}
                  </span>
                  <button
                    type="button"
                    onClick={() => remove(c.id)}
                    className="rounded p-1 text-zinc-500 hover:text-red-400"
                    aria-label={`Delete ${c.name}`}
                  >
                    <Trash2 size={16} />
                  </button>
                </li>
              ))}
            </ul>
          )}
          <h2 className="mt-8 text-lg font-semibold">Assignments</h2>
          {assignments.length === 0 ? (
            <p className="mt-2 text-sm text-zinc-500">No assignments yet.</p>
          ) : (
            <ul className="mt-2 space-y-2" data-testid="assignments-list">
              {assignments.map((a) => (
                <li key={a.id} className="rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm">
                  {a.title}
                  <span className="text-zinc-500">
                    {" "}
                    — max {a.max_score}
                    {a.due_date && ` — due ${a.due_date}`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}

      {(coursesOnly || !coursesOnly) && (
        <>
          {coursesOnly ? null : <h2 className="mt-8 text-lg font-semibold">Courses</h2>}
          {courses.length === 0 ? (
            <p className="mt-2 text-sm text-zinc-500" data-testid="courses-empty">
              No courses yet — create them via the `course_create` MCP tool.
            </p>
          ) : (
            <ul className="mt-2 space-y-2" data-testid="courses-list">
              {courses.map((c) => (
                <li key={c.id} className="rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm">
                  <span className="font-mono text-amber-400">{c.code}</span> {c.title}
                  {c.subject && <span className="text-zinc-500"> — {c.subject}</span>}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
