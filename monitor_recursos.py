"""Monitorea el uso de RAM y CPU y registra alertas de memoria."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError as exc:
    raise SystemExit(
        "Falta psutil. Instálala ejecutando: python -m pip install -r requirements.txt"
    ) from exc


def monitor_resources(interval: float, log_path: Path, threshold: float) -> None:
    if interval <= 0:
        raise ValueError("El intervalo debe ser mayor que cero.")
    if not 0 < threshold <= 100:
        raise ValueError("El umbral debe estar entre 0 y 100.")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(
        f"Monitoreando cada {interval:g} s; alertas de RAM > {threshold:g}% "
        f"en {log_path}. Pulsa Ctrl+C para terminar."
    )
    try:
        while True:
            cpu_percent = psutil.cpu_percent(interval=interval)
            memory = psutil.virtual_memory()
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            print(
                f"{now} | CPU {cpu_percent:5.1f}% | "
                f"RAM {memory.percent:5.1f}% "
                f"({memory.used / 1024**3:.2f}/{memory.total / 1024**3:.2f} GiB)"
            )
            if memory.percent > threshold:
                line = (
                    f"{now} | ALERTA RAM {memory.percent:.1f}% "
                    f"(umbral: {threshold:.1f}%)\n"
                )
                with log_path.open("a", encoding="utf-8") as log_file:
                    log_file.write(line)
                print(f"  {line.rstrip()}")
    except KeyboardInterrupt:
        print("\nMonitoreo terminado.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitorea CPU/RAM y guarda alertas cuando la RAM supera el umbral."
    )
    parser.add_argument("--interval", type=float, default=2.0, help="Intervalo en segundos.")
    parser.add_argument("--threshold", type=float, default=80.0, help="Umbral de RAM.")
    parser.add_argument(
        "--log", type=Path, default=Path("ram_alertas.txt"), help="Archivo de alertas."
    )
    args = parser.parse_args()
    try:
        monitor_resources(args.interval, args.log, args.threshold)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
