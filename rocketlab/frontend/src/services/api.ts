import axios from "axios"

const API_BASE = import.meta.env.VITE_API_URL || "/api"

const api = axios.create({
  baseURL: `${API_BASE}/v1`,
  headers: {
    "Content-Type": "application/json",
  },
})

// Experiments
export const listExperiments = (params?: {
  skip?: number
  limit?: number
  algorithm?: string
  is_demo?: boolean
}) => api.get("/experiments", { params })

export const getExperiment = (id: string) => api.get(`/experiments/${id}`)

export const createExperiment = (data: any) => api.post("/experiments", data)

export const updateExperiment = (id: string, data: any) =>
  api.patch(`/experiments/${id}`, data)

export const deleteExperiment = (id: string) =>
  api.delete(`/experiments/${id}`)

export const listExperimentRuns = (id: string) =>
  api.get(`/experiments/${id}/runs`)

// Runs
export const listRuns = (params?: {
  skip?: number
  limit?: number
  status?: string
  algorithm?: string
  experiment_id?: string
}) => api.get("/runs", { params })

export const getRun = (id: string) => api.get(`/runs/${id}`)

export const createRun = (data: any) => api.post("/runs", data)

export const updateRun = (id: string, data: any) =>
  api.patch(`/runs/${id}`, data)

export const cancelRun = (id: string) => api.post(`/runs/${id}/cancel`)

export const retryRun = (id: string) => api.post(`/runs/${id}/retry`)

export const getTelemetry = (runId: string, params?: { limit?: number; offset?: number }) =>
  api.get(`/runs/${runId}/telemetry`, { params })

export const getTrajectory = (runId: string) =>
  api.get(`/runs/${runId}/trajectory`)

export const getTraining = (runId: string, params?: { limit?: number }) =>
  api.get(`/runs/${runId}/training`, { params })

export const getLogs = (runId: string, params?: { limit?: number }) =>
  api.get(`/runs/${runId}/logs`, { params })

// Workers
export const listWorkers = (params?: { skip?: number; limit?: number }) =>
  api.get("/workers", { params })

export const registerWorker = (data: any) => api.post("/workers/register", data)

export const workerHeartbeat = (data: any) => api.post("/workers/heartbeat", data)

export const claimJob = (data: any) => api.post("/workers/claim", data)

// Dashboard
export const getDashboardSummary = () => api.get("/dashboard/summary")
