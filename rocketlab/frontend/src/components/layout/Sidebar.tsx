import { Menu, LayoutDashboard, Rocket, BarChart, Activity, Users, Settings } from "lucide-react"
import { useAppStore } from "@/hooks/useAppStore"

export function Sidebar() {
  const { sidebarOpen, setSidebarOpen } = useAppStore()

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 w-64 border-r border-slate-800 bg-slate-900/90 backdrop-blur transform transition-transform duration-300 ${
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      } md:relative md:translate-x-0`}
    >
      <div className="flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-rocket-500 rounded-lg flex items-center justify-center">
            <Rocket className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-slate-100 tracking-tight">RocketLab</span>
        </div>
        <button
          onClick={() => setSidebarOpen(false)}
          className="md:hidden p-2 text-slate-400 hover:text-white"
        >
          <Menu size={20} />
        </button>
      </div>

      <nav className="mt-6 px-3 space-y-1">
        <a
          href="/"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-rocket-600/20 text-rocket-400 font-medium"
        >
          <LayoutDashboard size={18} />
          Mission Control
        </a>
        <a
          href="/experiments"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white transition"
        >
          <BarChart size={18} />
          Experiments
        </a>
        <a
          href="/workers"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white transition"
        >
          <Users size={18} />
          Workers
        </a>
        <a
          href="/comparison"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white transition"
        >
          <Activity size={18} />
          Comparison
        </a>
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
        <div className="flex items-center gap-2 px-2">
          <Settings size={16} className="text-slate-500" />
          <span className="text-xs text-slate-500">v0.1.0</span>
        </div>
      </div>
    </aside>
  )
}
