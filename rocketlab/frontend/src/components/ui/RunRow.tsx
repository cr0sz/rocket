import { ChevronRight } from "lucide-react"

interface RunRowProps {
  run: {
    id: string
    algorithm: string
    obs_mode: string | null
    seed: number | null
    status: string
    progress: number
    metrics: Record<string, any> | null
    duration_seconds: number | null
    created_at: string
    experiment?: { name: string; is_demo: boolean }
  }
}

export function RunRow({ run }: RunRowProps) {
  const statusColors: Record<string, string> = {
    completed: "text-green-400 border-green-900/50 bg-green-900/30",
    running: "text-amber-400 border-amber-900/50 bg-amber-900/30",
    failed: "text-red-400 border-red-900/50 bg-red-900/30",
    queued: "text-slate-400 border-slate-700 bg-slate-800",
    cancelled: "text-slate-500 border-slate-800 bg-slate-900",
  }

  const landing = run.metrics?.landing_success
  const landingText = landing === true ? "Landed" : landing === false ? "Crashed" : "—"
  const landingVariant = landing === true ? "success" : landing === false ? "danger" : "info"

  return (
    <div className="group border border-slate-800 rounded-xl bg-slate-900/40 p-3 hover:border-slate-700 transition">
      <div className="flex items-start justify-between gap-2 mb-1">
        <div className="flex items-center gap-2">
          <Badge variant="demo">{run.experiment?.is_demo ? "DEMO" : ""}</Badge>
          <span className="text-sm font-medium text-slate-200">{run.algorithm}</span>
        </div>
        <Badge variant={landing === true ? "success" : landing === false ? "danger" : "info"}>
          {landingText}
        </Badge>
      </div>
      <div className="flex items-center justify-between gap-3 mb-2">
        <div className="text-xs text-slate-500">
          Seed: {run.seed ?? "—"} · {run.obs_mode || "n/a"} obs
        </div>
        <div className="text-xs text-slate-400">
          {new Date(run.created_at).toLocaleString()}
        </div>
      </div>
      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div
          className="h-full bg-rocket-500 transition-all duration-500"
          style={{ width: `${run.progress}%` }}
        />
      </div>
      <div className="flex items-center justify-between gap-3 mt-2 text-xs text-slate-500">
        <span>
          {run.duration_seconds != null
            ? run.duration_seconds.toFixed(1) + " s"
            : "—"}
        </span>
        <span>
          Touchdown: {run.metrics?.touchdown_velocity_mps?.toFixed?.(1) ?? "—"} m/s
        </span>
      </div>
    </div>
  )
}
