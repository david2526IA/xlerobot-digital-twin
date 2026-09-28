# Teleoperación con mando Switch

El script `scripts/run_mujoco.py` usa GLFW, por tanto funciona con un Pro Controller, Joy-Con emparejados como mando o cualquier gamepad expuesto por el sistema.

1. Empareja el mando en el sistema operativo antes de arrancar MuJoCo.
2. Ejecuta `python scripts/run_mujoco.py`; debe imprimir su nombre.
3. Stick izquierdo: avance/giro de la base. A/B controlan la pinza derecha; X/Y, la izquierda. Stick derecho: pan/tilt del cuello.

Los índices de botones difieren entre controladores. Imprime `joystick.get_name()` y ajusta los cuatro índices en el script si tu Switch los anuncia de otro modo. La velocidad y los límites son deliberadamente conservadores; añade control de brazos solo después de verificar signos y topes de cada eje.

La política de control separa acciones normalizadas de la implementación del mando. Esa misma interfaz permitirá sustituir el gamepad por un visor VR o por LeRobot en el robot físico.
