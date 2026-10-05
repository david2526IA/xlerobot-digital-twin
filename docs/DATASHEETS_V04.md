# Fichas técnicas y límites de lo publicado

## Valores incorporados

### Feetech STS3215 de 12 V

El BOM oficial de XLeRobot exige expresamente la variante de 12 V. La referencia
correcta es `ST-3215-C018`, no la variante C001 de 7,4 V.

| Dato a 7,4 V | Valor publicado | Uso en el gemelo |
| --- | --- | --- |
| Par de bloqueo | 30 kg·cm, aproximadamente 2,942 N·m | límite pico de referencia |
| Par nominal | 10 kg·cm, aproximadamente 0,981 N·m | referencia continua inicial |
| Velocidad sin carga | 0,222 s/60°, 45 RPM | límite cinemático inicial |
| Corriente de bloqueo | 2,7 A | dimensionado y protección |
| Masa | 55 ± 1 g | masa de cada servo |
| Dimensiones | 45,2 × 24,7 × 35 mm | comprobación geométrica |
| Reducción | 1:345 | modelo del accionamiento |
| Holgura declarada | como máximo 0,5° | mínimo de backlash; el conjunto puede tener más |
| Resolución | 0,088° por pulso | cuantización del encoder |
| Actualización máxima | 1 ms | capacidad del servo, no frecuencia garantizada del sistema |

El antiguo `forcerange=3.35` superaba el pico publicado. Se ha sustituido por
`2.94 N·m`; para operación sostenida todavía debe definirse un límite térmico
más conservador mediante ensayos.

### Carro IKEA RÅSKOG

Para el artículo 306.297.11, IKEA publica 35 × 45 × 77 cm, carga máxima de
18 kg y 6 kg por nivel. Los 6,83 kg publicados corresponden al paquete y no se
adoptan como masa dinámica exacta del carro ensamblado.

### Ruedas de la versión 0.4

La guía oficial XLeRobot especifica ruedas universales de caminador de 5
pulgadas y rodamientos de 30 × 37 × 4 mm. Cinco pulgadas justifican un radio
nominal de 63,5 mm, pero el radio efectivo bajo carga, ancho, masa, compuesto y
fricción dependen de la rueda comprada y deben medirse.

### Brazos SO-101

El URDF publicado por TheRobotStudio contiene masas, centros de masa e inercias
por eslabón. Esos valores ya son la referencia usada por los brazos del modelo.
Siguen siendo valores derivados del CAD y pueden diferir por material de
impresión, relleno, tornillería, cables y cámaras de muñeca.

## Lo que ninguna ficha genérica puede resolver

- distancia entre centros de las ruedas una vez montadas;
- posición exacta del eje y los apoyos en este carro;
- masa y centro de gravedad del robot completo;
- batería, ordenador, controladoras, cableado y piezas impresas concretas;
- fricción rueda-suelo, deformación, holgura total y latencia;
- modelo, intrínsecas y pose exacta de la cámara instalada;
- ceros y topes seguros con los cables del robot real.

Estos parámetros dependen de la unidad montada. La ficha reduce el trabajo de
medición, pero no sustituye la identificación del sistema.
