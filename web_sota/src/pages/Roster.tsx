import { Trash2, UserPlus } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { type Student, api } from "../lib/api";

export default function Roster() {
  const [students, setStudents] = useState<Student[]>([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(
    () =>
      api
        .students()
        .then((d) => setStudents(d.students))
        .catch((e: Error) => setError(e.message)),
    [],
  );

  useEffect(() => {
    refresh();
  }, [refresh]);

  const create = () => {
    setError("");
    api
      .studentCreate({ name, email: email || undefined })
      .then((r) => {
        if (!r.success) setError(r.error ?? "Create failed");
        setName("");
        setEmail("");
        refresh();
      })
      .catch((e: Error) => setError(e.message));
  };

  const remove = (id: number) => {
    api
      .studentDelete(id)
      .then(() => refresh())
      .catch((e: Error) => setError(e.message));
  };

  return (
    <div>
      <h1 className="text-xl font-bold" data-testid="roster-title">
        Roster
      </h1>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      <div className="mt-4 flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Name"
          className="rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
          data-testid="roster-name"
        />
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email (optional)"
          className="rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
          data-testid="roster-email"
        />
        <button
          type="button"
          onClick={create}
          disabled={!name.trim()}
          className="flex items-center gap-1 rounded bg-amber-500 px-3 py-2 text-sm font-semibold text-black disabled:opacity-40"
          data-testid="roster-add"
        >
          <UserPlus size={16} /> Add
        </button>
      </div>
      {students.length === 0 ? (
        <p className="mt-6 text-sm text-zinc-500" data-testid="roster-empty">
          No students yet — add the first one above.
        </p>
      ) : (
        <table className="mt-4 w-full text-sm" data-testid="roster-table">
          <thead>
            <tr className="text-left text-zinc-400">
              <th className="py-2">Name</th>
              <th>Email</th>
              <th>Level</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {students.map((s) => (
              <tr key={s.id} className="border-t border-zinc-800">
                <td className="py-2">{s.name}</td>
                <td>{s.email ?? "-"}</td>
                <td>{s.level ?? "-"}</td>
                <td>{s.active ? "active" : "inactive"}</td>
                <td className="text-right">
                  <button
                    type="button"
                    onClick={() => remove(s.id)}
                    className="rounded p-1 text-zinc-500 hover:text-red-400"
                    aria-label={`Delete ${s.name}`}
                    data-testid={`roster-del-${s.id}`}
                  >
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
