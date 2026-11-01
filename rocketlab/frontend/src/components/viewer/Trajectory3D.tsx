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
}

interface Trajectory3DProps {
  points: TrajectoryPoint[]
  landingSuccess?: boolean | null
  touchdownVelocity?: number | null
}

export function Trajectory3D({ points, landingSuccess, touchdownVelocity }: Trajectory3DProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [hoverInfo, setHoverInfo] = useState<{ t: number; alt: number; speed: number; fuel: number } | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x020617)
    scene.fog = new THREE.FogExp2(0x020617, 0.02)

    const camera = new THREE.PerspectiveCamera(60, containerRef.clientWidth / containerRef.clientHeight, 0.1, 2000)
    camera.position.set(120, 120, 120)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(containerRef.clientWidth, containerRef.clientHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    containerRef.current.appendChild(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05

    // Ground plane
    const groundGeo = new THREE.PlaneGeometry(400, 400, 32, 32)
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      side: THREE.DoubleSide,
      roughness: 0.8,
      metalness: 0.2,
    })
    const ground = new THREE.Mesh(groundGeo, groundMat)
    ground.rotation.x = -Math.PI / 2
    scene.add(ground)

    // Grid
    const grid = new THREE.GridHelper(400, 40, 0x334155, 0x0f172a)
    scene.add(grid)

    // Landing target (red X on ground)
    const targetGeo = new THREE.BoxGeometry(4, 0.2, 4)
    const targetMat = new THREE.MeshBasicMaterial({ color: 0xef4444 })
    const target = new THREE.Mesh(targetGeo, targetMat)
    target.position.set(0, 0.1, 0)
    scene.add(target)

    // Target cross lines
    const crossMat = new THREE.LineBasicMaterial({ color: 0xef4444, linewidth: 2 })
    const crossGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-6, 0.15, 0),
      new THREE.Vector3(6, 0.15, 0),
    ])
    scene.add(new THREE.Line(crossGeo, crossMat))
    const crossGeo2 = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0.15, -6),
      new THREE.Vector3(0, 0.15, 6),
    ])
    scene.add(new THREE.Line(crossGeo2, crossMat))

    // Trajectory line
    if (points && points.length > 0) {
      const trajectoryPts = points.map((p) => new THREE.Vector3(p.x_m, p.z_m, p.y_m))
      const trajGeo = new THREE.BufferGeometry().setFromPoints(trajectoryPts)
      const trajMat = new THREE.LineBasicMaterial({
        color: 0x3b82f6,
        transparent: true,
        opacity: 0.5,
      })
      const trajLine = new THREE.Line(trajGeo, trajMat)
      scene.add(trajLine)

      // Rocket mesh (simple cone + cylinder)
      const rocketGroup = new THREE.Group()
      const body = new THREE.Mesh(
        new THREE.CylinderGeometry(0.6, 0.6, 4, 16),
        new THREE.MeshStandardMaterial({ color: 0x3b82f6, emissive: 0x1e3a8a })
      )
      body.rotation.x = Math.PI / 2
      const nose = new THREE.Mesh(
        new THREE.ConeGeometry(0.6, 2, 16),
        new THREE.MeshStandardMaterial({ color: 0x60a5fa })
      )
      nose.position.y = 2
      nose.rotation.x = Math.PI / 2
      const flame = new THREE.Mesh(
        new THREE.ConeGeometry(0.4, 1.5, 12),
        new THREE.MeshBasicMaterial({ color: 0xfbbf24 })
      )
      flame.position.y = -3.5
      flame.rotation.x = Math.PI / 2
      rocketGroup.add(body, nose, flame)
      scene.add(rocketGroup)

      // Start point marker
      const startPt = trajectoryPts[0]
      const startGeo = new THREE.SphereGeometry(1.5, 16, 16)
      const startMat = new THREE.MeshBasicMaterial({ color: 0x22c55e })
      const startMarker = new THREE.Mesh(startGeo, startMat)
      startMarker.position.copy(startPt)
      startMarker.position.y += 1
      scene.add(startMarker)

      // Animation state
      let frame = 0
      const total = points.length
      let playing = true
      let rocketY = trajectoryPts[0].y
      let rocketX = trajectoryPts[0].x
      let rocketZ = trajectoryPts[0].z

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
      scene.add(ambientLight)
      const dirLight = new THREE.DirectionalLight(0xffffff, 1)
      dirLight.position.set(50, 100, 50)
      scene.add(dirLight)

      const animate = () => {
        requestAnimationFrame(animate)
        controls.update()

        if (playing && total > 0) {
          frame = (frame + 1) % total
          const pt = points[frame]
          rocketGroup.position.set(pt.x_m, pt.z_m, pt.y_m)
          rocketGroup.lookAt(
            points[(frame + 1) % total]?.x_m ?? pt.x_m,
            points[(frame + 1) % total]?.z_m ?? pt.z_m,
            points[(frame + 1) % total]?.y_m ?? pt.y_m
          )
          flame.scale.y = pt.throttle > 0 ? 1 : 0.1
          flame.material.color = pt.throttle > 0 ? new THREE.Color(0xfbbf24) : new THREE.Color(0x334155)

          setHoverInfo({
            t: pt.t_s,
            alt: pt.altitude_m,
            speed: pt.speed_mps,
            fuel: pt.fuel_kg,
          })
        }

        renderer.render(scene, camera)
      }
      animate()

      return () => {
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
    }
  }, [points])

  return (
    <div ref={containerRef} className="w-full h-[500px] bg-slate-900/30 border border-slate-800 rounded-xl relative overflow-hidden" />
  )
}
