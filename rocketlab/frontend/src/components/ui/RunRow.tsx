import { Badge } from "@/components/ui/Badge"

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
  }
}

export function RunRow({ run }: RunRowProps) {
  const landing = run.metrics?.landing_success
  const landingText = landing === true ? "Landed" : landing === false ? "Crashed" : "—"

  return (
    <div className="group border border-slate-800 rounded-xl bg-slate-900/40 p-3 hover:border-slate-700 transition">
      <div className="flex items-start justify-between gap-2 mb-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-200">{run.algorithm}</span>
        </div>
        <Badge
          variant={landing === true ? "success" : landing === false ? "danger" : "info"}
        >
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
