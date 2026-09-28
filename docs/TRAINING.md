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

La ruta mínima de diagnóstico no necesita GPU ni PyTorch:

```powershell
python scripts/train_cem.py --iterations 40 --population 32
python scripts/evaluate_cem.py
```

CEM confirma que observaciones, acciones, recompensa y checkpoints están conectados,
pero no se considera una política competente salvo que su evaluación muestre éxito.
Para obtener una política utilizable usa PPO y aplica siempre un umbral de aceptación.

Para PPO de mayor escala:

```powershell
pip install -r requirements-rl.txt
python scripts/train_rl.py --timesteps 100000 --output outputs/models/ppo_reach
python scripts/evaluate_rl.py outputs/models/ppo_reach.zip --episodes 10
```

En GitHub, el workflow manual `train-ppo` entrena con cuatro entornos, evalúa 50
episodios sobre semillas separadas, rechaza políticas por debajo del umbral indicado
y conserva checkpoint, métricas y checkpoints intermedios como artefacto.

En Windows también puede hacerse instalación, entrenamiento y evaluación con un solo comando:

```powershell
.\scripts\train.ps1 -Timesteps 100000 -Output outputs/models/ppo_reach
```

El entrenador crea checkpoints periódicos en `outputs/models/ppo_reach_checkpoints`
y un manifiesto reproducible `ppo_reach.run.json`. Para continuar un checkpoint:

```powershell
.\scripts\train.ps1 -Timesteps 100000 -Output outputs/models/ppo_reach_continued `
  -Resume outputs/models/ppo_reach_checkpoints/ppo_reach_25000_steps.zip
```

Para registrar métricas en TensorBoard, instala `tensorboard` y añade
`--tensorboard-log outputs/tensorboard` al comando de entrenamiento.

La primera tarea es alcanzar el cubo con la base estacionaria junto a la mesa; las dos
acciones de base se reservan pero se ignoran durante esta fase. No usa agarre
asistido. Es el control de sanidad para cinemática, acciones, cámaras y recompensa.
La locomoción debe entrenarse como currículo separado antes de combinarlas. Después
se debe implementar agarre sólo cuando las pinzas y el contacto estén calibrados.

## 3. Demostraciones y VLA

Genera demostraciones competentes con el controlador IK incluido. Los intentos fallidos
se rechazan y no contaminan el dataset:

```powershell
python scripts/record_expert.py --episodes 100 --images --output datasets/expert/reach
```

Para probar solamente el formato también se pueden generar acciones aleatorias con
`python scripts/record_rollouts.py --episodes 10 --images`. Los `.npz` guardan
observación, acción, recompensa, imagen del cuello e instrucción sin esconder ninguna
conversión. Convierte las demostraciones al formato oficial v3 con:

```powershell
pip install -r requirements-lerobot.txt
python scripts/export_lerobot.py datasets/expert/reach
```

LeRobot exige `create`, `add_frame`, `save_episode` y finalmente `finalize`; omitir `finalize` deja Parquet incompleto. Los rollouts aleatorios sólo sirven para verificar el formato: para ACT/SmolVLA deben grabarse demostraciones competentes.

## 4. Randomización antes de sim-to-real

Por episodio, aleatoriza posición de cubo, iluminación, textura, masa, fricción, cámara, ganancia de servo y latencia. Mantén un conjunto de evaluación fijo para detectar regresiones.

## 5. Isaac Sim

Sigue [isaac/README.md](../isaac/README.md). Mantén exactamente el mismo contrato: base diferencial, acción de 16 dimensiones, nombres de articulación y cámara de cuello.
