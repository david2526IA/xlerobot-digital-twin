# Ruta Isaac Sim

La descripción canónica está en `robot_description/xlerobot_v04.urdf`. Fue
importada con Isaac Sim 6.0.1 y el USD resultante contiene 16 joints, las mallas
CAD v0.4 y cámaras `neck_rgb`/`neck_depth`.

Fuentes geométricas oficiales: `XLeRobot040_armbase.step`, `XLeRobot040_dualwheelbase.step` y `XLeRobot040_neck_refined.step` en el repositorio upstream. El URDF oficial existente pertenece a XLeRobot 0.3 y no representa fielmente la base 0.4.

Ejecuta `isaac/import.ps1 -IsaacRoot C:\isaacsim` y después
`isaac/open.ps1 -IsaacRoot C:\isaacsim`. No desplegar en físico hasta que el
error de pose, rueda y cámara esté medido.
