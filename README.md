# Taller de Sistemas Operativos

## Manipulación y monitoreo de recursos del sistema operativo

**Asignatura:** Sistemas Operativos  
**Código:** A_Sistemas_Operativos_2620_7647  
**Lenguaje:** Python  
**Plataforma de desarrollo y pruebas:** Windows

Este proyecto implementa cuatro demostraciones prácticas de conceptos del
sistema operativo: monitoreo de CPU y RAM, lectura con una caché en memoria,
reserva de memoria con límites de seguridad y comparación de prioridades de
procesos. Cada ejercicio se ejecuta desde su propio archivo, sin tener que
modificar el código.

Los resultados medidos y el alcance de las pruebas están documentados en
[EVIDENCIAS.md](./EVIDENCIAS.md). El enunciado entregado para el taller se
conserva en [taller.readme](./taller.readme).

## Contenido del proyecto

| Archivo | Ejercicio |
| --- | --- |
| `monitor_recursos.py` | Muestra CPU/RAM y registra alertas al superar el umbral de RAM. |
| `simulador_cache.py` | Compara la primera lectura desde disco con las lecturas desde caché RAM. |
| `estres_memoria.py` | Reserva strings con límites automáticos y libera la memoria al finalizar. |
| `prioridad_procesos.py` | Compara el tiempo de cálculo de procesos con prioridades distintas. |
| `requirements.txt` | Dependencias necesarias para ejecutar los ejercicios. |
| `EVIDENCIAS.md` | Resultados de las pruebas ejecutadas y sus limitaciones. |

## Requisitos e instalación

- Python 3.10 o posterior.
- Windows para ejecutar la comparación de prioridad baja contra Tiempo Real.
- `psutil`, instalado desde la carpeta del proyecto:

```powershell
python -m pip install -r requirements.txt
```

Ejecuta los comandos desde esta carpeta. Todos los ejercicios aceptan `--help`
para mostrar sus opciones.

## 1. Vigilante de recursos: RAM y CPU

```powershell
python monitor_recursos.py
python monitor_recursos.py --interval 1 --threshold 80 --log registros\ram_alertas.txt
```

Muestra el porcentaje de CPU y RAM en cada intervalo. Cada lectura que supere
el umbral agrega una línea con fecha, hora y porcentaje de RAM al archivo de
log. Termina con `Ctrl+C`.

## 2. Simulador de caché de archivos

```powershell
python simulador_cache.py .\archivo_grande.bin
python simulador_cache.py .\archivo_grande.bin --repeats 5 --max-mb 256
```

La primera solicitud lee los bytes del disco y los guarda en un diccionario en
RAM; las solicitudes posteriores usan ese mismo contenido sin volver a abrir
el archivo. Se muestran el tiempo y el origen de cada lectura. Por seguridad,
el tamaño por defecto máximo es 256 MiB. Si no tienes un archivo de prueba,
puedes usar cualquier archivo grande existente.

## 3. Estrés de memoria y paginación

```powershell
python estres_memoria.py
python estres_memoria.py --max-mb 128 --hold-seconds 30
```

Reserva strings mientras muestra la cantidad de objetos y la RAM disponible.
El límite real es el menor valor entre el límite solicitado, 10% de la RAM
disponible al inicio y 5% de la RAM física. El límite solicitado no puede
superar 512 MiB; la reserva se libera automáticamente y el tiempo de
observación está limitado a 120 segundos. Mientras corre, observa en el
Administrador de tareas **Memoria** y **Memoria confirmada**.

La prueba permite observar la presión de memoria, pero no garantiza que Windows
use el archivo de paginación: ese comportamiento depende de la configuración,
la carga del equipo y la memoria disponible. Interrumpe con `Ctrl+C` si notas
que el equipo se vuelve lento; la memoria se libera al terminar.

## 4. Prioridad de procesos

```powershell
python prioridad_procesos.py
python prioridad_procesos.py --iterations 2000000 --allow-realtime
```

La opción Tiempo Real requiere `--allow-realtime` y una confirmación escrita
(`SI`) en la terminal. Se inicia un proceso de prioridad **Por debajo de lo
normal** y otro de clase **Tiempo Real**, con el mismo número de operaciones.
Se informa cuánto tarda cada uno y cuál termina primero. Cada proceso tiene un
límite de 10 millones de iteraciones y la prueba completa se interrumpe al
superar 60 segundos.

**Precaución:** Tiempo Real puede dejar el equipo sin respuesta. Guarda tu
trabajo antes de habilitarlo y no aumentes el número de iteraciones sin
necesidad. Windows puede rechazar el cambio por permisos; en ese caso el
programa informa el error. El proceso que termina primero puede variar por
carga, afinidad de CPU, permisos y otros factores; una ejecución no demuestra
por sí sola el efecto de la planificación.
