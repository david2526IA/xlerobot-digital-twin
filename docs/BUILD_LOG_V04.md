# Registro de construcción del gemelo XLeRobot 0.4

Este documento registra qué se hizo realmente, con comandos y resultados. No
sustituye la hoja de ruta: `ROADMAP_V04.md` describe lo pendiente y este archivo
documenta lo ejecutado.

## 2026-10-01 — Punto 1: incorporar las fuentes CAD oficiales

### Objetivo

Guardar dentro del proyecto los CAD necesarios para que el gemelo pueda
reconstruirse sin depender de que cambie el repositorio upstream.

### Procedimiento

1. Se clonó `https://github.com/Vector-Wangel/XLeRobot` y se fijó el commit
   `749abc837d5d771f26aeff961009c290e574b024`.
2. Se copiaron, sin modificarlos, los tres STEP de `hardware/step/XLeRobot_040`
   y el STL oficial de piezas extra.
3. Se conservó la licencia Apache-2.0 upstream.
4. Se calcularon hashes SHA-256 y se registraron en
   `third_party/xlerobot_official/SOURCE.yaml`.
5. Se añadió `scripts/verify_official_assets.py` para detectar archivos
   ausentes o modificados.
6. Se añadió `scripts/inspect_v04_cad.py` para auditar sólidos, dimensiones,
   volumen y centro de masa usando FreeCAD, antes de separar las piezas.

### Repetición y verificación

```powershell
cd C:\Users\farqu\OneDrive\Documentos\ChatGPT\xlerobot
.\.venv\Scripts\python.exe scripts\verify_official_assets.py
```

Resultado esperado:

```text
PASS: 4 official CAD assets | commit=749abc837d5d771f26aeff961009c290e574b024 | license=Apache-2.0
```

### Resultado

Los archivos fuente ocupan aproximadamente 28,5 MB y quedan versionados junto
al proyecto. Ningún fichero derivado ha reemplazado los originales.

### Siguiente punto

Separar las piezas rígidas y móviles del STEP, decidir los frames mecánicos y
exportar mallas derivadas con escala en metros. En particular, las ruedas no se
fusionarán con el chasis porque deben conservar joints de rotación físicos.

## 2026-10-01 — Punto 2: separar piezas y exportar mallas métricas

### Hallazgo previo

El STEP `XLeRobot040_dualwheelbase.step` es una presentación explotada. Sus
piezas están desplazadas para verse por separado; esas posiciones no son las
transformaciones del robot montado. Usarlas directamente habría creado una base
con una vía falsa.

### Procedimiento

1. Se inspeccionaron todos los sólidos `Part::Feature` con FreeCAD 1.1.
2. Se clasificaron en chasis rígido, interfaces de rueda, rotores móviles, base
   superior, cuello, gimbal, cámara y pinza blanda opcional.
3. Se exportaron 16 STL binarios. Cada componente usa un frame local centrado en
   su bounding box y vértices expresados numéricamente en metros.
4. `base_chassis.stl` excluye los dos rotores y sus interfaces.
5. Se mantuvieron los nombres neutrales `drive_side_a` y `drive_side_b`: la
   vista explotada no demuestra qué pieza es izquierda o derecha.
6. Se definió la convención mecánica REP-103 en `twin/v04_frames.yaml`; la vía
   oficial fija `y=+/-0.125 m`, mientras offsets no publicados quedan como
   `pending_assembly`.
7. Se añadió validación de formato binario, escala, hashes, dimensiones,
   triángulos y separación de ruedas.

### Repetición

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\python.exe" scripts\export_v04_meshes.py
.\.venv\Scripts\python.exe scripts\validate_v04_meshes.py
```

### Resultado y discrepancia abierta

Se obtuvieron 16 mallas separadas, incluidas dos piezas con rol
`moving_wheel`. El componente circular del CAD tiene 60 mm de diámetro de
bounds, mientras el controlador oficial declara un radio efectivo de 50 mm.
Puede ser un hub/interfaz y no la banda de rodadura definitiva. Se conservarán
ambas evidencias hasta contrastarlas con el montaje y una medición física.

### Siguiente punto

Ensamblar las piezas en el árbol cinemático v0.4 y crear el URDF/Xacro. En ese
momento se asumió una vía física de 0,25 m; la corrección fotográfica del
2026-10-02 demuestra que ese valor pertenece al controlador.

## 2026-10-01 — Punto 3: ensamblaje canónico e integración

### Descripción canónica

Se añadió `scripts/generate_v04_urdf.py`, que genera de forma determinista
`robot_description/xlerobot_v04.urdf`. El árbol contiene 22 links, 21 joints y
16 articulaciones móviles: dos ruedas, doce articulaciones de brazos/pinzas y
dos del cuello. Usa REP-103 y separa magnitudes físicas de parámetros efectivos
del controlador para no confundirlos:

- radio físico de neumático: 0,0635 m (rueda comercial de 5 pulgadas);
- radio efectivo del controlador oficial: 0,05 m.
- vía física provisional reconstruida de fotografías: 0,460 m;
- `wheelbase` efectivo del controlador oficial: 0,250 m.

Los 60 mm observados en las piezas STEP corresponden a la interfaz/rotor y no
se usan como diámetro exterior del neumático.

### MuJoCo

El MJCF incorpora el chasis, soportes, rotores, base superior, cuello refinado,
gimbal y soporte de cámara del CAD 0.4. Las ruedas son cuerpos dinámicos
independientes con juntas y actuadores. Se mantienen los 16 actuadores y las
cámaras de cuello. Una prueba automática comprueba avance y giro por contacto,
sin trasladar cinemáticamente la base.

### Isaac Sim

La importación parte ahora del mismo URDF canónico mediante el importador URDF
oficial de Isaac Sim. Mantiene base flotante y joints fijos, y un postproceso
añade las cámaras RGB y depth al frame óptico. El pipeline se ejecutó en este PC
con Isaac Sim 6.0.1; el USD resultante fue validado con 16 joints revolute y las
dos cámaras.

### Qué continúa siendo provisional

Los STEP oficiales se publicaron como vistas explotadas y no fijan todas las
transformaciones ensambladas. Los offsets no publicados se reconstruyeron con
las dimensiones CAD, fotografías y el modelo funcional existente. Siguen
necesitando medición del robot real: masas e inercias, posición longitudinal
exacta del eje, fricción y deformación de neumáticos, holguras, latencia y
óptica/extrínsecas exactas de la cámara.

### Siguiente punto

Completar la teleoperación Xbox con dead-man, brazos, cuello y pinzas, usando la
misma interfaz de 16 acciones en MuJoCo y, después, en Isaac Sim.

## 2026-10-02 — Corrección con fotografías reales y teleoperación

Las fotografías `IMG_4064.DNG` y `IMG_4065.DNG` muestran las ruedas grandes en
los extremos exteriores del carro y los dos apoyos pasivos por dentro. Se dejó
de usar la posición explotada del STEP como ensamblaje, se adoptó una vía física
provisional de 0,460 m y se conservaron por separado los 0,250 m del controlador.

La cámara se corrigió eliminando un giro de 180° que sólo existía en el MJCF. El
cuerpo y la lente ahora están delante del soporte de tilt; la cámara neutral
mira en `+x` y su frame óptico cumple REP-103. MuJoCo y el URDF vuelven a tener
la misma transformación.

La teleoperación de mando ahora cubre base, cuello, los dos brazos y ambas
pinzas en MuJoCo e Isaac Sim. Incluye reconexión en caliente en MuJoCo, zona
muerta, curva suave, dead-man, E-stop enclavado y vuelta a home. Sus mapeos y
mecanismos de seguridad están cubiertos por pruebas automáticas; el adaptador de
Isaac abrió el USD regenerado, añadió suelo y validó los 16 joints durante una
prueba headless de diez pasos. Falta la prueba física con el mando del usuario.
