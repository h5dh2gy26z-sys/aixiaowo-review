<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import Papa from "papaparse";
import YAML from "yaml";
import { api, type FileTreeEntry, type PdfEntry, type ProjectStatsResponse, type ToolRunResponse } from "./api";

type Mode = "workbench" | "files";

const loading = ref(true);
const busyMsg = ref<string | null>(null);
const errorMsg = ref<string | null>(null);

const projects = ref<{ slug: string }[]>([]);
const selectedProject = ref<string>("");
const newSlug = ref("demo_survey_web_2");

const mode = ref<Mode>("workbench");

const files = ref<FileTreeEntry[]>([]);
const fileQuery = ref("");
const selectedPath = ref("");
const editorContent = ref("");
const dirty = ref(false);

const logTitle = ref("输出");
const logText = ref("就绪。");

const stats = ref<ProjectStatsResponse | null>(null);
const pdfs = ref<PdfEntry[]>([]);
const phase2TopN = ref(10);
const tracePreview = ref("");

const PAPERS_COLS = [
  "paper_id",
  "title",
  "year",
  "authors",
  "venue",
  "abstract",
  "keywords",
  "doi",
  "url",
  "source_database",
] as const;
type PaperRow = Record<(typeof PAPERS_COLS)[number], string>;

const DECISION_COLS = ["paper_id", "decision", "reason_tag", "notes"] as const;
type DecisionRow = Record<(typeof DECISION_COLS)[number], string>;

const papers = ref<PaperRow[]>([]);
const decisionsById = ref<Record<string, DecisionRow>>({});

const taxonomyPreview = ref("");
const outlinePreview = ref("");

const filteredFiles = computed(() => {
  const q = fileQuery.value.trim().toLowerCase();
  if (!q) return files.value;
  return files.value.filter((f) => f.path.toLowerCase().includes(q));
});

const includedCount = computed(() => {
  return Object.values(decisionsById.value).filter((d) => (d.decision || "").toLowerCase() === "include").length;
});

const pdfCount = computed(() => pdfs.value.length);
const paperCardsCount = computed(
  () => files.value.filter((f) => f.path.startsWith("05_evidence/paper_cards/") && f.path.endsWith(".json")).length
);
const includedPapers = computed(() =>
  papers.value.filter((p) => (decisionsById.value[p.paper_id]?.decision || "").toLowerCase() === "include")
);
const firstPaperCardPath = computed(() => {
  const hit = files.value.find((f) => f.path.startsWith("05_evidence/paper_cards/") && f.path.endsWith(".json"));
  return hit?.path ?? "";
});

function hasPdf(paperId: string): boolean {
  return pdfs.value.some((p) => p.paper_id === paperId);
}

function setError(e: unknown) {
  errorMsg.value = e instanceof Error ? e.message : String(e);
}

function emptyPaperRow(): PaperRow {
  const row = {} as PaperRow;
  for (const c of PAPERS_COLS) row[c] = "";
  return row;
}

function emptyDecisionRow(paperId: string): DecisionRow {
  return { paper_id: paperId, decision: "", reason_tag: "", notes: "" };
}

function parseCsvRows<T extends Record<string, string>>(content: string): { rows: T[]; fields: string[] } {
  const parsed = Papa.parse<Record<string, unknown>>(content, { header: true, skipEmptyLines: "greedy" });
  if (parsed.errors?.length) throw new Error(parsed.errors[0]?.message || "CSV parse error");
  const fields = (parsed.meta.fields || []).map((f) => String(f));
  const rows = (parsed.data || []).map((r) => {
    const out: Record<string, string> = {};
    for (const k of fields) out[k] = String((r as any)?.[k] ?? "");
    return out as T;
  });
  return { rows, fields };
}

function toCsv<T extends Record<string, string>>(rows: T[], columns: readonly string[]): string {
  const clean = rows
    .map((r) => {
      const out: Record<string, string> = {};
      for (const c of columns) out[c] = (r[c] ?? "").toString();
      return out;
    })
    .filter((r) => Object.values(r).some((v) => (v ?? "").toString().trim() !== ""));
  return Papa.unparse(clean, { columns: [...columns] });
}

async function refreshProjects(selectFirst = true) {
  const res = await api.listProjects();
  projects.value = res.projects;
  if (selectFirst && !selectedProject.value && projects.value.length > 0) {
    selectedProject.value = projects.value[0].slug;
  }
}

async function refreshTree() {
  if (!selectedProject.value) return;
  const res = await api.tree(selectedProject.value);
  files.value = res.files;
  if (!selectedPath.value) {
    const preferred = [
      "00_project.yaml",
      "02_import/papers_canonical.csv",
      "03_screening/abstract_decisions.csv",
      "04_taxonomy/taxonomy.yaml",
      "06_draft/00_outline.md",
    ];
    const hit = preferred.find((p) => files.value.some((f) => f.path === p));
    selectedPath.value = hit ?? (files.value[0]?.path ?? "");
  }
}

async function refreshPdfs() {
  if (!selectedProject.value) return;
  const res = await api.listPdfs(selectedProject.value);
  pdfs.value = res.pdfs;
}

async function loadFile(path: string) {
  if (!selectedProject.value) return;
  if (dirty.value && !confirm("当前文件未保存，确定切换吗？")) return;
  selectedPath.value = path;
  const res = await api.readFile(selectedProject.value, path);
  editorContent.value = res.content;
  dirty.value = false;
  errorMsg.value = null;
}

async function saveFile() {
  if (!selectedProject.value || !selectedPath.value) return;
  await api.writeFile(selectedProject.value, selectedPath.value, editorContent.value);
  dirty.value = false;
  logTitle.value = "保存";
  logText.value = `已保存: ${selectedPath.value}`;
}

function showRun(title: string, r: ToolRunResponse) {
  logTitle.value = title + (r.ok ? " (OK)" : " (FAIL)");
  logText.value = [r.stdout?.trim(), r.stderr?.trim()].filter(Boolean).join("\n\n") || "(no output)";
}

async function loadWorkbenchOutputs() {
  if (!selectedProject.value) return;
  taxonomyPreview.value = "";
  outlinePreview.value = "";
  tracePreview.value = "";

  try {
    const tax = await api.readFile(selectedProject.value, "04_taxonomy/taxonomy.yaml");
    const doc = YAML.parse(tax.content) as any;
    const children = doc?.nodes?.[0]?.children ?? [];
    const lines = ["Taxonomy nodes (root children):"];
    for (const n of children) {
      if (!n?.id) continue;
      lines.push(`- ${n.id}: ${n.name ?? ""}`);
    }
    taxonomyPreview.value = lines.join("\n");
  } catch {
    taxonomyPreview.value = "";
  }

  try {
    const outline = await api.readFile(selectedProject.value, "06_draft/00_outline.md");
    outlinePreview.value = outline.content;
  } catch {
    outlinePreview.value = "";
  }

  try {
    const tr = await api.readFile(selectedProject.value, "07_quality/traceability_report.md");
    tracePreview.value = tr.content;
  } catch {
    tracePreview.value = "";
  }
}

async function loadWorkbenchData() {
  if (!selectedProject.value) return;
  busyMsg.value = "加载项目中...";
  try {
    stats.value = await api.stats(selectedProject.value);

    try {
      const file = await api.readFile(selectedProject.value, "02_import/papers_canonical.csv");
      const parsed = parseCsvRows<Record<string, string>>(file.content);
      papers.value = parsed.rows.map((r) => {
        const out = emptyPaperRow();
        for (const c of PAPERS_COLS) out[c] = (r[c] ?? "").toString();
        return out;
      });
    } catch {
      papers.value = [];
    }

    try {
      const file = await api.readFile(selectedProject.value, "03_screening/abstract_decisions.csv");
      const parsed = parseCsvRows<Record<string, string>>(file.content);
      const map: Record<string, DecisionRow> = {};
      for (const r of parsed.rows) {
        const pid = (r.paper_id ?? "").toString().trim();
        if (!pid) continue;
        map[pid] = {
          paper_id: pid,
          decision: (r.decision ?? "").toString(),
          reason_tag: (r.reason_tag ?? "").toString(),
          notes: (r.notes ?? "").toString(),
        };
      }
      decisionsById.value = map;
    } catch {
      decisionsById.value = {};
    }

    await refreshTree();
    await refreshPdfs();
    await loadWorkbenchOutputs();
  } finally {
    busyMsg.value = null;
  }
}

async function savePapers() {
  if (!selectedProject.value) return;
  busyMsg.value = "保存论文中...";
  try {
    const csv = toCsv(papers.value, PAPERS_COLS);
    await api.writeFile(selectedProject.value, "02_import/papers_canonical.csv", csv + "\n");
    await loadWorkbenchData();
    logTitle.value = "论文导入";
    logText.value = "已保存: 02_import/papers_canonical.csv";
  } finally {
    busyMsg.value = null;
  }
}

async function saveDecisions() {
  if (!selectedProject.value) return;
  busyMsg.value = "保存筛选结果中...";
  try {
    const rows: DecisionRow[] = papers.value
      .map((p) => p.paper_id.trim())
      .filter(Boolean)
      .map((pid) => decisionsById.value[pid] ?? emptyDecisionRow(pid));
    const csv = toCsv(rows, DECISION_COLS);
    await api.writeFile(selectedProject.value, "03_screening/abstract_decisions.csv", csv + "\n");
    await loadWorkbenchData();
    logTitle.value = "摘要筛选";
    logText.value = "已保存: 03_screening/abstract_decisions.csv";
  } finally {
    busyMsg.value = null;
  }
}

function addPaperRow() {
  papers.value = [...papers.value, emptyPaperRow()];
}

function removePaperRow(idx: number) {
  const row = papers.value[idx];
  if (!row) return;
  const pid = (row.paper_id || "").trim();
  if (pid && decisionsById.value[pid]) {
    const next = { ...decisionsById.value };
    delete next[pid];
    decisionsById.value = next;
  }
  papers.value = papers.value.filter((_, i) => i !== idx);
}

function setDecision(paperId: string, decision: string) {
  const pid = (paperId || "").trim();
  if (!pid) return;
  const next = { ...decisionsById.value };
  next[pid] = { ...(next[pid] ?? emptyDecisionRow(pid)), decision };
  decisionsById.value = next;
}

function setDecisionField(paperId: string, key: "reason_tag" | "notes", value: string) {
  const pid = (paperId || "").trim();
  if (!pid) return;
  const next = { ...decisionsById.value };
  next[pid] = { ...(next[pid] ?? emptyDecisionRow(pid)), [key]: value } as DecisionRow;
  decisionsById.value = next;
}

async function runPhase1() {
  if (!selectedProject.value) return;
  if (includedCount.value <= 0) throw new Error("还没有纳入的论文。请至少把 1 篇的 decision 设为 include。");
  const r = await api.runPhase1(selectedProject.value);
  await refreshTree();
  await refreshPdfs();
  await loadWorkbenchOutputs();
  showRun("Phase 1: Abstract -> Taxonomy", r);
}

async function runPhase2() {
  if (!selectedProject.value) return;
  const r = await api.runPhase2(selectedProject.value, phase2TopN.value);
  await refreshTree();
  await refreshPdfs();
  await loadWorkbenchOutputs();
  showRun("Phase 2: PDF -> Paper Cards", r);
}

async function runPhase3() {
  if (!selectedProject.value) return;
  const r = await api.runPhase3(selectedProject.value);
  await refreshTree();
  await refreshPdfs();
  await loadWorkbenchOutputs();
  showRun("Phase 3: Tables-first Draft", r);
}

async function runPhase4() {
  if (!selectedProject.value) return;
  const r = await api.runPhase4(selectedProject.value);
  await refreshTree();
  await refreshPdfs();
  await loadWorkbenchOutputs();
  showRun("Phase 4: Traceability Check", r);
}

async function runRubric() {
  if (!selectedProject.value) return;
  const r = await api.runRubric(selectedProject.value);
  showRun("Rubric Check", r);
}

async function createProject() {
  const slug = newSlug.value.trim();
  if (!slug) return;
  busyMsg.value = "创建项目中...";
  try {
    await api.createProject(slug);
    await refreshProjects(false);
    selectedProject.value = slug;
    selectedPath.value = "";
    mode.value = "workbench";
    await loadWorkbenchData();
    logTitle.value = "项目";
    logText.value = `已创建: ${slug}`;
  } finally {
    busyMsg.value = null;
  }
}

function openInFiles(path: string) {
  mode.value = "files";
  loadFile(path).catch(setError);
}

async function uploadPdf(paperId: string, file: File | null) {
  if (!selectedProject.value) return;
  if (!file) return;
  busyMsg.value = `上传 PDF: ${paperId}...`;
  try {
    await api.uploadPdf(selectedProject.value, paperId, file);
    await refreshPdfs();
    logTitle.value = "PDF";
    logText.value = `已上传: 05_evidence/pdfs/${paperId}.pdf`;
  } finally {
    busyMsg.value = null;
  }
}

async function onProjectChanged() {
  errorMsg.value = null;
  selectedPath.value = "";
  editorContent.value = "";
  dirty.value = false;
  await loadWorkbenchData();
}

onMounted(async () => {
  try {
    await api.health();
    await refreshProjects(true);
    if (selectedProject.value) await loadWorkbenchData();
  } catch (e) {
    setError(e);
  } finally {
    loading.value = false;
  }
});

watch(
  () => selectedProject.value,
  async (v, oldV) => {
    if (!v || v === oldV) return;
    await onProjectChanged();
  }
);
</script>

<template>
  <div class="app-shell" v-if="!loading">
    <aside class="panel sidebar">
      <div class="brand">
        <h1>Review Web</h1>
        <span class="pill">Survey/Tutorial</span>
      </div>

      <div class="card controls">
        <div class="row">
          <select v-model="selectedProject">
            <option value="" disabled>选择项目...</option>
            <option v-for="p in projects" :key="p.slug" :value="p.slug">{{ p.slug }}</option>
          </select>
        </div>
        <div class="row">
          <input type="text" v-model="newSlug" placeholder="新项目 slug (例如 demo_survey_web_2)" />
          <button class="btn primary" @click="createProject">创建</button>
        </div>
        <div class="row" style="justify-content: space-between; align-items: center">
          <div class="segmented">
            <button class="btn" :class="{ primary: mode === 'workbench' }" @click="mode = 'workbench'">工作台</button>
            <button class="btn" :class="{ primary: mode === 'files' }" @click="mode = 'files'">文件</button>
          </div>
        </div>
        <div class="row" style="gap: 10px; flex-wrap: wrap">
          <span class="badge"><strong>{{ papers.length }}</strong> 篇论文</span>
          <span class="badge"><strong>{{ includedCount }}</strong> 已纳入</span>
        </div>
        <div v-if="busyMsg" class="muted">{{ busyMsg }}</div>
      </div>

      <template v-if="mode === 'files'">
        <div class="card controls">
          <input type="text" v-model="fileQuery" placeholder="搜索文件..." />
        </div>

        <div class="card file-list">
          <div
            v-for="f in filteredFiles"
            :key="f.path"
            class="file-item"
            :class="{ active: f.path === selectedPath }"
            @click="loadFile(f.path).catch(setError)"
          >
            <code>{{ f.path }}</code>
            <span class="muted">{{ f.size }}B</span>
          </div>
          <div v-if="filteredFiles.length === 0" class="muted" style="padding: 10px">没有匹配文件</div>
        </div>
      </template>
    </aside>

    <main class="panel main">
      <template v-if="mode === 'workbench'">
        <div class="card main-header">
          <div>
            <h2>{{ selectedProject ? selectedProject : "未选择项目" }}</h2>
            <div class="muted">推荐流程: 导入论文 -> 摘要筛选 -> Phase 1 -> 上传 PDF -> Phase 2 -> Phase 3 -> Phase 4</div>
          </div>
          <div class="row" style="flex-wrap: wrap; justify-content: flex-end">
            <button class="btn" :disabled="!selectedProject" @click="loadWorkbenchData().catch(setError)">刷新</button>
            <button class="btn" :disabled="!selectedProject" @click="runRubric().catch(setError)">Rubric</button>
            <button class="btn primary" :disabled="!selectedProject || includedCount <= 0" @click="runPhase1().catch(setError)">
              运行 Phase 1
            </button>
            <button class="btn primary" :disabled="!selectedProject || pdfCount <= 0" @click="runPhase2().catch(setError)">运行 Phase 2</button>
            <button class="btn" :disabled="!selectedProject" @click="runPhase3().catch(setError)">运行 Phase 3</button>
            <button class="btn" :disabled="!selectedProject" @click="runPhase4().catch(setError)">运行 Phase 4</button>
          </div>
        </div>

        <div class="card editor">
          <div v-if="errorMsg" class="muted" style="color: var(--danger); padding: 0 0 8px 2px">{{ errorMsg }}</div>

          <div class="two-col">
            <div>
              <h3 class="section-title">1) 导入论文 (02_import/papers_canonical.csv)</h3>
              <p class="section-desc">最少需要: paper_id + title + abstract。编辑完点击保存。</p>

              <div class="row" style="justify-content: space-between; margin: 10px 0">
                <div class="row">
                  <button class="btn" @click="addPaperRow">新增一行</button>
                  <button class="btn primary" :disabled="!selectedProject" @click="savePapers().catch(setError)">保存论文</button>
                </div>
                <button class="btn" @click="openInFiles('02_import/papers_canonical.csv')">以文件方式打开</button>
              </div>

              <div class="table-wrap">
                <table class="grid">
                  <thead>
                    <tr>
                      <th style="min-width: 110px">paper_id</th>
                      <th style="min-width: 240px">title</th>
                      <th style="min-width: 90px">year</th>
                      <th style="min-width: 200px">authors</th>
                      <th style="min-width: 160px">venue</th>
                      <th style="min-width: 360px">abstract</th>
                      <th style="min-width: 180px">keywords</th>
                      <th style="min-width: 150px">doi</th>
                      <th style="min-width: 180px">url</th>
                      <th style="min-width: 150px">source</th>
                      <th style="width: 1%"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(p, idx) in papers" :key="idx">
                      <td><input type="text" v-model="p.paper_id" placeholder="P001" /></td>
                      <td><input type="text" v-model="p.title" placeholder="Title" /></td>
                      <td><input type="text" v-model="p.year" placeholder="2024" /></td>
                      <td><input type="text" v-model="p.authors" placeholder="Author A; Author B" /></td>
                      <td><input type="text" v-model="p.venue" placeholder="Venue" /></td>
                      <td><textarea v-model="p.abstract" placeholder="Abstract..." /></td>
                      <td><input type="text" v-model="p.keywords" placeholder="kw1; kw2" /></td>
                      <td><input type="text" v-model="p.doi" placeholder="10.xxxx/xxxx" /></td>
                      <td><input type="text" v-model="p.url" placeholder="https://..." /></td>
                      <td><input type="text" v-model="p.source_database" placeholder="scopus/wos/..." /></td>
                      <td><button class="btn danger" @click="removePaperRow(idx)">Remove</button></td>
                    </tr>
                    <tr v-if="papers.length === 0">
                      <td colspan="11" class="muted">暂无论文。点击“新增一行”。</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <h3 class="section-title">2) 摘要筛选 (03_screening/abstract_decisions.csv)</h3>
              <p class="section-desc">为每篇论文设置 decision。Phase 1 需要至少 1 篇 decision=include。</p>

              <div class="row" style="justify-content: space-between; margin: 10px 0">
                <div class="row">
                  <button class="btn primary" :disabled="!selectedProject" @click="saveDecisions().catch(setError)">保存筛选结果</button>
                </div>
                <button class="btn" @click="openInFiles('03_screening/abstract_decisions.csv')">以文件方式打开</button>
              </div>

              <div class="table-wrap">
                <table class="grid">
                  <thead>
                    <tr>
                      <th style="min-width: 110px">paper_id</th>
                      <th style="min-width: 240px">title</th>
                      <th style="min-width: 120px">decision</th>
                      <th style="min-width: 160px">reason_tag</th>
                      <th style="min-width: 260px">notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="p in papers" :key="p.paper_id || p.title">
                      <td class="mono">{{ p.paper_id }}</td>
                      <td>{{ p.title }}</td>
                      <td>
                        <select
                          :value="(decisionsById[p.paper_id]?.decision || '').toLowerCase()"
                          @change="setDecision(p.paper_id, ($event.target as HTMLSelectElement).value)"
                        >
                          <option value="">(未设置)</option>
                          <option value="include">include</option>
                          <option value="exclude">exclude</option>
                          <option value="uncertain">uncertain</option>
                        </select>
                      </td>
                      <td>
                        <input
                          type="text"
                          :value="decisionsById[p.paper_id]?.reason_tag || ''"
                          placeholder="core_topic / out_of_scope / ..."
                          @input="setDecisionField(p.paper_id, 'reason_tag', ($event.target as HTMLInputElement).value)"
                        />
                      </td>
                      <td>
                        <textarea
                          :value="decisionsById[p.paper_id]?.notes || ''"
                          placeholder="Notes..."
                          @input="setDecisionField(p.paper_id, 'notes', ($event.target as HTMLTextAreaElement).value)"
                        />
                      </td>
                    </tr>
                    <tr v-if="papers.length === 0">
                      <td colspan="5" class="muted">请先导入论文。</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="row" style="justify-content: space-between; margin-top: 12px">
                <span class="badge"><strong>{{ includedCount }}</strong> 已纳入 (Phase 1 需要 >= 1)</span>
                <span class="muted">提示: 任何其他产物都可以去“文件”模式查看。</span>
              </div>
            </div>
          </div>

          <div style="margin-top: 12px">
            <h3 class="section-title">3) Phase 1 产物</h3>
            <p class="section-desc">下面是快速预览。详细内容可在“文件”模式查看/编辑。</p>
            <div class="row" style="gap: 8px; flex-wrap: wrap; margin: 10px 0">
              <button class="btn" @click="openInFiles('04_taxonomy/taxonomy.yaml')">打开 taxonomy.yaml</button>
              <button class="btn" @click="openInFiles('04_taxonomy/paper_classification.csv')">打开 paper_classification.csv</button>
              <button class="btn" @click="openInFiles('04_taxonomy/fulltext_priority.csv')">打开 fulltext_priority.csv</button>
              <button class="btn" @click="openInFiles('04_taxonomy/table_figure_plan.yaml')">打开 table_figure_plan.yaml</button>
              <button class="btn" @click="openInFiles('06_draft/00_outline.md')">打开 00_outline.md</button>
            </div>

            <div class="two-col">
              <div class="card" style="padding: 12px">
                <div class="row" style="justify-content: space-between; padding-bottom: 6px">
                  <strong style="font-size: 13px">Taxonomy 预览</strong>
                  <span class="muted mono">04_taxonomy/taxonomy.yaml</span>
                </div>
                <pre class="mono" style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ taxonomyPreview || "（尚未生成）" }}</pre>
              </div>
              <div class="card" style="padding: 12px">
                <div class="row" style="justify-content: space-between; padding-bottom: 6px">
                  <strong style="font-size: 13px">Outline 预览</strong>
                  <span class="muted mono">06_draft/00_outline.md</span>
                </div>
                <pre class="mono" style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ outlinePreview || "（尚未生成）" }}</pre>
              </div>
            </div>
          </div>

          <div style="margin-top: 12px">
            <h3 class="section-title">4) 上传全文 PDF（Phase 2）</h3>
            <p class="section-desc">把 PDF 存到 `05_evidence/pdfs/&lt;paper_id&gt;.pdf`。这里可直接上传（只对已纳入论文建议上传）。</p>

            <div class="row" style="gap: 10px; flex-wrap: wrap; margin: 10px 0; justify-content: space-between">
              <div class="row" style="gap: 10px; flex-wrap: wrap">
                <span class="badge"><strong>{{ pdfCount }}</strong> 已上传 PDF</span>
                <span class="badge"><strong>{{ paperCardsCount }}</strong> paper cards</span>
              </div>
              <div class="row" style="max-width: 340px">
                <input type="number" v-model.number="phase2TopN" min="1" step="1" placeholder="Phase 2 top_n (默认 10)" />
              </div>
            </div>

            <div class="table-wrap">
              <table class="grid">
                <thead>
                  <tr>
                    <th style="min-width: 110px">paper_id</th>
                    <th style="min-width: 260px">title</th>
                    <th style="min-width: 120px">pdf</th>
                    <th style="min-width: 360px">upload</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in includedPapers" :key="p.paper_id">
                    <td class="mono">{{ p.paper_id }}</td>
                    <td>{{ p.title }}</td>
                    <td>
                      <span class="badge"><strong>{{ hasPdf(p.paper_id) ? "已上传" : "缺失" }}</strong></span>
                    </td>
                    <td>
                      <input
                        type="file"
                        accept="application/pdf"
                        @change="uploadPdf(p.paper_id, (($event.target as HTMLInputElement).files || [])[0] || null).catch(setError)"
                      />
                    </td>
                  </tr>
                  <tr v-if="includedPapers.length === 0">
                    <td colspan="4" class="muted">没有已纳入论文（先在摘要筛选中把 decision 设为 include）。</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div style="margin-top: 12px">
            <h3 class="section-title">5) Phase 2/3/4 产物</h3>
            <p class="section-desc">
              Phase 2 会生成 `05_evidence/paper_cards/*.json` + `05_evidence/chunks/chunks.jsonl`；Phase 3 会生成/刷新章节草稿；Phase 4 会输出 traceability 报告。
            </p>
            <div class="row" style="gap: 8px; flex-wrap: wrap; margin: 10px 0">
              <button class="btn" @click="openInFiles('05_evidence/chunks/chunks.jsonl')">打开 chunks.jsonl</button>
              <button class="btn" :disabled="!firstPaperCardPath" @click="firstPaperCardPath && openInFiles(firstPaperCardPath)">打开第一个 paper card</button>
              <button class="btn" @click="openInFiles('06_draft/10_intro.md')">打开 10_intro.md</button>
              <button class="btn" @click="openInFiles('06_draft/20_taxonomy.md')">打开 20_taxonomy.md</button>
              <button class="btn" @click="openInFiles('06_draft/30_comparison.md')">打开 30_comparison.md</button>
              <button class="btn" @click="openInFiles('06_draft/claims_map.csv')">打开 claims_map.csv</button>
              <button class="btn" @click="openInFiles('07_quality/traceability_report.md')">打开 traceability_report.md</button>
            </div>

            <div class="card" style="padding: 12px">
              <div class="row" style="justify-content: space-between; padding-bottom: 6px">
                <strong style="font-size: 13px">Traceability 预览</strong>
                <span class="muted mono">07_quality/traceability_report.md</span>
              </div>
              <pre class="mono" style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ tracePreview || "（尚未生成）" }}</pre>
            </div>
          </div>
        </div>

        <div class="card log">
          <div class="row" style="justify-content: space-between; padding-bottom: 8px">
            <strong style="font-size: 13px">{{ logTitle }}</strong>
            <span class="muted">API: <code>/api</code></span>
          </div>
          <pre>{{ logText }}</pre>
        </div>
      </template>

      <template v-else>
        <div class="card main-header">
          <div>
            <h2>{{ selectedProject ? selectedProject : "未选择项目" }}</h2>
            <div class="muted" v-if="selectedPath"><code>{{ selectedPath }}</code> <span v-if="dirty">(未保存)</span></div>
          </div>
          <div class="row">
            <button class="btn" :disabled="!selectedPath" @click="selectedPath && loadFile(selectedPath).catch(setError)">重载</button>
            <button class="btn primary" :disabled="!dirty || !selectedPath" @click="saveFile().catch(setError)">保存</button>
          </div>
        </div>

        <div class="card editor">
          <div v-if="errorMsg" class="muted" style="color: var(--danger); padding: 0 0 8px 2px">{{ errorMsg }}</div>
          <textarea v-model="editorContent" @input="dirty = true" spellcheck="false" :disabled="!selectedPath" />
        </div>

        <div class="card log">
          <div class="row" style="justify-content: space-between; padding-bottom: 8px">
            <strong style="font-size: 13px">{{ logTitle }}</strong>
            <span class="muted">API: <code>/api</code></span>
          </div>
          <pre>{{ logText }}</pre>
        </div>
      </template>
    </main>
  </div>

  <div v-else class="app-shell">
    <div class="panel" style="padding: 18px">
      <div class="muted">连接后端中... 请先启动 backend (默认端口: 8731)。</div>
    </div>
  </div>
</template>
