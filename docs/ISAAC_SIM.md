# Ruta Isaac Sim

MuJoCo es el entorno canónico de este repositorio porque aquí se incluye un modelo funcional de base diferencial. Isaac Sim debe importarse cuando se haya generado y validado un URDF 0.4.

Fuentes geométricas oficiales: `XLeRobot040_armbase.step`, `XLeRobot040_dualwheelbase.step` y `XLeRobot040_neck_refined.step` en el repositorio upstream. El URDF oficial existente pertenece a XLeRobot 0.3 y no representa fielmente la base 0.4.

Proceso: exportar STEP a mallas en metros; crear enlaces y joints de la base diferencial; reutilizar límites de los SO-101; estimar masas/inercia; importar con el URDF Importer; crear articulación, drives y cámaras RTX; validar la misma trayectoria de articulaciones contra MuJoCo. No desplegar en físico hasta que el error de pose, rueda y cámara esté medido.
