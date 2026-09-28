# Entrenamiento paso a paso

## 1. Preparar MuJoCo

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python scripts/validate_twin.py
python scripts/smoke_env.py
```

`smoke_env.py` ejecuta una tarea de alcance y guarda una imagen de `neck_rgb`. Si esto falla, no avances a entrenamiento.

## 2. Entrenar la primera política

```powershell
pip install -r requirements-rl.txt
python scripts/train_rl.py
```

La primera tarea es alcanzar el cubo; no usa agarre asistido. Es el control de sanidad para cinemática, acciones, cámaras y recompensa. Después se debe implementar una tarea de agarre sólo cuando las pinzas y el contacto estén calibrados.

## 3. Demostraciones y VLA

Genera primero episodios de prueba con `python scripts/record_rollouts.py --episodes 100`. Los `.npz` guardan observación, acción, recompensa e instrucción sin esconder ninguna conversión. Teleopera después con el mando en `scripts/run_mujoco.py` y registra la misma estructura. Convierte únicamente demostraciones de calidad al formato LeRobot. Empieza con SmolVLA, que requiere fine-tuning sobre las mismas vistas de cámara y la misma semántica de acción.

## 4. Randomización antes de sim-to-real

Por episodio, aleatoriza posición de cubo, iluminación, textura, masa, fricción, cámara, ganancia de servo y latencia. Mantén un conjunto de evaluación fijo para detectar regresiones.

## 5. Isaac Sim

Sigue [isaac/README.md](../isaac/README.md). Mantén exactamente el mismo contrato: base diferencial, acción de 16 dimensiones, nombres de articulación y cámara de cuello.
