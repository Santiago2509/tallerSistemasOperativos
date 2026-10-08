"""Reserva memoria de forma limitada para observar el uso de RAM/paginación."""

from __future__ import annotations

import argparse
import sys
import time

try:
    import psutil
except ImportError as exc:
    raise SystemExit(
        "Falta psutil. Instálala ejecutando: python -m pip install -r requirements.txt"
    ) from exc


def stress_memory(max_mb: int, hold_seconds: int) -> None:
    if not 1 <= max_mb <= 512:
        raise ValueError("El límite solicitado debe estar entre 1 y 512 MiB.")
    if not 0 <= hold_seconds <= 120:
        raise ValueError("El tiempo de observación debe estar entre 0 y 120 s.")

    memory = psutil.virtual_memory()
    initial_available = memory.available
    safe_budget = min(
        max_mb * 1024**2,
        int(initial_available * 0.10),
        int(memory.total * 0.05),
    )
    if safe_budget < 1024**2:
        raise RuntimeError(
            "No hay suficiente RAM disponible para iniciar una prueba segura "
            "(el presupuesto calculado es menor que 1 MiB)."
        )

    sample = f"taller-memoria-{0:012d}-" + "x" * 96
    estimated_item_bytes = sys.getsizeof(sample) + 8
    max_items = safe_budget // estimated_item_bytes
    items: list[str] = []
    print(
        f"Presupuesto de seguridad: {safe_budget / 1024**2:.1f} MiB "
        f"(límite solicitado: {max_mb} MiB; máximo: 5% de RAM física "
        "y 10% de RAM disponible al iniciar)."
    )

    try:
        while len(items) < max_items:
            current_available = psutil.virtual_memory().available
            consumed = initial_available - current_available
            if consumed >= safe_budget:
                print("Se alcanzó el presupuesto de seguridad; se detiene la reserva.")
                break

            chunk_size = min(5_000, max_items - len(items))
            items.extend(
                f"taller-memoria-{index:012d}-" + "x" * 96
                for index in range(len(items), len(items) + chunk_size)
            )
            if len(items) % 50_000 < chunk_size or len(items) == max_items:
                current = psutil.virtual_memory()
                allocated_estimate = len(items) * estimated_item_bytes
                print(
                    f"Objetos: {len(items):,} | estimado: "
                    f"{allocated_estimate / 1024**2:.1f} MiB | "
                    f"RAM disponible: {current.available / 1024**3:.2f} GiB"
                )

        print(
            f"Reserva detenida con {len(items):,} strings. Observa el "
            f"Administrador de tareas durante {hold_seconds} s."
        )
        for remaining in range(hold_seconds, 0, -1):
            print(f"\rLiberación automática en {remaining:3d} s", end="", flush=True)
            time.sleep(1)
        if hold_seconds:
            print()
    except KeyboardInterrupt:
        print("\nPrueba interrumpida manualmente; la memoria se liberará.")
    finally:
        items.clear()
        print("Memoria liberada.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reserva strings en RAM con un límite de seguridad automático."
    )
    parser.add_argument("--max-mb", type=int, default=128, help="Límite solicitado en MiB.")
    parser.add_argument(
        "--hold-seconds", type=int, default=20, help="Tiempo para observar la memoria."
    )
    args = parser.parse_args()
    try:
        stress_memory(args.max_mb, args.hold_seconds)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
