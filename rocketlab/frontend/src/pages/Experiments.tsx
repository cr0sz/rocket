import { useEffect, useState } from "react"
import { listExperiments, createExperiment } from "@/services/api"
import { useAppStore } from "@/hooks/useAppStore"
import { Experiment } from "@/types"
import { Rocket, Plus, ArrowRight } from "lucide-react"
import { Badge } from "@/components/ui/Badge"

const ALGORITHMS = [
  { value: "ppo_extended", label: "PPO (Extended)", obs: "extended" },
  { value: "ppo_basic", label: "PPO (Basic)", obs: "basic" },
  { value: "hand_rule", label: "Hand Rule", obs: null },
  { value: "random", label: "Random", obs: null },
]

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({
    name: "",
    description: "",
    algorithm: "ppo_extended" as string,
    obs_mode: "extended" as string | null,
    seed: 0 as number | null,
    is_demo: false,
  })
  const setAppExperiments = useAppStore((s) => s.setExperiments)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    const res = await listExperiments()
    setExperiments(res.data)
    setAppExperiments(res.data)
    setLoading(false)
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setCreating(true)
    try {
      const res = await createExperiment({
        name: form.name,
        description: form.description || null,
        algorithm: form.algorithm,
        obs_mode: form.obs_mode,
        seed: form.seed,
        config: { demo: form.is_demo },
        is_demo: form.is_demo,
      })
      setExperiments((prev) => [...prev, res.data])
      setAppExperiments([...experiments, res.data])
      setForm({ name: "", description: "", algorithm: "ppo_extended", obs_mode: "extended", seed: 0, is_demo: false })
    } catch (err) {
      alert("Failed to create experiment")
    } finally {
      setCreating(false)
    }
  }

  if (loading) return <div className="text-slate-500 text-sm">Loading experiments…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Experiments</h1>
          <p className="text-slate-400 text-sm">Create and manage simulation experiments</p>
        </div>
        <button
          onClick={() => setCreating(!creating)}
          className="flex items-center gap-2 px-4 py-2 bg-rocket-600 hover:bg-rocket-500 text-white rounded-lg text-sm font-medium transition"
        >
          <Plus size={16} /> New Experiment
        </button>
      </div>

      {creating && (
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <form onSubmit={handleCreate} className="space-y-4 max-w-md">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Experiment Name</label>
              <input
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-rocket-500 focus:outline-none"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. PPO Extended Sweep"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Description</label>
              <input
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-rocket-500 focus:outline-none"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Algorithm</label>
                <select
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-rocket-500 focus:outline-none"
                  value={form.algorithm}
                  onChange={(e) => {
                    const alg = e.target.value as string
                    const obs = ALGORITHMS.find((a) => a.value === alg)?.obs ?? null
                    setForm({ ...form, algorithm: alg, obs_mode: obs })
                  }}
                >
                  {ALGORITHMS.map((a) => (
                    <option key={a.value} value={a.value}>
                      {a.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-2 text-xs font-medium text-slate-400">
                  <input
                    type="checkbox"
                    checked={form.is_demo}
                    onChange={(e) => setForm({ ...form, is_demo: e.target.checked })}
                    className="rounded bg-slate-800 border-slate-700 text-rocket-600 focus:ring-rocket-500"
                  />
                  Demo data
                </label>
              </div>
            </div>
            <button
              type="submit"
              disabled={!form.name || creating}
              className="w-full py-2 bg-rocket-600 hover:bg-rocket-500 text-white rounded-lg font-medium disabled:opacity-50 transition"
            >
              {creating ? "Creating…" : "Create Experiment"}
            </button>
          </form>
        </div>
      )}

      <div className="border border-slate-800 rounded-xl bg-slate-900/40 p-4">
        <h2 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <Rocket size={16} /> All Experiments ({experiments.length})
        </h2>
        {experiments.length === 0 ? (
          <p className="text-sm text-slate-500">No experiments yet. Create one to get started.</p>
        ) : (
          <div className="space-y-2">
            {experiments.map((exp) => (
              <div
                key={exp.id}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 cursor-pointer hover:bg-slate-800 transition group"
                onClick={() => {}}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-slate-200">{exp.name}</span>
                    <Badge variant="demo">{exp.is_demo ? "DEMO" : ""}</Badge>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    {exp.algorithm} · {exp.obs_mode || "n/a"} obs · seed {exp.seed ?? "—"}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono text-slate-400 truncate max-w-[120px]" title={exp.id}>
                    {exp.id.slice(0, 8)}…
                  </div>
                  <ArrowRight size={14} className="text-slate-600 group-hover:text-rocket-400 ml-2" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
