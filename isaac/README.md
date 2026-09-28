# Isaac Sim: importación del gemelo 0.4

Isaac Sim puede importar MJCF directamente. Esta es la ruta recomendada porque el formato fuente del repositorio contiene los actuadores y límites de MuJoCo; NVIDIA recomienda MJCF cuando se quiere preservar esa configuración de actuadores.

## Importación reproducible por línea de comandos

Para Isaac Sim 6.1, indica la carpeta de instalación desde PowerShell:

```powershell
.\isaac\import.ps1 -IsaacRoot "C:\isaacsim"
```

El comando usa el ejemplo oficial `mjcf_import.py`, escribe
`isaac/generated/xlerobot.usd` y lo abre con `pxr` para comprobar las
articulaciones esperadas. `generated` es un artefacto regenerable y no se edita a
mano.

## Importar

1. Instala Isaac Sim con una GPU RTX y abre la aplicación.
2. Selecciona **File → Import → MJCF**.
3. Selecciona `assets/xlerobot/xlerobot.xml` de este repositorio y deja las mallas relativas en `assets/xlerobot/assets/`.
4. Guarda el resultado como `isaac/output/xlerobot_04.usd`.
5. Abre ese USD, pulsa Play y confirma que existen las 16 acciones: avance, giro, 12 de brazos/pinzas y 2 de cuello.
6. Añade una cámara RTX al frame importado de `head_camera_rgb_frame`; usa `docs/CALIBRATION_PROTOCOL.md` para sustituir la óptica provisional por la calibración física.

## Entrenamiento en Isaac

Para RL masivo, crea un proyecto Isaac Lab que clone el USD por entorno, exponga la misma acción de 16 dimensiones que `XLeRobotReachEnv` y use la posición del efector/cubo como observación inicial. Reutiliza las distribuciones de randomización de `docs/SIM_TO_REAL.md`.

No se incluye un USD preexportado porque Isaac Sim no está instalado en esta máquina y un USD generado sin abrir el importador no sería verificable. El MJCF, las mallas, la escena de mesa y los actuadores sí están listos para importarse.
