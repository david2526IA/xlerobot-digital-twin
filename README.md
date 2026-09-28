# XLeRobot 0.4 Digital Twin

Gemelo digital abierto y reproducible para el XLeRobot 0.4 de base diferencial. El objetivo inmediato es simulación, teleoperación y aprendizaje en **MuJoCo**; Isaac Sim queda documentado como ruta de importación cuando se haya validado el URDF específico de 0.4.

> Estado: el modelo MuJoCo y sus mallas se incluyen y se pueden ejecutar. El fabricante/proyecto upstream no ha publicado un URDF oficial de 0.4; por ello este repositorio no afirma que el URDF de 0.3 represente la base 0.4.

## Inicio rápido

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/run_mujoco.py
```

Esto abre el modelo de base diferencial con dos brazos SO-101, pinzas y cuello. Conecta un mando Switch compatible antes de iniciar para teleoperar; consulta [docs/TELEOP_SWITCH.md](docs/TELEOP_SWITCH.md).

Comprueba la integridad estática con `python scripts/validate_twin.py`. El protocolo que convierte este modelo en un gemelo físicamente validado está en [docs/CALIBRATION_PROTOCOL.md](docs/CALIBRATION_PROTOCOL.md).

## Contenido

- `assets/xlerobot/`: MJCF y mallas del modelo de dos ruedas.
- `scripts/run_mujoco.py`: simulador y teleoperación de mando.
- `scripts/download_model.py`: descarga explícita y reproducible de checkpoints.
- `docs/`: calibración, VR, cámaras, Isaac Sim, modelos y sim-to-real.
- `models/models.yaml`: catálogo con compatibilidad y limitaciones de cada checkpoint.
- `twin/manifest.yaml`: contrato de embodiment 0.4 y evidencia de cada parámetro.

## Arquitectura

```text
Switch / VR ──> adaptador de teleop ──> acciones normalizadas ──> MuJoCo
                                                          └──> LeRobot (futuro real)
MuJoCo cámara del cuello ──> imagen RGB / pose ──> VLA o visor VR
```

## Seguridad

Los modelos preentrenados incluidos en el catálogo son específicos de tarea. Nunca copies sus acciones al robot físico sin calibrar ejes, límites, cámara, latencia y una parada de emergencia. Empieza con el robot suspendido, velocidad limitada y una sola articulación.

## Procedencia y licencia

Los assets de `assets/xlerobot` proceden de [Vector-Wangel/MuJoCo-GS-Web](https://github.com/Vector-Wangel/MuJoCo-GS-Web), Apache-2.0. El diseño y software de XLeRobot proceden de [Vector-Wangel/XLeRobot](https://github.com/Vector-Wangel/XLeRobot), Apache-2.0. Consulta [docs/PROVENANCE.md](docs/PROVENANCE.md) antes de redistribuir modelos.
