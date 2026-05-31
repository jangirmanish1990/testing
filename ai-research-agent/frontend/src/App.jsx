import { useEffect, useRef, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS = API.replace(/^http/, "ws");

const STAGES = [
  { key: "plan", label: "Planning sub-topics" },
  { key: "research_done", label: "Researching the web" },
  { key: "write_done", label: "Drafting the report" },
  { key: "critique_done", label: "Critiquing for gaps" },
];

export default function App() {
  const [topic, setTopic] = useState("");
  const [status, setStatus] = useState("idle"); // idle | running | done | error
  const [events, setEvents] = useState([]);
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const wsRef = useRef(null);
  const logRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/api/runs`)
      .then((r) => r.json())
      .then(setHistory)
      .catch(() => {});
  }, [report]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [events]);

  function start() {
    if (!topic.trim() || status === "running") return;
    setStatus("running");
    setEvents([]);
    setReport(null);

    const ws = new WebSocket(`${WS}/ws/research`);
    wsRef.current = ws;
    ws.onopen = () => ws.send(JSON.stringify({ topic }));
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "progress") {
        setEvents((prev) => [...prev, msg]);
      } else if (msg.type === "report") {
        setReport(msg);
        setStatus("done");
        ws.close();
      } else if (msg.type === "error") {
        setEvents((prev) => [...prev, { event: "error", message: msg.message }]);
        setStatus("error");
        ws.close();
      }
    };
    ws.onerror = () => setStatus("error");
  }

  const reached = (key) => events.some((e) => e.event === key);

  return (
    <div className="min-h-screen bg-stone-950 text-stone-200 font-sans">
      <header className="border-b border-stone-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-baseline gap-3">
          <span className="text-amber-400 font-mono text-sm tracking-widest">
            ◆ AGENT
          </span>
          <h1 className="text-lg font-medium tracking-tight">
            Autonomous Research Assistant
          </h1>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-8">
        <section>
          <div className="flex gap-2 mb-6">
            <input
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && start()}
              placeholder="Enter a research topic…"
              className="flex-1 bg-stone-900 border border-stone-700 rounded-md px-4 py-2.5 text-sm outline-none focus:border-amber-500 transition"
            />
            <button
              onClick={start}
              disabled={status === "running"}
              className="bg-amber-500 text-stone-950 font-medium px-5 rounded-md text-sm hover:bg-amber-400 disabled:opacity-40 transition"
            >
              {status === "running" ? "Researching…" : "Research"}
            </button>
          </div>

          {status !== "idle" && (
            <div className="mb-6 space-y-2">
              {STAGES.map((s) => {
                const active = reached(s.key);
                const current =
                  status === "running" &&
                  !active &&
                  STAGES.findIndex((x) => reached(x.key)) === STAGES.indexOf(s) - 1;
                return (
                  <div key={s.key} className="flex items-center gap-3 text-sm">
                    <span
                      className={
                        active
                          ? "text-amber-400"
                          : current
                          ? "text-amber-400 animate-pulse"
                          : "text-stone-600"
                      }
                    >
                      {active ? "●" : current ? "◐" : "○"}
                    </span>
                    <span className={active ? "text-stone-200" : "text-stone-500"}>
                      {s.label}
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {events.length > 0 && !report && (
            <div
              ref={logRef}
              className="bg-stone-900 border border-stone-800 rounded-md p-4 font-mono text-xs text-stone-400 max-h-48 overflow-auto mb-6"
            >
              {events.map((e, i) => (
                <div key={i}>
                  <span className="text-amber-500/70">{e.event}</span>{" "}
                  {e.message || JSON.stringify(rest(e))}
                </div>
              ))}
            </div>
          )}

          {report && (
            <article className="bg-stone-900 border border-stone-800 rounded-lg p-6">
              <div className="text-xs text-stone-500 mb-4 font-mono">
                {report.source_count} sources · run {report.run_id?.slice(0, 8)}
              </div>
              <pre className="whitespace-pre-wrap text-sm text-stone-200 leading-relaxed font-sans">
                {report.markdown}
              </pre>
            </article>
          )}
        </section>

        <aside>
          <h2 className="text-xs uppercase tracking-widest text-stone-500 mb-3">
            Past runs
          </h2>
          <div className="space-y-1.5">
            {history.length === 0 && (
              <p className="text-sm text-stone-600">No runs yet.</p>
            )}
            {history.map((run) => (
              <button
                key={run.id}
                onClick={() =>
                  fetch(`${API}/api/runs/${run.id}`)
                    .then((r) => r.json())
                    .then((d) =>
                      setReport({
                        run_id: d.id,
                        topic: d.topic,
                        markdown: d.report_markdown,
                        source_count: d.source_count,
                      })
                    )
                }
                className="w-full text-left bg-stone-900 border border-stone-800 rounded-md px-3 py-2 hover:border-stone-600 transition"
              >
                <div className="text-sm text-stone-300 truncate">{run.topic}</div>
                <div className="text-xs text-stone-600 font-mono">
                  {run.source_count} sources
                </div>
              </button>
            ))}
          </div>
        </aside>
      </main>
    </div>
  );
}

function rest(e) {
  const { type, event, ...r } = e;
  return r;
}
