import { create } from "zustand"
import { persist } from "zustand/middleware"
import {
  DashboardSummary,
  Experiment,
  Run,
  TelemetryPoint,
  TrainingMetric,
  Worker,
} from "@/types"

interface AppState {
  // UI
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  theme: "dark" | "light"
  setTheme: (theme: "dark" | "light") => void

  // Data
  summary: DashboardSummary | null
  setSummary: (s: DashboardSummary) => void
  experiments: Experiment[]
  setExperiments: (e: Experiment[]) => void
  runs: Run[]
  setRuns: (r: Run[]) => void
  workers: Worker[]
  setWorkers: (w: Worker[]) => void

  // Selected run for detail view
  selectedRunId: string | null
  setSelectedRunId: (id: string | null) => void

  // Telemetry for viewer
  trajectory: TelemetryPoint[]
  setTrajectory: (pts: TelemetryPoint[]) => void
  training: TrainingMetric[]
  setTraining: (m: TrainingMetric[]) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      theme: "dark",
      setTheme: (t) => set({ theme: t }),
      summary: null,
      setSummary: (s) => set({ summary: s }),
      experiments: [],
      setExperiments: (e) => set({ experiments: e }),
      runs: [],
      setRuns: (r) => set({ runs: r }),
      workers: [],
      setWorkers: (w) => set({ workers: w }),
      selectedRunId: null,
      setSelectedRunId: (id) => set({ selectedRunId: id }),
      trajectory: [],
      setTrajectory: (pts) => set({ trajectory: pts }),
      training: [],
      setTraining: (m) => set({ training: m }),
    }),
    { name: "rocketlab-storage" }
  ),
)
