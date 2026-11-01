import { useEffect, useRef, useState } from "react"
import * as THREE from "three"
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js"

interface TrajectoryPoint {
  t_s: number
  x_m: number
  y_m: number
  z_m: number
  altitude_m: number
  speed_mps: number
  fuel_kg: number
  throttle: number
}

interface Trajectory3DProps {
  points: TrajectoryPoint[]
  landingSuccess?: boolean | null
  touchdownVelocity?: number | null
}

export function Trajectory3D({ points, landingSuccess: _landingSuccess, touchdownVelocity: _touchdownVelocity }: Trajectory3DProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [telemetry, setTelemetry] = useState<{ t: number; alt: number; speed: number; fuel: number } | null>(null)
  const [playing, setPlaying] = useState(true)

  useEffect(() => {
    if (!containerRef.current) return

    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x020617)
    scene.fog = new THREE.FogExp2(0x020617, 0.015)

    const camera = new THREE.PerspectiveCamera(
      55,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      2000,
    )
    camera.position.set(140, 140, 140)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    containerRef.current.appendChild(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.06
    controls.autoRotate = false
    controls.autoRotateSpeed = 1.0

    // Ground plane
    const groundGeo = new THREE.PlaneGeometry(500, 500, 64, 64)
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x0b1120,
      side: THREE.DoubleSide,
      roughness: 0.9,
      metalness: 0.1,
    })
    const ground = new THREE.Mesh(groundGeo, groundMat)
    ground.rotation.x = -Math.PI / 2
    scene.add(ground)

    // Grid
    const grid = new THREE.GridHelper(500, 50, 0x1e293b, 0x070a14)
    scene.add(grid)

    // Landing target on ground
    const targetMat = new THREE.MeshBasicMaterial({ color: 0xef4444 })
    const targetGeo = new THREE.RingGeometry(2, 5, 32)
    const target = new THREE.Mesh(targetGeo, targetMat)
    target.rotation.x = -Math.PI / 2
    target.position.set(0, 0.05, 0)
    scene.add(target)

    // Target pulse ring
    const pulseGeo = new THREE.RingGeometry(4, 6, 64)
    const pulseMat = new THREE.MeshBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0 })
    const pulse = new THREE.Mesh(pulseGeo, pulseMat)
    pulse.rotation.x = -Math.PI / 2
    pulse.position.set(0, 0.06, 0)
    scene.add(pulse)

    // Trajectory line
    let trajectoryLine: THREE.Line | null = null
    if (points && points.length > 1) {
      const trajPts = points.map((p) => new THREE.Vector3(p.x_m, p.z_m, p.y_m))
      const trajGeo = new THREE.BufferGeometry().setFromPoints(trajPts)
      const trajMat = new THREE.LineBasicMaterial({
        color: 0x3b82f6,
        transparent: true,
        opacity: 0.35,
      })
      trajectoryLine = new THREE.Line(trajGeo, trajMat)
      scene.add(trajectoryLine)
    }

    // Start marker (green)
    let startMarker: THREE.Mesh | null = null
    if (points && points.length > 0) {
      const startGeo = new THREE.SphereGeometry(1.2, 16, 16)
      const startMat = new THREE.MeshBasicMaterial({ color: 0x22c55e })
      startMarker = new THREE.Mesh(startGeo, startMat)
      startMarker.position.set(points[0].x_m, points[0].z_m, points[0].y_m + 1)
      scene.add(startMarker)
    }

    // Landing marker (red if crashed, green if landed)
    let landMarker: THREE.Mesh | null = null
    if (points && points.length > 0) {
      const last = points[points.length - 1]
      const landGeo = new THREE.SphereGeometry(1.2, 16, 16)
      const landMat = new THREE.MeshBasicMaterial({
        color: _landingSuccess === true ? 0x22c55e : 0xef4444,
      })
      landMarker = new THREE.Mesh(landGeo, landMat)
      landMarker.position.set(last.x_m, last.z_m, last.y_m + 1)
      scene.add(landMarker)
    }

    // Rocket mesh
    const rocketGroup = new THREE.Group()
    const body = new THREE.Mesh(
      new THREE.CylinderGeometry(0.5, 0.5, 3.5, 16),
      new THREE.MeshStandardMaterial({ color: 0x3b82f6, emissive: 0x1e3a8a }),
    )
    body.rotation.x = Math.PI / 2
    const nose = new THREE.Mesh(
      new THREE.ConeGeometry(0.5, 1.8, 16),
      new THREE.MeshStandardMaterial({ color: 0x60a5fa }),
    )
    nose.position.y = 1.9
    nose.rotation.x = Math.PI / 2
    const flame = new THREE.Mesh(
      new THREE.ConeGeometry(0.35, 1.2, 12),
      new THREE.MeshBasicMaterial({ color: 0xfbbf24 }),
    )
    flame.position.y = -2.6
    flame.rotation.x = Math.PI / 2
    rocketGroup.add(body, nose, flame)
    scene.add(rocketGroup)

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.25)
    scene.add(ambientLight)
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8)
    dirLight.position.set(50, 100, 50)
    scene.add(dirLight)

    // Animation state
    let frame = 0
    const total = points.length
    let animId: number

    const animate = () => {
      animId = requestAnimationFrame(animate)
      controls.update()

      // Pulse animation
      const time = Date.now() / 1000
      pulse.scale.set(1 + Math.sin(time * 3) * 0.3, 1 + Math.sin(time * 3) * 0.3, 1)
      pulse.material.opacity = 0.3 + Math.sin(time * 3) * 0.2

      if (playing && total > 0) {
        frame = (frame + 1) % total
        const pt = points[frame]
        rocketGroup.position.set(pt.x_m, pt.z_m, pt.y_m)
        rocketGroup.lookAt(
          points[(frame + 1) % total]?.x_m ?? pt.x_m,
          points[(frame + 1) % total]?.z_m ?? pt.z_m,
          points[(frame + 1) % total]?.y_m ?? pt.y_m,
        )
        flame.scale.y = pt.throttle > 0 ? 1 : 0.15
        flame.material.color = pt.throttle > 0 ? new THREE.Color(0xfbbf24) : new THREE.Color(0x334155)

        setTelemetry({
          t: pt.t_s,
          alt: pt.altitude_m,
          speed: pt.speed_mps,
          fuel: pt.fuel_kg,
        })
      }

      renderer.render(scene, camera)
    }
    animate()

    const handleResize = () => {
      if (!containerRef.current) return
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    }
    window.addEventListener("resize", handleResize)

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener("resize", handleResize)
      controls.dispose()
      renderer.dispose()
      scene.traverse((object) => {
        if ((object as THREE.Mesh).geometry) (object as THREE.Mesh).geometry.dispose()
        if ((object as THREE.Mesh).material) {
          const m = object as THREE.Mesh
          if (Array.isArray(m.material)) m.material.forEach((mat) => mat.dispose())
          else m.material.dispose()
        }
      })
      if (containerRef.current) containerRef.current.removeChild(renderer.domElement)
    }
  }, [points, _landingSuccess, playing])

  if (!points || points.length === 0) {
    return (
      <div ref={containerRef} className="w-full h-[520px] bg-[#0e1524]/50 border border-slate-800 rounded-xl flex items-center justify-center text-slate-500">
        No trajectory data
      </div>
    )
  }

  return (
    <div className="w-full h-[520px] bg-[#0e1524]/50 border border-slate-800 rounded-xl relative overflow-hidden">
      <div ref={containerRef} className="absolute inset-0" />
      <div className="absolute bottom-4 left-4 right-4 p-4 bg-[#070b14]/90 backdrop-blur border border-slate-800 rounded-lg">
        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300">
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "#3b82f6" }} />
            <span>T: {telemetry?.t.toFixed?.(1) ?? "—"}s</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-rocket-500" />
            <span>Alt: {telemetry?.alt.toFixed?.(0) ?? "—"}m</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            <span>Speed: {telemetry?.speed.toFixed?.(1) ?? "—"}m/s</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            <span>Fuel: {telemetry?.fuel.toFixed?.(0) ?? "—"}kg</span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={() => setPlaying((p) => !p)}
              className="p-1.5 rounded bg-slate-800 text-slate-300 hover:text-white transition"
              title={playing ? "Pause" : "Play"}
            >
              {playing ? "⏸" : "▶"}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
