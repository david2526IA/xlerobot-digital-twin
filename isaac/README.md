# Isaac Sim: importación del gemelo 0.4

Isaac Sim importa el URDF canónico `robot_description/xlerobot_v04.urdf`. Así,
MuJoCo e Isaac comparten árbol, nombres, límites y geometría v0.4. Esta ruta fue
probada localmente con Isaac Sim 6.0.1.

## Importación reproducible por línea de comandos

Indica la carpeta de instalación desde PowerShell:

```powershell
.\isaac\import.ps1 -IsaacRoot "C:\isaacsim"
```

El comando usa el importador URDF oficial, conserva la base flotante y los fixed
joints, crea las cámaras RTX `neck_rgb` y `neck_depth`, y valida los 16 joints.
El USD regenerable queda en
`isaac/generated/xlerobot_v04/xlerobot_v04.usda`.

Para verlo después de importar:

```powershell
.\isaac\open.ps1 -IsaacRoot "C:\isaacsim"
```

La óptica usa temporalmente 60 grados de FOV. Debe sustituirse por la
calibración intrínseca y extrínseca del sensor físico antes del sim-to-real.

## Entrenamiento en Isaac

Para RL masivo, crea un proyecto Isaac Lab que clone el USD por entorno, exponga la misma acción de 16 dimensiones que `XLeRobotReachEnv` y use la posición del efector/cubo como observación inicial. Reutiliza las distribuciones de randomización de `docs/SIM_TO_REAL.md`.

El USD no se versiona porque contiene rutas y artefactos regenerables de Isaac.
El URDF, mallas y postprocesado de cámara sí están versionados y verificados.
