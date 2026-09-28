# Entrenamiento paso a paso

En Windows, `scripts/bootstrap.ps1` instala y ejecuta el smoke test; `scripts/verify.ps1` valida MuJoCo, el paquete fuente para Isaac, Gymnasium y un rollout completo.

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

La ruta mínima verificada no necesita GPU ni PyTorch:

```powershell
python scripts/train_cem.py --iterations 40 --population 32
python scripts/evaluate_cem.py
```

Para PPO de mayor escala:

```powershell
pip install -r requirements-rl.txt
python scripts/train_rl.py --timesteps 100000 --output outputs/models/ppo_reach
python scripts/evaluate_rl.py outputs/models/ppo_reach.zip --episodes 10
```

La primera tarea es alcanzar el cubo; no usa agarre asistido. Es el control de sanidad para cinemática, acciones, cámaras y recompensa. Después se debe implementar una tarea de agarre sólo cuando las pinzas y el contacto estén calibrados.

## 3. Demostraciones y VLA

Genera primero episodios de prueba con cámara mediante `python scripts/record_rollouts.py --episodes 100 --images`. Los `.npz` guardan observación, acción, recompensa, imagen del cuello e instrucción sin esconder ninguna conversión. Convierte al formato oficial v3 con:

```powershell
pip install -r requirements-lerobot.txt
python scripts/export_lerobot.py datasets/raw/reach_random
```

LeRobot exige `create`, `add_frame`, `save_episode` y finalmente `finalize`; omitir `finalize` deja Parquet incompleto. Los rollouts aleatorios sólo sirven para verificar el formato: para ACT/SmolVLA deben grabarse demostraciones competentes.

## 4. Randomización antes de sim-to-real

Por episodio, aleatoriza posición de cubo, iluminación, textura, masa, fricción, cámara, ganancia de servo y latencia. Mantén un conjunto de evaluación fijo para detectar regresiones.

## 5. Isaac Sim

Sigue [isaac/README.md](../isaac/README.md). Mantén exactamente el mismo contrato: base diferencial, acción de 16 dimensiones, nombres de articulación y cámara de cuello.
