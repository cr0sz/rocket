export interface Experiment {
  id: string
  name: string
  description: string | null
  algorithm: string
  obs_mode: string | null
  seed: number | null
  config: Record<string, any> | null
  is_demo: boolean
  created_at: string
  updated_at: string | null
}

export interface ExperimentCreate {
  name: string
  description?: string
  algorithm: string
  obs_mode?: string | null
  seed?: number | null
  config?: Record<string, any> | null
  is_demo?: boolean
}

export interface Run {
  id: string
  experiment_id: string
  worker_id: string | null
  algorithm: string
  obs_mode: string | null
  seed: number | null
  config: Record<string, any> | null
  status: string
  progress: number
  metrics: Record<string, any> | null
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  duration_seconds: number | null
  created_at: string
}

export interface TelemetryPoint {
  id: number
  run_id: string
  t_s: number
  x_m: number
  y_m: number
  z_m: number
  vx_mps: number
  vy_mps: number
  vz_mps: number
  altitude_m: number
  speed_mps: number
  fuel_kg: number
  throttle: number
  tilt_deg: number
}

export interface TrainingMetric {
  id: number
  run_id: string
  episode: number
  reward: number
  avg_reward: number | null
  policy_loss: number | null
  value_loss: number | null
  episode_length: number | null
  success_rate: number | null
  t_s: number
}

export interface Worker {
  id: string
  name: string
  hostname: string
  cpu_info: string | null
  token: string
  status: string
  current_job_id: string | null
  last_heartbeat: string | null
  registered_at: string
}

export interface DashboardSummary {
  total_experiments: number
  total_runs: number
  landing_success_rate: number
  best_touchdown_velocity: number | null
  best_horizontal_error: number | null
  active_workers: number
  recent_runs: Run[]
}

export interface ComparisonRun {
  id: string
  experiment_name: string
  algorithm: string
  seed: number | null
  status: string
  metrics: Record<string, any> | null
  trajectory: TelemetryPoint[] | null
}
