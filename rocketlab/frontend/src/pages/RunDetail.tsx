import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import {
  getRun,
  getTelemetry,
  getTrajectory,
  getTraining,
  getLogs,
  cancelRun,
  retryRun,
} from "@/services/api"
import { Run } from "@/types"
import { Trajectory3D } from "@/components/viewer/Trajectory3D"
import { AltitudeChart, VelocityChart, FuelChart, TrainingChart } from "@/components/charts/TelemetryCharts"
import { MetricCard } from "@/components/ui/MetricCard"
import { Badge } from "@/components/ui/Badge"
import {
  RefreshCw,
  X,
  Rocket,
  Activity,
  Terminal,
} from "lucide-react"
import { useAppStore } from "@/hooks/useAppStore"

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [run, setRun] = useState<Run | null>(null)
  const [telemetry, setTelemetry] = useState<any[]>([])
  const [training, setTraining] = useState<any[]>([])
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const setTrajectory = useAppStore((s) => s.setTrajectory)
  const setTrainingStore = useAppStore((s) => s.setTraining)

  useEffect(() => {
    load()
  }, [id])

  async function load() {
    const [r, t, traj, tr, lg] = await Promise.all([
      getRun(id!),
      getTelemetry(id!, { limit: 5000 }),
      getTrajectory(id!),
      getTraining(id!, { limit: 1000 }),
      getLogs(id!, { limit: 200 }),
    ])
    setRun(r.data)
    setTelemetry(t.data)
    setTrajectory(traj.data.points)
    setTraining(tr.data)
    setTrainingStore(tr.data)
    setLogs(lg.data.reverse())
    setLoading(false)
  }

  if (loading) return <div className="text-slate-500 text-sm">Loading run…</div>
  if (!run) return <div className="text-slate-500 text-sm">Run not found</div>

  const m = run.metrics || {}

  const handleCancel = async () => {
    await cancelRun(id!)
    setRun((prev) => (prev ? { ...prev, status: "cancelled" as const } : prev))
  }
  const handleRetry = async () => {
    await retryRun(id!)
    setRun((prev) => (prev ? { ...prev, status: "queued" as const, progress: 0 } : prev))
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Run {run.id.slice(0, 8)}</h1>
          <p className="text-slate-400 text-sm">{run.algorithm} · {run.obs_mode || "n/a"} obs · seed {run.seed ?? "—"}</p>
        </div>
        <div className="flex items-center gap-2">
          {run.status === "running" && (
            <button
              onClick={handleCancel}
              className="px-3 py-1.5 bg-red-900/30 text-red-400 border border-red-900/50 rounded-lg text-xs hover:bg-red-900/50 transition"
            >
              <X size={14} /> Cancel
            </button>
          )}
          {(run.status === "failed" || run.status === "cancelled") && (
            <button
              onClick={handleRetry}
              className="px-3 py-1.5 bg-rocket-600 hover:bg-rocket-500 text-white rounded-lg text-xs transition"
            >
              <RefreshCw size={14} /> Retry
            </button>
          )}
        </div>
      </div>

      <div className="flex items-end gap-4 mb-2">
        <Badge variant="demo">DEMO</Badge>
        <Badge
          variant={run.status === "completed" ? "success" : run.status === "running" ? "warning" : run.status === "failed" ? "danger" : "info"}
        >
          {run.status.toUpperCase()}
        </Badge>
        <div className="flex items-center gap-1 text-xs text-slate-500">
          <Activity size={14} className="animate-pulse" />
          <span>{Math.round(run.progress)}%</span>
        </div>
      </div>

      {/* Overview metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard title="Result" value={m.landing_success ? "Landed" : "Crashed"} sub={run.status} trend={m.landing_success ? "safe" : "unsafe"} />
        <MetricCard title="Touchdown Velocity" value={m.touchdown_velocity_mps?.toFixed?.(1) ?? "—"} sub="m/s" />
        <MetricCard title="Horizontal Error" value={m.horizontal_error_m?.toFixed?.(1) ?? "—"} sub="m" />
        <MetricCard title="Fuel Used" value={m.fuel_used_kg?.toFixed?.(1) ?? "—"} sub="kg" />
        <MetricCard title="Max Altitude" value={m.max_altitude_m?.toFixed?.(0) ?? "—"} sub="m" />
        <MetricCard title="Duration" value={run.duration_seconds?.toFixed?.(1) ?? "—"} sub="s" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Viewer */}
        <div className="lg:col-span-2">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-slate-200">
                <Rocket size={16} className="mr-2" /> Flight Trajectory (3D)
              </h2>
              <span className="text-xs text-slate-500">{telemetry.length} telemetry points</span>
            </div>
            <div className="h-[500px]">
              <Trajectory3D
                points={telemetry}
                landingSuccess={m.landing_success}
                touchdownVelocity={m.touchdown_velocity_mps}
              />
            </div>
          </div>
        </div>

        {/* Telemetry charts */}
        <div className="lg:col-span-1">
          <div className="space-y-4">
            <AltitudeChart data={telemetry} />
            <VelocityChart data={telemetry} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-1">
          <FuelChart data={telemetry} />
        </div>
        <div className="lg:col-span-1">
          {training.length > 0 ? (
            <TrainingChart data={training} />
          ) : (
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 h-[260px] flex items-center justify-center text-slate-500 text-sm">
              No training data (non-RL run)
            </div>
          )}
        </div>
      </div>

      {/* Logs */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Terminal size={16} /> Worker Logs
          </h2>
          <span className="text-xs text-slate-500">{logs.length} entries</span>
        </div>
        <div className="p-4 font-mono text-xs overflow-y-auto max-h-64">
          {logs.length === 0 ? (
            <p className="text-slate-500">No logs yet</p>
          ) : (
            logs.map((log: any) => (
              <div key={log.id} className="flex gap-2 mb-1">
                <span className="text-slate-600 w-16">{new Date(log.t_s).toLocaleTimeString()}</span>
                <span
                  className={`text-xs ${log.level === "error" ? "text-red-400" : log.level === "warn" ? "text-amber-400" : "text-slate-300"}`}
                >
                  [{log.level.toUpperCase()}]
                </span>
                <span className="text-slate-400">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
