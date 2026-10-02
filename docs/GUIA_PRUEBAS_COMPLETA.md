# Guía completa de pruebas del gemelo XLeRobot 0.4

Esta guía permite comprobar, en orden, instalación, geometría, física,
teleoperación, cámaras, datasets y entrenamiento. No conectes todavía el robot
real: todos los comandos de este documento actúan únicamente sobre simulación.

## 1. Estado actual y límites de fidelidad

El repositorio contiene un gemelo funcional con 16 articulaciones móviles:
ruedas izquierda/derecha, seis acciones por brazo y pan/tilt del cuello. Las
ruedas físicas se representan con 127 mm de diámetro y 50 mm de ancho. Su vía
provisional es 0,500 m; el radio efectivo de 0,050 m y `wheelbase` de 0,250 m
del controlador oficial se mantienen separados.

La geometría, los límites, las cámaras y el software se pueden probar ahora.
Para llamarlo gemelo calibrado todavía faltan medidas directas de vía y offsets,
masa/inercia de cada conjunto, fricción, holgura, respuesta de motores y
calibración intrínseca/extrínseca de la cámara.

## 2. Validación automática

Desde PowerShell, en la raíz del repositorio:

```powershell
.\scripts\verify.ps1
```

El resultado correcto termina con `10 passed` y `Verification complete`. La
validación comprueba el MJCF, las mallas CAD, el URDF, los 16 actuadores, la
cámara del cuello, la lógica del mando y un episodio de dataset.

## 3. Inspección visual de las ruedas

Regenera las vistas:

```powershell
.\.venv\Scripts\python.exe scripts\render_twin_snapshot.py
```

Abre `outputs/xlerobot_v04_front.png`. Deben verse dos neumáticos completos
fuera de los laterales del carro, sus cubos metálicos y dos carcasas oscuras
junto a los soportes. No debe aparecer la antigua carcasa CAD centrada.

## 4. MuJoCo y teleoperación

Conecta un mando Xbox, Switch Pro o compatible antes o después de arrancar:

```powershell
.\.venv\Scripts\python.exe scripts\run_mujoco.py
```

Mantén `A` pulsado para habilitar movimiento. Sin bumper, el stick izquierdo
mueve la base y el derecho el cuello. `LB` selecciona el brazo izquierdo, `RB`
el derecho y ambos activan modo bimanual. El D-pad mueve el roll de muñeca y los
gatillos la pinza. `B` enclava el E-stop; `A+Start` lo libera y vuelve a home.

Prueba mínima:

1. Sin pulsar `A`, mueve todos los sticks: nada debe moverse.
2. Mantén `A` y avanza lentamente: ambas ruedas deben girar igual.
3. Mantén `A` y gira: las ruedas deben girar en sentidos opuestos.
4. Suelta `A`: la base debe detenerse inmediatamente.
5. Pulsa `B`: nada debe responder hasta pulsar `A+Start`.
6. Comprueba cuello, ambos brazos y las dos pinzas.

Para usar la vista de cámara:

```powershell
.\.venv\Scripts\python.exe scripts\run_mujoco.py --camera neck_rgb
```

## 5. Isaac Sim y teleoperación

Regenera el USD desde el URDF canónico:

```powershell
.\isaac\import.ps1 -IsaacRoot "C:\isaacsim"
```

El importador selecciona la revisión recién creada, añade `neck_rgb` y
`neck_depth` y valida 16 joints. Para una comprobación sin ventana:

```powershell
C:\isaacsim\python.bat .\isaac\teleop_gamepad.py --headless --smoke-steps 10
```

Debe imprimir `Validated articulation: 16 joints` y terminar con código cero.
Para manejarlo con ventana y mando:

```powershell
C:\isaacsim\python.bat .\isaac\teleop_gamepad.py
```

La asignación y los mecanismos de seguridad son los mismos que en MuJoCo. Los
errores de `isaacsim.robot.experimental.wheeled_robots` y Jinja2 que aparecen en
esta instalación son de una extensión opcional de Isaac 6.0.1; este lanzador no
la utiliza. La validación real es el mensaje de 16 joints y el código de salida.

## 6. Crear un dataset simulado

Dataset básico de rollouts:

```powershell
.\.venv\Scripts\python.exe scripts\record_rollouts.py --episodes 10 --output outputs\dataset_prueba
```

Dataset con el experto incluido:

```powershell
.\.venv\Scripts\python.exe scripts\record_expert.py --episodes 10 --max-attempts 50 --output outputs\dataset_experto
```

Antes de usar imágenes para sim-to-real hay que calibrar la cámara real y añadir
randomización de iluminación, texturas, exposición, ruido, latencia y pose.

## 7. Prueba de entrenamiento

Entrenamiento PPO corto para validar el pipeline:

```powershell
.\.venv\Scripts\python.exe scripts\train_rl.py --action-mode right_arm --timesteps 2048 --output outputs\models\ppo_prueba
.\.venv\Scripts\python.exe scripts\evaluate_rl.py outputs\models\ppo_prueba.zip --action-mode right_arm --episodes 5
```

Que el entrenamiento se ejecute no significa que la política esté lista para el
robot real. Primero deben cerrarse las mediciones físicas, la tarea, recompensa,
observaciones, randomización y criterios de evaluación.

## 8. Mediciones necesarias para cerrar el gemelo

Registra en `calibration/measurements.yaml`:

- distancia centro-a-centro entre ruedas y posición del eje respecto al carro;
- diámetro y ancho reales del neumático bajo carga;
- masa total y masas/centros de gravedad de base, brazos y cuello;
- límites mecánicos y cero real de cada servo;
- velocidad, par, retardo, fricción, backlash y respuesta a escalón;
- intrínsecas, distorsión, resolución, FOV y pose base-cámara;
- diez rectas de 2 m, diez giros de 360 grados y pruebas de agarre.

Después se actualizan los parámetros, se repiten todas las pruebas y sólo se
promueve una política a hardware con límites de velocidad, E-stop físico y una
zona de ensayo despejada.

