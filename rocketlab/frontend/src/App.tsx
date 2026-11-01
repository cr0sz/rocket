import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Sidebar } from "@/components/layout/Sidebar"
import { Navbar } from "@/components/layout/Navbar"
import DashboardPage from "@/pages/Dashboard"
import ExperimentsPage from "@/pages/Experiments"
import RunDetailPage from "@/pages/RunDetail"
import ComparisonPage from "@/pages/Comparison"
import WorkersPage from "@/pages/Workers"

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-slate-200">
        <Sidebar />
        <Navbar />
        <main className="md:ml-64 p-4 md:p-6 transition-margin duration-300">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/experiments" element={<ExperimentsPage />} />
            <Route path="/experiments/:id" element={<ExperimentsPage />} />
            <Route path="/runs/:id" element={<RunDetailPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="/workers" element={<WorkersPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
