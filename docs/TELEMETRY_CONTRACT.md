# Contrato de telemetría para teleoperación y datos

El enlace de Isaac Lab que inspira esta ampliación destaca teleoperación de dos
brazos, base móvil y recogida de datos. Este repositorio conserva esas ideas
como un contrato propio y verificable, sin reutilizar código ajeno ni afirmar
validación sobre el robot físico.

## Objetivo

Todos los episodios simulados usan el esquema `xlerobot_episode_v1`. MuJoCo es
la fuente actual; Isaac Lab y un puente físico futuro deberán producir las
mismas claves, unidades y orden de acción.

| Campo | Forma | Significado |
| --- | --- | --- |
| `timestamp_s` | `(T,)` | Tiempo de control, en segundos y desde cero. |
| `observation` | `(T, N)` | Observación del entorno antes de ejecutar cada acción. |
| `action` | `(T, 16)` | Acción normalizada según `action_names`. |
| `qpos`, `qvel` | `(T, *)` | Estado MuJoCo posterior al paso; radianes y rad/s salvo ruedas. |
| `neck_rgb` | opcional `(T, H, W, 3)` | Imagen RGB de la cámara del cuello. |
| `reward`, `success` | `(T,)`, escalar | Métrica de la tarea y resultado del episodio. |
| `source` | escalar | Procedencia: experto IK, política, Isaac Lab o hardware. |

## Orden de acción

1. `base_forward`, `base_turn`
2. Seis articulaciones/pinza izquierdas
3. Seis articulaciones/pinza derechas
4. `head_pan`, `head_tilt`

El orden completo vive en `xlerobot_twin.episode.ACTION_NAMES` y se exporta
junto al episodio. Así se evita inferir nombres de columnas por posición.

## Uso

Generar demostraciones de IK, con cámaras:

```powershell
python scripts/record_expert.py --episodes 20 --images
```

Generar exploración aleatoria para probar el pipeline:

```powershell
python scripts/record_rollouts.py --episodes 10 --images
```

Cada archivo `.npz` es autocontenido. Antes de convertirlo a LeRobotDataset o
entregarlo a Isaac Lab, valida: misma longitud `T` para todas las series,
`action.shape[1] == 16`, timestamps monótonos y `source` identificable.

## Límite de seguridad

El contrato no es un protocolo de control del robot real. Un puente de hardware
debe añadir watchdog, parada física, límites medidos, mapeo de signos/ceros y
registro de latencia antes de aceptar una sola acción.
