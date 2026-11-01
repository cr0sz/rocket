interface MetricCardProps {
  title: string
  value: string | number
  sub?: string
  trend?: string
  accent?: string
}

export function MetricCard({ title, value, sub, trend, accent = "rocket-500" }: MetricCardProps) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{title}</p>
          <div className="flex items-baseline gap-1 mt-1">
            <span className={`text-2xl font-bold text-white ${accent}`}>{value}</span>
            {sub && <span className="text-sm text-slate-500">{sub}</span>}
          </div>
        </div>
        <div className="ml-4">
          {trend && (
            <span className={`text-xs font-medium ${trend.startsWith("-") || trend.startsWith("+") ? "text-rocket-400" : "text-slate-500"}`}>
              {trend}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
