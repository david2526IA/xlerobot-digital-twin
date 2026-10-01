# Protocolo de fidelidad del gemelo 0.4

Este gemelo separa parámetros **confirmados** de parámetros **a identificar**.
Los confirmados son: base diferencial, ruedas nominales de 5 pulgadas
(`0.0635 m` de radio geométrico), radio efectivo de control `0.050 m`, distancia
entre ejes de rueda `0.250 m`, dos SO-101 de 6 acciones y dos motores de cuello.
El diámetro procede de la guía/BOM 0.4 y el radio efectivo/vía del controlador
oficial `xlerobot_2wheels`. La diferencia entre radio geométrico y efectivo se
mantiene explícita y debe identificarse con pruebas de rodadura.

## Medición obligatoria en el robot real

| Bloque | Medición | Criterio de aceptación |
| --- | --- | --- |
| Base | 10 rectas de 2 m y 10 giros de 360° | error longitudinal < 2 %, yaw < 3° |
| Brazos | 20 poses, efector con marcador | RMSE de posición < 10 mm |
| Cuello/cámara | tablero Charuco y transformada base-cámara | reproyección < 1 px |
| Dinámica | escalón de rueda y 6 articulaciones | tiempo/overshoot dentro de 10 % |
| Contacto | pinzar objeto de masa conocida | éxito y deslizamiento coherentes |

Guarda los resultados en `calibration/measurements.yaml` y actualiza los parámetros de MuJoCo sólo con resultados medidos.

## Cámara de cuello

`neck_rgb` está ligado al marco óptico del cuello. El campo de visión de 60° es intencionalmente provisional: no debe usarse para entrenamiento visual sim-to-real hasta sustituirlo por `fx`, `fy`, `cx`, `cy`, resolución, distorsión y latencia de la cámara instalada.
