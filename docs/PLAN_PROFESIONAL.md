# Plan profesional del gemelo digital XLeRobot 0.4

## Regla de avance

Cada bloque termina con un artefacto, una prueba automática y una prueba manual.
No se generan datasets definitivos ni se comparan modelos preentrenados mientras
cambien la convención de ejes, el orden de acciones o la cámara.

## B0. Configuración y trazabilidad — completado

- Variante congelada `xlerobot_v0.4_servo_dualwheel`.
- CAD oficial fijado a un commit y manifiesto de mallas.
- Inventario de parámetros con valor, unidad, fuente, confianza y verificación.
- Plantilla privada de mediciones y auditoría automática de procedencia.

```powershell
.\.venv\Scripts\python.exe scripts\audit_model_parameters.py
```

`--require-measured` se reserva para la certificación sim-to-real y debe fallar
mientras existan valores provisionales.

## B1. Geometría y árbol cinemático 0.4 — funcional, pendiente de medir

Cerrar vía, rueda, eje, apoyos, bases de brazos, cuello, cámara y colisiones con
mediciones del robot físico. Criterio: URDF y MJCF comparten nombres, límites y
transformaciones; 20 poses coinciden dentro de 2 mm entre simuladores.

## B2. Física e identificación — siguiente bloque

Crear perfiles `nominal`, `measured` y `randomized` para masas, inercias,
STS3215, latencia, ruedas, apoyos, pinzas y frecuencias. Ensayos: recta, giro,
frenado, escalón articular, contacto y agarre. Sólo se denomina calibrado al
cumplir `CALIBRATION_PROTOCOL.md` con logs reales.

## B3. Teleoperación unificada — parcialmente completado

Adaptadores de teclado, Xbox/SDL, Switch Pro/SDL, Joy-Con/HID y OpenXR deben
producir el mismo comando normalizado y pasar por dead-man, E-stop, límites,
aceleración, watchdog y telemetría. MuJoCo e Isaac no tendrán mapeos separados.

## B4. Sensores y cámara

Calibrar intrínsecas, distorsión, extrínsecas, resolución, FPS, exposición,
timestamps y latencia. Criterio: reproyección menor de 1 px y sincronía
imagen-estado-acción documentada.

## B5. Escenas, tareas y métricas

Separar conducción, alcance, agarre, pick-and-place y manipulación móvil. Cada
tarea tendrá reset, observación, acción, recompensa, terminación y éxito.

## B6. Dataset profesional

Grabar teleoperación y expertos con metadatos, hash del modelo y parámetros.
Validar, reproducir y exportar LeRobotDataset v3 sin alterar frames, acciones,
timestamps ni imágenes.

## B7. Entrenamiento propio

CEM como prueba de cableado; PPO/SAC para control; ACT o SmolVLA para imitación.
Evaluar en semillas y escenas no vistas. Retorno de entrenamiento no sustituye
a tasa de éxito.

## B8. Modelos externos ya entrenados

Evaluar siempre en sandbox:

- `lerobot/smolvla_base`: base para fine-tuning;
- `xuweiwu/pi05_bimanual_so101_lora`: referencia bimanual SO-101;
- `madokalif/xlerobot-pi05-bottle`: candidato específico de XLeRobot;
- `lissajous/xlerobot-act-local-grasp-v1`: candidato ACT de agarre local.

Para cada uno: fijar revisión/licencia, inspeccionar features, adaptar de forma
explícita, verificar cámaras/normalización, ejecutar sin actuadores y evaluar en
sim. Las incompatibilidades se rechazan, nunca se corrigen silenciosamente.

## B9. Paridad Isaac Sim / Isaac Lab

Escena equivalente, drives PhysX, sensores, tareas Isaac Lab, teleoperación y
grabador con el mismo contrato. Comparar trayectorias con MuJoCo.

## B10. VR

Ruta principal en Ubuntu: Isaac Teleop/OpenXR o CloudXR, controlador 6-DoF con
clutch, IK bimanual, gatillos para pinzas y stick para base. Primero mostrar
`neck_rgb` en un panel monoscópico; después vista inmersiva. Pérdida de tracking
o red provoca parada.

## B11. Sim-to-real y aceptación final

Ajustar sólo con datos de identificación y reservar evaluación. Probar ruedas
elevadas, después velocidad mínima y finalmente suelo despejado, siempre con
E-stop físico y watchdog.

## Secuencia

`B0 -> B1 -> B2 -> B3 -> B4 -> B5 -> B6 -> B7 -> B8 -> B9 -> B10 -> B11`

