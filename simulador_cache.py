"""Compara la lectura de un archivo desde disco y desde una caché en RAM."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


class FileCache:
    """Guarda en RAM el contenido de los archivos solicitados."""

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes
        self._contents: dict[Path, bytes] = {}

    def read(self, file_path: Path) -> tuple[bytes, bool]:
        resolved_path = file_path.expanduser().resolve(strict=True)
        if not resolved_path.is_file():
            raise ValueError(f"No es un archivo: {resolved_path}")
        if resolved_path in self._contents:
            return self._contents[resolved_path], True

        file_size = resolved_path.stat().st_size
        if file_size > self.max_bytes:
            raise ValueError(
                f"El archivo ocupa {file_size / 1024**2:.1f} MiB y supera "
                f"el límite de caché de {self.max_bytes / 1024**2:.1f} MiB."
            )

        with resolved_path.open("rb") as file:
            contents = file.read()
        self._contents[resolved_path] = contents
        return contents, False


def compare_file_reads(file_path: Path, max_mb: int, repeats: int) -> None:
    if max_mb < 1:
        raise ValueError("El límite de caché debe ser de al menos 1 MiB.")
    if repeats < 2:
        raise ValueError("Solicita el archivo al menos dos veces.")

    cache = FileCache(max_mb * 1024**2)
    timings: list[float] = []
    for request_number in range(1, repeats + 1):
        started = time.time()
        contents, from_cache = cache.read(file_path)
        elapsed = time.time() - started
        timings.append(elapsed)
        source = "caché RAM" if from_cache else "disco"
        print(
            f"Solicitud {request_number}: {source:10} | "
            f"{elapsed:.6f} s | {len(contents):,} bytes"
        )

    if timings[0] > 0 and timings[1] > 0:
        print(f"Primera lectura / segunda lectura: {timings[0] / timings[1]:.2f}x")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lee un archivo desde disco una vez y luego desde una caché en RAM."
    )
    parser.add_argument("file", type=Path, help="Archivo que se desea leer.")
    parser.add_argument("--max-mb", type=int, default=256, help="Tamaño máximo en MiB.")
    parser.add_argument("--repeats", type=int, default=3, help="Número de solicitudes.")
    args = parser.parse_args()
    try:
        compare_file_reads(args.file, args.max_mb, args.repeats)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
