import { useEffect, useState } from "react"
import { listWorkers, registerWorker } from "@/services/api"
import { Worker } from "@/types"
import { Users, Rocket, Monitor, Activity } from "lucide-react"

export default function WorkersPage() {
  const [workers, setWorkers] = useState<Worker[]>([])
  const [loading, setLoading] = useState(true)
  const [registering, setRegistering] = useState(false)
  const [form, setForm] = useState({
    name: "",
    hostname: typeof window !== "undefined" ? window.location.hostname : "",
    cpu_info: "",
    token: "",
  })

  useEffect(() => {
    load()
  }, [])

  async function load() {
    const res = await listWorkers()
    setWorkers(res.data)
    setLoading(false)
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault()
    setRegistering(true)
    try {
      await registerWorker(form)
      setForm({ name: "", hostname: typeof window !== "undefined" ? window.location.hostname : "", cpu_info: "", token: "" })
      load()
    } catch (err) {
      alert("Failed to register worker")
    } finally {
      setRegistering(false)
    }
  }

  if (loading) return <div className="text-slate-500 text-sm">Loading workers…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Workers</h1>
          <p className="text-slate-400 text-sm">Distributed simulation workers</p>
        </div>
        <button
          onClick={() => setRegistering(!registering)}
          className="flex items-center gap-2 px-4 py-2 bg-rocket-600 hover:bg-rocket-500 text-white rounded-lg text-sm font-medium transition"
        >
          <Rocket size={16} /> Register Worker
        </button>
      </div>

      {registering && (
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 max-w-md">
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Worker Name</label>
              <input
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-rocket-500 focus:outline-none"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. bekir-laptop"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Hostname</label>
              <input
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-rocket-500 focus:outline-none"
                value={form.hostname}
                onChange={(e) => setForm({ ...form, hostname: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">CPU Info</label>
              <input
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-rocket-500 focus:outline-none"
                value={form.cpu_info}
                onChange={(e) => setForm({ ...form, cpu_info: e.target.value })}
                placeholder="e.g. Apple M2 Pro"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Worker Token</label>
              <input
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-rocket-500 focus:outline-none font-mono"
                value={form.token}
                onChange={(e) => setForm({ ...form, token: e.target.value })}
                placeholder="worker-change-me"
              />
              <p className="text-xs text-slate-500 mt-1">Set WORKER_TOKEN in backend .env to match</p>
            </div>
            <button
              type="submit"
              disabled={registering || !form.name || !form.token}
              className="w-full py-2 bg-rocket-600 hover:bg-rocket-500 text-white rounded-lg font-medium disabled:opacity-50 transition"
            >
              {registering ? "Registering…" : "Register Worker"}
            </button>
          </form>
        </div>
      )}

      <div className="border border-slate-800 rounded-xl bg-slate-900/40 p-4">
        <h2 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <Users size={16} /> Active Workers ({workers.length})
        </h2>
        {workers.length === 0 ? (
          <p className="text-sm text-slate-500">No workers registered. Register a worker to run simulations.</p>
        ) : (
          <div className="space-y-2">
            {workers.map((w) => (
              <div key={w.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-800/50">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2.5 h-2.5 rounded-full ${w.status === "online" ? "bg-green-400 animate-pulse" : "bg-slate-500"}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-slate-200">{w.name}</div>
                    <div className="text-xs text-slate-500">{w.hostname}</div>
                    <div className="text-xs text-slate-600 font-mono">{w.cpu_info || "unknown CPU"}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-medium">
                    {w.status === "online" ? "Online" : w.status === "busy" ? "Busy" : "Offline"}
                  </div>
                  <div className="text-xs text-slate-500 font-mono truncate max-w-[120px]" title={w.id}>
                    {w.id.slice(0, 8)}…
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
        <h2 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider flex items-center gap-2">
          <Monitor size={14} /> Connect a Local Worker
        </h2>
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-xs text-slate-300 overflow-x-auto">
          {`# PowerShell (Windows)
$env:WORKER_TOKEN="worker-change-me"
python -m rocketlab_worker register --name "my-laptop" --hostname $env:COMPUTERNAME --token $env:WORKER_TOKEN --api-url http://localhost:8080

python -m rocketlab_worker run`}
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Workers connect to the API, claim queued jobs, run simulations locally, and stream results back.
        </p>
      </div>
    </div>
  )
}
