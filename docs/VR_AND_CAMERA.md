# VR, pinzas y cámara del cuello

## Estado actual

El modelo incluye articulaciones `head_pan`, `head_tilt`, `Jaw_L` y `Jaw_R`. El visor estándar de MuJoCo no proporciona por sí solo un runtime OpenXR ni streaming estereoscópico; esa integración necesita un PC con SteamVR/OpenXR y un visor compatible. No se debe anunciar como lista sin probarla en ese hardware.

## Implementación prevista

1. Añadir cámaras MuJoCo `neck_rgb_left` y `neck_rgb_right` unidas a `head_camera_link`, usando las intrínsecas medidas de la cámara real.
2. Un adaptador OpenXR publica, a 60--90 Hz, poses de ambos controladores y la pose HMD.
3. Resolver IK de cada brazo contra las poses de los controladores, limitar velocidad/aceleración y mapear gatillo a `Jaw_L/Jaw_R`.
4. Renderizar las dos cámaras en las capas OpenXR y aplicar la transformación cámara--HMD calibrada.
5. Registrar simultáneamente poses, imágenes, acciones y latencias en LeRobotDataset.

## Calibración imprescindible

Mide transformaciones `base->neck`, `neck->camera`, `wrist->gripper` y la orientación cero de todos los STS3215. Valida con un marcador visible: el efector simulado y el físico deben coincidir antes de permitir pinzar objetos.

El repositorio upstream de XLeRobot contiene teleoperación VR y simulación ManiSkill; se usa como referencia de interfaz, no como validación del hardware 0.4.
