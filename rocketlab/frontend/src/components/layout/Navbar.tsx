import { Bell, HelpCircle, Sun, Moon, Menu } from "lucide-react"
import { useAppStore } from "@/hooks/useAppStore"

export function Navbar() {
  const { theme, setTheme, sidebarOpen, setSidebarOpen } = useAppStore()

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between px-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur">
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="p-2 text-slate-400 hover:text-white md:hidden"
      >
        <Menu size={20} />
      </button>

      <div className="flex items-center gap-4">
        <span className="text-xs font-mono text-slate-500">rocketlab.api › live</span>
        <div className="h-6 w-px bg-slate-800" />
        <span className="text-xs font-mono text-rocket-400">● system online</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition"
          title="Toggle theme"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition">
          <Bell size={18} className="relative" />
        </button>
        <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition">
          <HelpCircle size={18} />
        </button>
      </div>
    </header>
  )
}
