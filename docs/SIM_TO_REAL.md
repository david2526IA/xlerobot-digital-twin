# Plan sim-to-real

1. **Identidad mecánica:** validar geometría, signo de articulaciones, radio/separación de ruedas y límites contra el robot.
2. **Identidad dinámica:** ajustar masa, centro de masa, fricción, ganancia/latencia de los STS3215 y control diferencial a registros reales.
3. **Identidad visual:** medir intrínsecas/extrínsecas de cámara, exposición y retardo; aleatorizar luz, texturas, fondo, objetos y ruido.
4. **Política:** entrenar primero tareas estacionarias, con acción y observación idénticas a LeRobot; transferir a baja velocidad y registrar fallos.
5. **Seguridad:** topes software, watchdog, parada física y operador presente. Ningún checkpoint del catálogo está aprobado para autonomía física.
