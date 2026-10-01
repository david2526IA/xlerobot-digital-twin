# Procedencia

| Recurso | Fuente | Uso |
| --- | --- | --- |
| Modelo MJCF y mallas | Vector-Wangel/MuJoCo-GS-Web | Base ejecutable de MuJoCo |
| Diseño 0.4 y STEP | Vector-Wangel/XLeRobot | Validación/reconstrucción geométrica |
| URDF ManiSkill | Vector-Wangel/XLeRobot | Referencia 0.3 de brazos; no base 0.4 |
| SmolVLA | lerobot/smolvla_base | Foundation model, requiere fine-tuning |
| pi0.5 bimanual | xuweiwu/pi05_bimanual_so101_lora | Referencia comunitaria de tarea |

Revisa la licencia y model card de cada checkpoint antes de redistribuirlo. Los pesos no se incluyen: se descargan de manera explícita con `scripts/download_model.py`.

El snapshot CAD oficial usado para la reconstrucción v0.4 está fijado al commit
`749abc837d5d771f26aeff961009c290e574b024`. Sus rutas originales, hashes y
licencia se conservan en `third_party/xlerobot_official/`.
