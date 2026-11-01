import { useEffect, useState } from "react"
import { getDashboardSummary } from "@/services/api"
import { useAppStore } from "@/hooks/useAppStore"
import { MetricCard } from "@/components/ui/MetricCard"
import { Badge } from "@/components/ui/Badge"
import { AltitudeChart, VelocityChart, FuelChart, TrainingChart } from "@/components/charts/TelemetryCharts"
import { Trajectory3D } from "@/components/viewer/Trajectory3D"
import { ArrowRight } from "lucide-react"

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const setAppSummary = useAppStore((s) => s.setSummary)

  useEffect(() => {
    getDashboardSummary()
      .then((res) => {
        setSummary(res.data)
        setAppSummary(res.data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-slate-500">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-rocket-500 mb-4" />
        <p>Loading mission control…</p>
      </div>
    )
  }

  const m = summary || {}
  const recent = (m.recent_runs || []).slice(0, 6)
  const demoRun = recent.find((r: any) => r.metrics?.landing_success === true)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Mission Control</h1>
          <p className="text-slate-400 text-sm">
            Real-time experiment monitoring and telemetry
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 px-2 py-1 rounded bg-green-900/30 text-green-400 text-xs border border-green-900/50">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            System Online
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Experiments" value={m.total_experiments} sub="active" />
        <MetricCard title="Total Runs" value={m.total_runs} sub="simulations" />
        <MetricCard
          title="Landing Success Rate"
          value={m.landing_success_rate}
          sub="%"
          trend={m.landing_success_rate >= 50 ? "+stable" : "needs work"}
        />
        <MetricCard
          title="Best Touchdown Velocity"
          value={m.best_touchdown_velocity != null ? m.best_touchdown_velocity.toFixed(1) : "—"}
          sub="m/s"
          trend={m.best_touchdown_velocity != null && m.best_touchdown_velocity < 10 ? "safe" : "—"}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-slate-200">3D Trajectory Viewer</h2>
              <Badge variant="demo">DEMO</Badge>
            </div>
            <div className="h-[400px]">
              {demoRun ? (
                <Trajectory3D
                  points={[]}
                  landingSuccess={demoRun.metrics?.landing_success}
                  touchdownVelocity={demoRun.metrics?.touchdown_velocity_mps}
                />
              ) : (
                <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                  Select a run to view its 3D trajectory
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="lg:col-span-1">
          <div className="space-y-4">
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
              <h2 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Recent Activity</h2>
              {recent.length === 0 ? (
                <p className="text-sm text-slate-500">No runs yet</p>
              ) : (
                <div className="space-y-2">
                  {recent.map((r: any) => (
                    <div key={r.id} className="flex items-center gap-3 p-2 rounded-lg bg-slate-800/30 hover:bg-slate-800 transition group">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: r.metrics?.landing_success ? "#22c55e" : "#ef4444" }} />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-slate-200 truncate">{r.algorithm}</div>
                        <div className="text-xs text-slate-500 truncate">
                          Seed {r.seed} · {new Date(r.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <ArrowRight size={14} className="text-slate-600 group-hover:text-rocket-400" />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-2">
          <AltitudeChart data={demoRun ? [] : []} />
        </div>
        <div className="lg:col-span-2">
          <VelocityChart data={demoRun ? [] : []} />
        </div>
        <div className="lg:col-span-2">
          <FuelChart data={demoRun ? [] : []} />
        </div>
        <div className="lg:col-span-2">
          <TrainingChart data={demoRun ? [] : []} />
        </div>
      </div>
    </div>
  )
}
