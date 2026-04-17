export type Project = { slug: string };
export type ProjectListResponse = { projects: Project[] };
export type FileTreeEntry = { path: string; size: number };
export type FileTreeResponse = { files: FileTreeEntry[] };
export type FileReadResponse = { path: string; content: string };

export type ProjectStatsResponse = {
  artifacts: Record<string, boolean>;
  counts: { papers_total: number; decisions_total: number; included_count: number };
};

export type ToolRunResponse = {
  ok: boolean;
  returncode: number;
  stdout: string;
  stderr: string;
};

export type PdfEntry = { paper_id: string; filename: string; size: number };

async function jsonFetch<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const res = await fetch(input, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => jsonFetch<{ ok: boolean }>("/api/health"),
  listProjects: () => jsonFetch<ProjectListResponse>("/api/projects"),
  createProject: (slug: string) => jsonFetch<{ ok: boolean }>(`/api/projects`, { method: "POST", body: JSON.stringify({ slug }) }),
  tree: (slug: string) => jsonFetch<FileTreeResponse>(`/api/projects/${encodeURIComponent(slug)}/tree`),
  readFile: (slug: string, path: string) =>
    jsonFetch<FileReadResponse>(`/api/projects/${encodeURIComponent(slug)}/file?path=${encodeURIComponent(path)}`),
  writeFile: (slug: string, path: string, content: string) =>
    jsonFetch<{ ok: boolean }>(`/api/projects/${encodeURIComponent(slug)}/file?path=${encodeURIComponent(path)}`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    }),
  stats: (slug: string) => jsonFetch<ProjectStatsResponse>(`/api/projects/${encodeURIComponent(slug)}/stats`),
  runPhase1: (slug: string) => jsonFetch<ToolRunResponse>(`/api/projects/${encodeURIComponent(slug)}/phase1/run`, { method: "POST" }),
  listPdfs: (slug: string) => jsonFetch<{ pdfs: PdfEntry[] }>(`/api/projects/${encodeURIComponent(slug)}/pdfs`),
  uploadPdf: async (slug: string, paperId: string, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`/api/projects/${encodeURIComponent(slug)}/pdfs/${encodeURIComponent(paperId)}`, { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    return (await res.json()) as { ok: boolean };
  },
  runPhase2: (slug: string, topN = 10) =>
    jsonFetch<ToolRunResponse>(`/api/projects/${encodeURIComponent(slug)}/phase2/run?top_n=${encodeURIComponent(String(topN))}`, { method: "POST" }),
  runPhase3: (slug: string) => jsonFetch<ToolRunResponse>(`/api/projects/${encodeURIComponent(slug)}/phase3/run`, { method: "POST" }),
  runPhase4: (slug: string) => jsonFetch<ToolRunResponse>(`/api/projects/${encodeURIComponent(slug)}/phase4/run`, { method: "POST" }),
  runRubric: (slug: string) => jsonFetch<ToolRunResponse>(`/api/projects/${encodeURIComponent(slug)}/rubric/check`, { method: "POST" }),
};
