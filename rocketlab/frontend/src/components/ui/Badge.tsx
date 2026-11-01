interface BadgeProps {
  children: React.ReactNode
  variant?: "success" | "warning" | "danger" | "info" | "demo"
}

export function Badge({ children, variant = "info" }: BadgeProps) {
  const base = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium"
  const variants: Record<string, string> = {
    success: "bg-green-900/30 text-green-400 border border-green-900/50",
    warning: "bg-amber-900/30 text-amber-400 border border-amber-900/50",
    danger: "bg-red-900/30 text-red-400 border border-red-900/50",
    info: "bg-slate-800 text-slate-300 border border-slate-700",
    demo: "bg-purple-900/30 text-purple-400 border border-purple-900/50",
  }
  return (
    <span className={`${base} ${variants[variant]}`}>
      {children}
    </span>
  )
}
