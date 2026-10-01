# Migración reproducible a Ubuntu

No copies `.venv`, cachés de Isaac ni rutas generadas en Windows. El repositorio,
los MJCF, las mallas y las configuraciones son portables; los entornos y el USD se
regeneran en Ubuntu.

## 1. Clonar y verificar MuJoCo

Requisitos: Ubuntu 22.04/24.04, Git, Python 3.12 y controladores gráficos. Para el
visor local también hacen falta las bibliotecas GLFW/OpenGL del sistema.

```bash
git clone https://github.com/david2526IA/xlerobot-digital-twin.git
cd xlerobot-digital-twin
chmod +x scripts/*.sh isaac/*.sh
./scripts/bootstrap.sh
./scripts/verify.sh
```

Ver el robot:

```bash
source .venv/bin/activate
python scripts/run_mujoco.py
```

Entrenar y evaluar PPO:

```bash
./scripts/train.sh 300000 outputs/models/ppo_reach
```

## 2. Isaac Sim en Ubuntu

Instala en Ubuntu una versión de Isaac Sim compatible con el controlador NVIDIA.
No copies `C:\isaacsim`: usa la distribución Linux. Suponiendo que está en
`~/isaacsim`:

```bash
./isaac/import.sh "$HOME/isaacsim"
./isaac/open.sh "$HOME/isaacsim"
```

El primer comando regenera y valida `isaac/generated/xlerobot/xlerobot.usda`; el
segundo lo abre en una ventana visible.

## 3. Transferir resultados opcionales

Los checkpoints y datasets están ignorados por Git. Si quieres conservarlos, copia
por separado `outputs/models/` y `datasets/` mediante un disco o `rsync`. No copies
`.venv`, `__pycache__`, `isaac/generated` ni las cachés de NVIDIA.

Después de la transferencia vuelve a ejecutar `./scripts/verify.sh`. Un resultado
válido debe mostrar los actuadores, cámaras, sitios de pinza, tests y rollout sin
errores.
