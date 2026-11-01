import { useEffect, useState } from "react"
import { getDashboardSummary, getTelemetry } from "@/services/api"
import { MetricCard } from "@/components/ui/MetricCard"
import { Badge } from "@/components/ui/Badge"
import { AltitudeChart, VelocityChart, FuelChart } from "@/components/charts/TelemetryCharts"
import { Trajectory3D } from "@/components/viewer/Trajectory3D"
import { ArrowRight } from "lucide-react"

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [selectedRun, setSelectedRun] = useState<any>(null)
  const [telemetry, setTelemetry] = useState<any[]>([])

  useEffect(() => {
    getDashboardSummary()
      .then((res) => {
        setSummary(res.data)
        setLoading(false)
        // Auto-select first completed run
        const first = (res.data.recent_runs || [])[0]
        if (first) selectRun(first)
      })
      .catch(() => setLoading(false))
  }, [])

  async function selectRun(run: any) {
    setSelectedRun(run)
    setTelemetry([])
    const [t] = await Promise.all([getTelemetry(run.id, { limit: 5000 })])
    setTelemetry(t.data)
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-slate-500">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-rocket-500 mb-4" />
        <p>Loading mission control…</p>
      </div>
    )
  }

  const m = summary || {}
  const recent = (m.recent_runs || []).slice(0, 8)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Mission Control</h1>
          <p className="text-slate-400 text-sm">
            Real-time experiment monitoring and telemetry
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 px-2.5 py-1 rounded bg-green-900/30 text-green-400 text-xs font-medium border border-green-900/50">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            System Online
          </span>
        </div>
      </div>

      {/* Overview metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Experiments" value={m.total_experiments} sub="active" />
        <MetricCard title="Total Runs" value={m.total_runs} sub="simulations" />
        <MetricCard
          title="Landing Success Rate"
          value={m.landing_success_rate}
          sub="%"
          trend={m.landing_success_rate >= 50 ? "stable" : "needs work"}
        />
        <MetricCard
          title="Best Touchdown Velocity"
          value={m.best_touchdown_velocity != null ? m.best_touchdown_velocity.toFixed(1) : "—"}
          sub="m/s"
          trend={m.best_touchdown_velocity != null && m.best_touchdown_velocity < 10 ? "safe" : "—"}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Trajectory */}
        <div className="lg:col-span-2">
          <div className="bg-[#0e1524] border border-slate-800 rounded-xl p-0 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <svg className="w-4 h-4 text-rocket-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 19l7-7 7 7M5 12l7-7 7 7M12 4l-2 8M12 20l-2-8"/></svg>
                3D Trajectory Viewer
              </h2>
              <Badge variant={selectedRun?.metrics?.landing_success === true ? "success" : selectedRun?.metrics?.landing_success === false ? "danger" : "info"}>
                {selectedRun?.metrics?.landing_success === true ? "Landed" : selectedRun?.metrics?.landing_success === false ? "Crashed" : "Select a run"}
              </Badge>
            </div>
            <div className="h-[520px]">
              {selectedRun && telemetry.length > 0 ? (
                <Trajectory3D
                  points={telemetry}
                  landingSuccess={selectedRun.metrics?.landing_success}
                  touchdownVelocity={selectedRun.metrics?.touchdown_velocity_mps}
                />
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-500">
                  <svg className="w-10 h-10 text-slate-700 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                  <p className="text-sm">Select a completed run to view its 3D trajectory</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent activity */}
        <div className="lg:col-span-1">
          <div className="bg-[#0e1524] border border-slate-800 rounded-xl p-4">
            <h2 className="text-xs font-semibold text-slate-400 mb-4 uppercase tracking-wider">Recent Activity</h2>
            {recent.length === 0 ? (
              <p className="text-sm text-slate-500">No runs yet</p>
            ) : (
              <div className="space-y-1">
                {recent.map((r: any) => (
                  <div
                    key={r.id}
                    className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition ${selectedRun?.id === r.id ? "bg-rocket-500/10 border border-rocket-500/50" : "bg-slate-800/30 hover:bg-slate-800"}`}
                    onClick={() => selectRun(r)}
                  >
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: r.metrics?.landing_success ? "#22c55e" : "#ef4444" }} />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-slate-200 truncate">{r.algorithm}</div>
                      <div className="text-xs text-slate-500 truncate">
                        Seed {r.seed} · {new Date(r.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-xs font-mono">
                      {(r.metrics?.touchdown_velocity_mps ?? 0).toFixed(1)} m/s
                    </div>
                    <ArrowRight size={14} className="text-slate-600 group-hover:text-rocket-400" />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AltitudeChart data={telemetry} />
        </div>
        <div className="lg:col-span-1">
          <VelocityChart data={telemetry} />
          <FuelChart data={telemetry} />
        </div>
      </div>

      {selectedRun && (
        <div className="bg-[#0e1524]/50 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Run Details</h2>
            <span className="text-xs text-slate-500">{selectedRun.id.slice(0, 8)}</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-xs text-slate-500 uppercase">Algorithm</div>
              <div className="text-sm font-mono text-slate-200">{selectedRun.algorithm}</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-xs text-slate-500 uppercase">Seed</div>
              <div className="text-sm font-mono text-slate-200">{selectedRun.seed ?? "—"}</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-xs text-slate-500 uppercase">Touchdown</div>
              <div className="text-sm font-mono text-slate-200">
                {selectedRun.metrics?.touchdown_velocity_mps?.toFixed?.(1) ?? "—"} m/s
              </div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-xs text-slate-500 uppercase">Duration</div>
              <div className="text-sm font-mono text-slate-200">
                {selectedRun.duration_seconds?.toFixed?.(1) ?? "—"} s
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
