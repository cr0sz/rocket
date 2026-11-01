import { useEffect, useState } from "react"
import { listRuns } from "@/services/api"
import { Run } from "@/types"
import { Trajectory3D } from "@/components/viewer/Trajectory3D"
import { Activity, Rocket, Target, Fuel, ArrowRight } from "lucide-react"
import { Badge } from "@/components/ui/Badge"

export default function ComparisonPage() {
  const [runs, setRuns] = useState<Run[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    const res = await listRuns({ limit: 100 })
    setRuns(res.data)
    setLoading(false)
  }

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const isSelected = (id: string) => selected.has(id)
  const selectedRuns = runs.filter((r) => selected.has(r.id))

  if (loading) return <div className="text-slate-500 text-sm">Loading runs…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Experiment Comparison</h1>
          <p className="text-slate-400 text-sm">
            Select up to 3 runs to compare trajectories and metrics
          </p>
        </div>
        {selectedRuns.length > 0 && (
          <button
            onClick={() => setSelected(new Set())}
            className="px-3 py-1.5 bg-red-900/30 text-red-400 border border-red-900/50 rounded-lg text-xs hover:bg-red-900/50 transition"
          >
            Clear selection
          </button>
        )}
      </div>

      <div className="border border-slate-800 rounded-xl bg-slate-900/40 p-4 overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="py-2 px-3 text-xs font-medium text-slate-400 w-10">Select</th>
              <th className="py-2 px-3 text-xs font-medium text-slate-400">Algorithm</th>
              <th className="py-2 px-3 text-xs font-medium text-slate-400">Obs</th>
              <th className="py-2 px-3 text-xs font-medium text-slate-400">Seed</th>
              <th className="py-2 px-3 text-xs font-medium text-slate-400">Status</th>
              <th className="py-2 px-3 text-xs font-medium text-slate-400 text-right">Touchdown (m/s)</th>
              <th className="py-2 px-3 text-xs font-medium text-slate-400 text-right">Error (m)</th>
              <th className="py-2 px-3 text-xs font-medium text-slate-400 text-right">Fuel (kg)</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr
                key={r.id}
                className={`border-b border-slate-800 hover:bg-slate-800/30 transition group cursor-pointer ${isSelected(r.id) ? "bg-rocket-500/10 border-r-2 border-rocket-500" : ""}`}
                onClick={() => toggle(r.id)}
              >
                <td className="py-2 px-3">
                  <input
                    type="checkbox"
                    checked={isSelected(r.id)}
                    onChange={() => toggle(r.id)}
                    className="rounded bg-slate-800 border-slate-700 text-rocket-600 focus:ring-rocket-500"
                    disabled={selectedRuns.length >= 3 && !isSelected(r.id)}
                  />
                </td>
                <td className="py-2 px-3 text-sm text-slate-200">{r.algorithm}</td>
                <td className="py-2 px-3 text-xs text-slate-500">{r.obs_mode || "—"}</td>
                <td className="py-2 px-3 text-xs font-mono text-slate-400">{r.seed ?? "—"}</td>
                <td className="py-2 px-3">
                  <Badge
                    variant={r.status === "completed" ? "success" : r.status === "failed" ? "danger" : "info"}
                  >
                    {r.status}
                  </Badge>
                </td>
                <td className="py-2 px-3 text-xs text-right font-mono text-slate-300">
                  {r.metrics?.touchdown_velocity_mps?.toFixed?.(1) ?? "—"}
                </td>
                <td className="py-2 px-3 text-xs text-right font-mono text-slate-300">
                  {r.metrics?.horizontal_error_m?.toFixed?.(1) ?? "—"}
                </td>
                <td className="py-2 px-3 text-xs text-right font-mono text-slate-300">
                  {r.metrics?.fuel_used_kg?.toFixed?.(1) ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedRuns.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
            <Activity size={16} /> Selected Runs Comparison
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
              <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">3D Trajectories (Overlay)</h3>
              <div className="h-[400px]">
                <Trajectory3D points={selectedRuns[0]?.trajectory || []} />
              </div>
            </div>
            <div className="space-y-4">
              <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Metrics Table</h3>
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 mb-2">
                    <th className="px-3 py-2 text-left text-slate-400">Metric</th>
                    {selectedRuns.map((r) => (
                      <th key={r.id} className="px-3 py-2 text-right text-slate-400 truncate max-w-[120px]" title={r.id.slice(0, 8)}>
                        {r.id.slice(0, 8)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="px-3 py-2 border-b border-slate-800 text-slate-300">Touchdown (m/s)</td>
                    {selectedRuns.map((r) => (
                      <td key={r.id} className="px-3 py-2 border-b border-slate-800 text-right font-mono text-slate-200">
                        {r.metrics?.touchdown_velocity_mps?.toFixed?.(1) ?? "—"}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-3 py-2 border-b border-slate-800 text-slate-300">Error (m)</td>
                    {selectedRuns.map((r) => (
                      <td key={r.id} className="px-3 py-2 border-b border-slate-800 text-right font-mono text-slate-200">
                        {r.metrics?.horizontal_error_m?.toFixed?.(1) ?? "—"}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-3 py-2 border-b border-slate-800 text-slate-300">Fuel (kg)</td>
                    {selectedRuns.map((r) => (
                      <td key={r.id} className="px-3 py-2 border-b border-slate-800 text-right font-mono text-slate-200">
                        {r.metrics?.fuel_used_kg?.toFixed?.(1) ?? "—"}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-3 py-2 border-b border-slate-800 text-slate-300">Duration (s)</td>
                    {selectedRuns.map((r) => (
                      <td key={r.id} className="px-3 py-2 border-b border-slate-800 text-right font-mono text-slate-200">
                        {r.duration_seconds?.toFixed?.(1) ?? "—"}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {runs.length === 0 && (
        <div className="text-center py-20 text-slate-500">
          <p>No runs available. Create an experiment and run a simulation first.</p>
        </div>
      )}
    </div>
  )
}
