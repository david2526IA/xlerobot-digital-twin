# Teleoperación Xbox y Switch

Conecta el mando y ejecuta:

```powershell
.\.venv\Scripts\python.exe scripts\run_mujoco.py
```

Para Isaac Sim 6.0.1, después de importar el USD:

```powershell
C:\isaacsim\python.bat .\isaac\teleop_gamepad.py
```

Los dos adaptadores usan exactamente la misma lógica de seguridad y asignación.

GLFW normaliza mandos Xbox, Switch Pro y compatibles. El mando se puede conectar
después de arrancar y se reconecta automáticamente.

| Control | Sin bumper | Con LB | Con RB |
| --- | --- | --- | --- |
| Mantener A | Dead-man necesario | Dead-man necesario | Dead-man necesario |
| Stick izquierdo | Avance y giro | Pan y pitch brazo izquierdo | Pan y pitch brazo derecho |
| Stick derecho | Pan y tilt de cabeza | Codo y pitch de muñeca izquierdo | Codo y pitch de muñeca derecho |
| D-pad izquierda/derecha | — | Roll de muñeca | Roll de muñeca |
| LT / RT | — | Abrir / cerrar pinza | Abrir / cerrar pinza |
| LB + RB | — | Control bimanual simultáneo | Control bimanual simultáneo |
| B | E-stop enclavado | E-stop enclavado | E-stop enclavado |
| A + Start | Quitar E-stop y volver a home | Igual | Igual |

Al soltar A la base se detiene inmediatamente y las articulaciones mantienen su
último objetivo. Para ver directamente la cámara del cuello:

```powershell
.\.venv\Scripts\python.exe scripts\run_mujoco.py --camera neck_rgb
```

La posición, orientación y FOV están listos para simulación, pero las
intrínsecas y extrínsecas exactas siguen pendientes de calibración con el robot
real.
