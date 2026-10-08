"""Compara el cálculo de dos procesos con prioridades distintas en Windows."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import psutil
except ImportError as exc:
    raise SystemExit(
        "Falta psutil. Instálala ejecutando: python -m pip install -r requirements.txt"
    ) from exc


def _run_worker(
    priority_name: str, priority_value: int, iterations: int, start_at: float, result_path: Path
) -> int:
    result: dict[str, object]
    try:
        process = psutil.Process()
        process.nice(priority_value)
        while time.time() < start_at:
            time.sleep(min(0.01, max(0, start_at - time.time())))

        started = time.perf_counter()
        value = 0
        for number in range(iterations):
            value = (value + number * number) % 1_000_000_007
        result = {
            "priority": priority_name,
            "elapsed_seconds": time.perf_counter() - started,
            "iterations": iterations,
            "checksum": value,
            "error": None,
        }
    except (psutil.AccessDenied, psutil.NoSuchProcess, OSError) as exc:
        result = {
            "priority": priority_name,
            "error": f"No se pudo cambiar la prioridad: {exc}",
        }
    try:
        result_path.write_text(json.dumps(result), encoding="utf-8")
    except OSError as exc:
        print(f"No se pudo guardar el resultado del proceso: {exc}", file=sys.stderr)
        return 2
    return 0 if result.get("error") is None else 1


def compare_priorities(iterations: int, allow_realtime: bool) -> None:
    if not 1 <= iterations <= 10_000_000:
        raise ValueError("Las iteraciones deben estar entre 1 y 10,000,000.")
    if os.name != "nt":
        raise RuntimeError(
            "La comparación solicitada (BAJA vs. TIEMPO REAL) está implementada "
            "para Windows, el sistema usado en este taller."
        )
    if not allow_realtime:
        raise RuntimeError(
            "La prioridad Tiempo Real puede dejar el equipo sin respuesta. "
            "Para habilitarla explícitamente, añade --allow-realtime."
        )
    if not sys.stdin.isatty():
        raise RuntimeError(
            "La prueba Tiempo Real requiere una terminal interactiva para confirmar "
            "el riesgo."
        )
    print(
        "ADVERTENCIA: Tiempo Real puede afectar la respuesta del sistema. "
        "El cálculo está limitado a 10,000,000 iteraciones."
    )
    if input("Escribe SI para continuar: ").strip().upper() != "SI":
        print("Prueba cancelada.")
        return

    priorities = [
        ("baja", psutil.BELOW_NORMAL_PRIORITY_CLASS),
        ("tiempo_real", psutil.REALTIME_PRIORITY_CLASS),
    ]
    start_at = time.time() + 1.5
    children: list[subprocess.Popen[str]] = []
    with tempfile.TemporaryDirectory(prefix="taller-prioridad-") as temp_dir:
        result_paths: list[Path] = []
        try:
            for name, priority in priorities:
                result_path = Path(temp_dir) / f"{name}.json"
                result_paths.append(result_path)
                command = [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "_worker",
                    name,
                    str(priority),
                    str(iterations),
                    str(start_at),
                    str(result_path),
                ]
                creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                children.append(
                    subprocess.Popen(command, creationflags=creation_flags, text=True)
                )

            deadline = time.monotonic() + 60
            for child in children:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(child.args, 60)
                child.wait(timeout=remaining)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            for child in children:
                if child.poll() is None:
                    child.terminate()
            for child in children:
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            raise RuntimeError(
                "La prueba se interrumpió o superó 60 segundos; se detuvieron "
                "los procesos hijos."
            )

        results = [json.loads(path.read_text(encoding="utf-8")) for path in result_paths]
        if any(result.get("error") for result in results):
            details = "; ".join(
                str(result["error"]) for result in results if result.get("error")
            )
            raise RuntimeError(details)

        for result in results:
            print(
                f"{result['priority']:12} | "
                f"{result['elapsed_seconds']:.6f} s | "
                f"{result['iterations']:,} iteraciones | "
                f"checksum {result['checksum']}"
            )
        low, realtime = results
        winner = (
            "baja"
            if low["elapsed_seconds"] < realtime["elapsed_seconds"]
            else "tiempo_real"
            if realtime["elapsed_seconds"] < low["elapsed_seconds"]
            else "empate"
        )
        print(f"Terminó primero: {winner}. El resultado puede variar entre ejecuciones.")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "_worker":
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("name")
        parser.add_argument("priority", type=int)
        parser.add_argument("iterations", type=int)
        parser.add_argument("start_at", type=float)
        parser.add_argument("result", type=Path)
        args = parser.parse_args(sys.argv[2:])
        return _run_worker(args.name, args.priority, args.iterations, args.start_at, args.result)

    parser = argparse.ArgumentParser(
        description="Compara procesos de prioridad baja y Tiempo Real en Windows."
    )
    parser.add_argument(
        "--iterations", type=int, default=2_000_000, help="Operaciones por proceso."
    )
    parser.add_argument(
        "--allow-realtime",
        action="store_true",
        help="Habilita la prueba de alto riesgo tras confirmación interactiva.",
    )
    args = parser.parse_args()
    try:
        compare_priorities(args.iterations, args.allow_realtime)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
