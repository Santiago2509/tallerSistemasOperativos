# Evidencias de ejecución

Resultados obtenidos al probar los cuatro ejercicios el **7 de octubre de
2026** en Windows, con Python 3.14.3 y psutil 7.2.2. Los tiempos dependen del
equipo y de la carga del sistema; son observaciones de estas ejecuciones, no
garantías para otras máquinas.

## Resumen

| Ejercicio | Prueba | Resultado |
| --- | --- | --- |
| Monitor de recursos | Dos muestras controladas con uso de RAM simulado al 90% y umbral de 80%. | Mostró CPU/RAM y escribió dos alertas en el log de prueba. |
| Caché de archivos | Archivo temporal de 4 MiB, solicitado tres veces. | Disco: 0,003809 s; primera lectura de caché: 0,000605 s; segunda lectura de caché: 0,000307 s. |
| Estrés de memoria | Límite solicitado de 16 MiB y observación durante 5 s. | Reservó 96.978 strings (estimado 16,0 MiB), se detuvo y liberó la reserva automáticamente. |
| Prioridad de procesos | Dos procesos con 2.000.000 de iteraciones cada uno. | Prioridad baja: 0,194036 s; Tiempo Real: 0,190503 s. En esta ejecución terminó primero Tiempo Real. |

## Detalle por ejercicio

### 1. Monitor de CPU y RAM

Se probó el ciclo del monitor proporcionando dos lecturas controladas con
`psutil` simulado. En ambas muestras, el uso de RAM reportado fue 90%, por
encima del umbral configurado de 80%. Se comprobó que el programa mostró las
métricas y agregó dos líneas de alerta al archivo de registro. Después se
simuló `Ctrl+C` y el monitor terminó correctamente.

La lectura del 90% fue simulada para comprobar la condición sin tener que
esperar a que el uso real del equipo superara el 80%.

### 2. Caché de archivos

Se creó un archivo temporal de prueba de 4.194.304 bytes (4 MiB) y se solicitó
tres veces:

```text
Solicitud 1: disco      | 0.003809 s | 4,194,304 bytes
Solicitud 2: caché RAM  | 0.000605 s | 4,194,304 bytes
Solicitud 3: caché RAM  | 0.000307 s | 4,194,304 bytes
Primera lectura / segunda lectura: 6.30x
```

Las dos solicitudes posteriores identificaron el origen como caché RAM. El
archivo usado en la prueba era temporal y se eliminó al terminar.

### 3. Reserva de memoria

La prueba se ejecutó con `--max-mb 16 --hold-seconds 5`. El programa calculó
un presupuesto seguro de 16 MiB y reportó:

```text
Objetos: 50,000 | estimado: 8.2 MiB | RAM disponible: 0.27 GiB
Objetos: 96,978 | estimado: 16.0 MiB | RAM disponible: 0.26 GiB
Reserva detenida con 96,978 strings.
Memoria liberada.
```

La reserva se detuvo en el límite y fue liberada automáticamente después de
la observación. El monitor informa la RAM disponible del sistema; estos datos
no son una captura independiente del Administrador de tareas.

**Alcance:** esta ejecución demuestra la reserva limitada y su liberación, pero
no confirma que Windows haya utilizado el archivo de paginación. Para
documentar ese comportamiento, hay que observar en el Administrador de tareas
la memoria física y la memoria confirmada mientras corre el programa. El uso
de paginación depende de la configuración y la presión de memoria del equipo.

### 4. Prioridad de procesos

Se ejecutó la comparación con 2.000.000 de iteraciones para cada proceso:

```text
baja         | 0.194036 s | 2,000,000 iteraciones | checksum 347464
tiempo_real  | 0.190503 s | 2,000,000 iteraciones | checksum 347464
Terminó primero: tiempo_real.
```

Ambos procesos produjeron el mismo checksum, confirmando que hicieron el mismo
cálculo. Tiempo Real terminó primero en esta ejecución, con una diferencia
pequeña. Una sola comparación no demuestra que Tiempo Real siempre vaya a
terminar primero: la carga del equipo, los permisos y otros factores pueden
cambiar el resultado.

La prueba requirió confirmar explícitamente la prioridad Tiempo Real. Windows
puede rechazar este cambio según los permisos del usuario. Esa prioridad puede
afectar la capacidad de respuesta del sistema; por eso el script limita las
iteraciones y exige confirmación.

## Verificaciones adicionales

- La sintaxis y el análisis de los cuatro scripts terminaron sin errores.
- Se verificaron las opciones de ayuda de los programas ejecutables.
- Las pruebas de RAM, caché y prioridad se ejecutaron con límites breves y
  controlados.
- No se agregan capturas inventadas ni resultados de paginación no observados.
