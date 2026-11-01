import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts"

interface ChartPoint {
  t_s: number
  [key: string]: number | string
}

interface SeriesDef {
  points: ChartPoint[]
  color: string
  label: string
}

function seriesToChartData(series: SeriesDef[], key: string) {
  // Merge all series points by t_s
  const timeSet = new Set<number>()
  series.forEach((s) => s.points.forEach((p) => timeSet.add(p.t_s)))
  const times = Array.from(timeSet).sort((a, b) => a - b)
  return times.map((t) => {
    const row: any = { t_s: t }
    series.forEach((s, i) => {
      const pt = s.points.find((p) => p.t_s === t)
      row[`s${i}`] = pt ? pt[key] : null
    })
    return row
  })
}

export function AltitudeChart({ data, series }: { data?: ChartPoint[]; series?: SeriesDef[] }) {
  const pts = series ? seriesToChartData(series, "altitude_m") : (data || [])
  if (!pts || pts.length === 0) {
    return <div className="h-64 flex items-center justify-center text-slate-500 text-sm">No telemetry data</div>
  }
  return (
    <div className="bg-[#0e1524] border border-slate-800 rounded-xl p-4">
      <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Altitude vs Time</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={pts} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="t_s" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <YAxis tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <Tooltip
            contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", color: "#f8fafc" }}
            cursor={{ strokeDasharray: "3 3" }}
          />
          <Legend verticalAlign="top" align="right" height={36} />
          {series ? series.map((s, i) => (
            <Line
              key={i}
              type="monotone"
              dataKey={`s${i}`}
              stroke={s.color}
              strokeWidth={2}
              dot={false}
              name={s.label}
            />
          )) : (
            <Line type="monotone" dataKey="altitude_m" stroke="#3b82f6" strokeWidth={2} dot={false} />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-2 flex items-center gap-2">
        <span className="w-3 h-3 rounded-full bg-rocket-500" />
        <span className="text-xs text-slate-400">Altitude (m)</span>
      </div>
    </div>
  )
}

export function VelocityChart({ data, series }: { data?: ChartPoint[]; series?: SeriesDef[] }) {
  const pts = series ? seriesToChartData(series, "speed_mps") : (data || [])
  if (!pts || pts.length === 0) {
    return <div className="h-64 flex items-center justify-center text-slate-500 text-sm">No telemetry data</div>
  }
  return (
    <div className="bg-[#0e1524] border border-slate-800 rounded-xl p-4">
      <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Velocity vs Time</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={pts} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="t_s" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <YAxis tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", color: "#f8fafc" }} />
          <Legend verticalAlign="top" align="right" height={36} />
          {series ? series.map((s, i) => (
            <Line key={i} type="monotone" dataKey={`s${i}`} stroke={s.color} strokeWidth={2} dot={false} name={s.label} />
          )) : (
            <Line type="monotone" dataKey="speed_mps" stroke="#22c55e" strokeWidth={2} dot={false} />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-2 flex items-center gap-2">
        <span className="w-3 h-3 rounded-full bg-green-500" />
        <span className="text-xs text-slate-400">Speed (m/s)</span>
      </div>
    </div>
  )
}

export function FuelChart({ data, series }: { data?: ChartPoint[]; series?: SeriesDef[] }) {
  const pts = series ? seriesToChartData(series, "fuel_kg") : (data || [])
  if (!pts || pts.length === 0) {
    return <div className="h-64 flex items-center justify-center text-slate-500 text-sm">No telemetry data</div>
  }
  return (
    <div className="bg-[#0e1524] border border-slate-800 rounded-xl p-4">
      <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Fuel vs Time</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={pts} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="t_s" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <YAxis tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", color: "#f8fafc" }} />
          <Legend verticalAlign="top" align="right" height={36} />
          {series ? series.map((s, i) => (
            <Line key={i} type="monotone" dataKey={`s${i}`} stroke={s.color} strokeWidth={2} dot={false} name={s.label} />
          )) : (
            <Line type="monotone" dataKey="fuel_kg" stroke="#f59e0b" strokeWidth={2} dot={false} fill="#f59e0b" fillOpacity={0.1} />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-2 flex items-center gap-2">
        <span className="w-3 h-3 rounded-full bg-amber-500" />
        <span className="text-xs text-slate-400">Fuel (kg)</span>
      </div>
    </div>
  )
}

export function TrainingChart({ data }: { data: { episode: number; reward: number; avg_reward: number | null }[] }) {
  if (!data || data.length === 0) {
    return <div className="h-64 flex items-center justify-center text-slate-500 text-sm">No training data</div>
  }
  return (
    <div className="bg-[#0e1524] border border-slate-800 rounded-xl p-4">
      <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Training Reward vs Episode</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="episode" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <YAxis tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickMargin={8} />
          <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", color: "#f8fafc" }} />
          <Line type="monotone" dataKey="reward" stroke="#a855f7" strokeWidth={2} dot={false} />
          {data.some((d) => d.avg_reward != null) && (
            <Line type="monotone" dataKey="avg_reward" stroke="#818cf8" strokeWidth={2} strokeDasharray="4 4" dot={false} />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
