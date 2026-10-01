# Hoja de ruta verificable: XLeRobot 0.4 servo de dos ruedas

## Objetivo y variante congelada

El objetivo es reproducir el **XLeRobot 0.4.0 servo dual-wheel**: dos brazos
SO-101, cuello pan/tilt, cámara de cabeza, dos ruedas motrices accionadas por
servos Feetech STS3215 y ruedas auxiliares de caminador de 5 pulgadas. La
variante brushless no se mezclará con esta definición; será otro perfil porque
sus motores, transmisión y controlador son diferentes.

La fuente oficial no contiene actualmente un URDF completo de la v0.4. El URDF
de ManiSkill corresponde al diseño anterior y el MuJoCo oficial todavía modela
la base omni de tres ruedas. Por ello, un URDF v0.4 debe reconstruirse a partir
del CAD y del controlador oficial y después validarse con mediciones físicas.

## Fuentes congeladas

La auditoría inicial se hizo contra el commit oficial
`749abc837d5d771f26aeff961009c290e574b024` de
[Vector-Wangel/XLeRobot](https://github.com/Vector-Wangel/XLeRobot).

| Evidencia | Fuente oficial | Qué permite afirmar |
| --- | --- | --- |
| Diseño v0.4 | `hardware/step/XLeRobot_040/XLeRobot040_dualwheelbase.step` | Geometría de la base servo nueva |
| Diseño superior | `XLeRobot040_armbase.step` y `XLeRobot040_neck_refined.step` | Montaje modular de brazos y cuello compacto |
| Piezas imprimibles | `hardware/XLeRobot_0_4_0_extra.stl` | Piezas adicionales de la versión publicada |
| Configuración de base | `software/src/robots/xlerobot_2wheels/` | Radio 0,05 m, vía 0,25 m y cinemática diferencial |
| Montaje | [Dual wheel Assembly](https://xlerobot.readthedocs.io/en/latest/hardware/getting_started/assemble_2wheel.html) | Dos ruedas, ruedas auxiliares de 5 pulgadas y diferencias respecto a 0.3 |
| Ausencia de URDF | [Issue oficial #131](https://github.com/Vector-Wangel/XLeRobot/issues/131) | No existe todavía un URDF v0.4 publicado que se pueda asumir exacto |
| Teleoperación | `software/examples/5_xlerobot_teleop_xbox.py` y `XLeVR/` | Referencias oficiales para Xbox y VR |

## Estado real al comenzar

| Componente | Estado | Veredicto |
| --- | --- | --- |
| Cinemática diferencial | Radio y vía coinciden con el controlador oficial | Utilizable como punto de partida |
| Dos ruedas motrices | Existen joints y actuadores físicos en MuJoCo | Funcional, pendiente de identificación dinámica |
| Brazos, pinzas y cuello | Articulados, con límites y actuadores | Funcionales, límites pendientes de contraste físico |
| Aspecto visual | Conserva mallas de cesta/ruedas del modelo anterior | **No representa todavía el diseño exterior 0.4** |
| URDF v0.4 | No existe upstream ni aquí como descripción canónica | Hay que construirlo |
| Isaac Sim | USD importable con 16 joints | La cámara no se recrea aún en USD y falta validar la base en PhysX |
| Mando | Base, cuello y pinzas tienen control básico | Faltan brazos, dead zone, dead-man, perfiles y prueba física de mando |
| RL/datasets | Gymnasium, PPO/CEM y exportación básica existen | Pipeline funcional, tarea y política todavía no validadas |
| VR | Diseño documentado | No implementado ni probado con visor real |

## Orden de ejecución

No se pasa de etapa hasta cumplir sus criterios de aceptación. Los entregables
se mantienen reproducibles tanto en Windows como en Ubuntu.

### Etapa 0 — Contrato del robot y trazabilidad

1. Copiar al repositorio sólo los CAD/assets oficiales necesarios, conservando
   licencia, URL y commit de origen.
2. Crear un manifiesto máquina-legible por parámetro con estados `official`,
   `cad-derived`, `measured` o `provisional`.
3. Congelar nombres, unidades, ejes, frames y orden de las 16 acciones:
   12 brazos/pinzas, 2 cuello y 2 ruedas.
4. Separar geometría visual, colisión simplificada e inercia.

Criterio: ningún número físico aparece sin valor, unidad, fuente y nivel de
confianza.

### Etapa 1 — Descripción v0.4 canónica y aspecto correcto

1. Abrir los tres STEP oficiales y exportar cada pieza rígida a STL/OBJ/USD sin
   perder escala.
2. Definir `base_link`, ruedas izquierda/derecha, apoyos pasivos, bases de
   brazos, brazos SO-101, cuello y frame óptico.
3. Crear el URDF/Xacro v0.4 desde cero; no renombrar el URDF 0.3.
4. Generar visuales v0.4 y colisiones convexas simples.
5. Generar MuJoCo e Isaac desde el mismo manifiesto/árbol cinemático.
6. Añadir pruebas automáticas de dimensiones, ejes, límites y transformaciones.

Criterio: superposición CAD/sim sin diferencias estructurales, dos ruedas
motrices reales, apoyos pasivos correctos y paridad de poses MuJoCo/Isaac.

### Etapa 2 — Física, límites y locomoción

1. Aplicar límites mecánicos y de velocidad de cada STS3215.
2. Introducir masas, centros de masa e inercias CAD; marcar como provisionales
   batería, cesta, ordenador y cableado hasta pesarlos.
3. Modelar par máximo, reducción, damping, fricción estática/dinámica, saturación
   y latencia de control.
4. Modelar ruedas motrices cilíndricas y apoyos pasivos, sin deslizamiento
   lateral artificial.
5. Validar avance, retroceso, giro sobre el centro, frenado y paso por pequeños
   obstáculos.

Criterio inicial de simulación: 10 rectas de 2 m con error menor del 2 %, 10
giros de 360° con error menor de 3° y ausencia de energía/contactos inestables.
La exactitud sim-to-real sólo se acepta después de repetirlo con el robot real.

### Etapa 3 — Teleoperación Xbox completamente funcional en este PC

1. Detectar y reconectar mandos mediante SDL/Pygame, con perfil Xbox explícito.
2. Stick izquierdo: velocidad lineal y angular diferencial.
3. Sticks, botones modificadores y gatillos: ambos brazos, cuello y pinzas.
4. Añadir dead zone, curvas suaves, límites de velocidad/aceleración, botón
   dead-man, parada inmediata y vuelta a home.
5. Mostrar en pantalla mando detectado, modo activo y comandos enviados.
6. Ejecutar una prueba automática del mapeo y una prueba manual completa.

Criterio: desde un mando Xbox se puede conducir, girar, mover ambos brazos y
cuello, abrir/cerrar ambas pinzas y parar con seguridad, sin editar código.

### Etapa 4 — Dataset desde simulación

1. Unificar observaciones: posiciones/velocidades, acción, pose de base, cámaras,
   timestamps, estado de tarea y metadatos de dominio.
2. Grabar episodios de teleoperación Xbox y de expertos programáticos.
3. Exportar LeRobotDataset v3 con RGB de cuello y, si se usa, cámaras de muñeca.
4. Añadir reproducción determinista y visor de episodios.
5. Validar sincronía imagen/acción y ejecutar un round-trip grabar-cargar-reproducir.

Criterio: un comando crea un dataset reproducible que LeRobot puede abrir y que
reproduce las acciones sin cambios de nombres ni unidades.

### Etapa 5 — RL entrenable y evaluable

1. Separar tareas: navegación, alcance, agarre, pick-and-place y tarea móvil.
2. Definir observaciones, acciones, recompensa, terminación y métricas por tarea.
3. Vectorizar entornos y añadir randomización de masas, fricción, latencia,
   cámara, luces y texturas.
4. Entrenar PPO/SAC para control de bajo nivel y mantener VLA/imitación como
   pipeline separado.
5. Evaluar con semillas retenidas y publicar tasa de éxito, no sólo retorno.

Criterio: `train -> checkpoint -> evaluate` funciona de cero en Windows/Ubuntu;
una política sólo se etiqueta como utilizable al superar el umbral de éxito de
su tarea en semillas no vistas.

### Etapa 6 — Paridad completa con Isaac Sim

1. Crear articulación PhysX, drives y límites equivalentes al MJCF.
2. Configurar controlador diferencial sobre las dos ruedas, no movimiento
   cinemático directo de la base.
3. Recrear cámara RGB/depth en el frame del cuello con intrínsecas configurables.
4. Añadir escenas/tareas de Isaac Lab y exportación de observaciones compatible.
5. Comparar las mismas trayectorias y poses contra MuJoCo.

Criterio: comandos idénticos producen juntas, base y cámara equivalentes dentro
de tolerancias documentadas.

### Etapa 7 — VR real y visión desde el cuello

1. Usar OpenXR como capa de entrada común; probar primero poses de HMD y mandos.
2. Resolver IK bimanual con límites, singularidades, colisiones y clutch/recentrado.
3. Mapear gatillos a pinzas y stick a base diferencial con dead-man.
4. Renderizar la cámara del cuello en el visor; modo inicial monoscópico en panel
   virtual y modo estereoscópico sólo si se definen dos cámaras físicas/virtuales.
5. Medir latencia extremo a extremo y mantener una salida segura si se pierde el
   tracking o la conexión.

Criterio: el usuario ve la cámara simulada, mueve base/brazos/pinzas y el robot
se detiene ante pérdida de tracking, todo probado con el visor especificado.

### Etapa 8 — Identificación y sim-to-real

1. Pesar subconjuntos y medir centros de masa, holguras y geometría real.
2. Calibrar ceros, signos, límites y transformación base-cámara.
3. Identificar respuesta a escalón, velocidad máxima, fricción y latencia.
4. Ajustar parámetros contra logs físicos sin usar datos de evaluación.
5. Añadir adaptador LeRobot con watchdog, límites y parada física.
6. Validar suspendido, después a baja velocidad y finalmente en suelo libre.

Criterio final: se cumplen las tolerancias de `CALIBRATION_PROTOCOL.md`, hay
trazabilidad de cada parámetro y una prueba de regresión compara sim y real.

## Qué significa “gemelo exacto”

No basta con que la forma se parezca. Para llamarlo gemelo digital exacto deben
estar medidos o demostrados:

- dimensiones, transforms y ceros articulares;
- límites mecánicos, velocidad, par y respuesta del controlador;
- masa, centro de masa e inercia de cada conjunto relevante;
- fricción y deformación de ruedas, apoyos y pinzas;
- holgura de transmisión, saturación, ruido y latencia;
- intrínsecas, distorsión, exposición y extrínsecas de todas las cámaras;
- carga real: batería, ordenador, cableado y objetos transportados;
- validación cuantitativa con trayectorias repetibles del robot físico.

Hasta completar la etapa 8, el nombre correcto es **modelo digital v0.4 basado
en CAD oficial y progresivamente calibrado**, no réplica física exacta.

## Próxima ejecución concreta

La siguiente entrega es la Etapa 0 + Etapa 1: importar los CAD v0.4 oficiales,
sustituir las mallas antiguas, crear la descripción canónica y demostrar visual
y cinemáticamente las dos ruedas. Después se cierra la Etapa 3 en este PC para
que el mando Xbox controle el robot completo antes de entrenar o grabar datos.
