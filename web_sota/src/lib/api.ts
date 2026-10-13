export interface Student {
  id: number;
  name: string;
  email: string | null;
  active: number;
  language: string | null;
  level: string | null;
}

export interface ClassItem {
  id: number;
  name: string;
  subject: string | null;
  student_count?: number;
}

export interface Assignment {
  id: number;
  class_id: number;
  title: string;
  due_date: string | null;
  max_score: number;
}

export interface Course {
  id: number;
  code: string;
  title: string;
  subject: string | null;
  level: string | null;
  credits: number | null;
}

export interface McpTool {
  name: string;
  description: string;
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return (await r.json()) as T;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return (await r.json()) as T;
}

async function del<T>(path: string): Promise<T> {
  const r = await fetch(path, { method: "DELETE" });
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return (await r.json()) as T;
}

export const api = {
  students: () => get<{ students: Student[]; count: number }>("/api/students"),
  studentCreate: (body: { name: string; email?: string }) =>
    post<{ success: boolean; id?: number; error?: string }>("/api/students", body),
  studentDelete: (id: number) => del<{ success: boolean }>(`/api/students/${id}`),
  classes: () => get<{ classes: ClassItem[]; count: number }>("/api/classes"),
  classCreate: (body: { name: string; subject?: string }) =>
    post<{ success: boolean; id?: number; error?: string }>("/api/classes", body),
  classDelete: (id: number) => del<{ success: boolean }>(`/api/classes/${id}`),
  assignments: () => get<{ assignments: Assignment[]; count: number }>("/api/assignments"),
  courses: () => get<{ courses: Course[]; count: number }>("/api/courses"),
  progress: () => get<{ records: unknown[]; count: number }>("/api/progress"),
  tools: () => get<{ tools: McpTool[]; count: number }>("/api/tools"),
  status: () =>
    get<{
      status: string;
      version: string;
      uptime_seconds: number;
      backend_port: number;
      frontend_port: number;
      tool_count: number;
    }>("/api/status"),
};
