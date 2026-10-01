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
