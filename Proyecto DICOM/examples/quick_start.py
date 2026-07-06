"""Minimal end-to-end demo of the dicom_tools toolkit.

Run from the project root with:
    python examples/quick_start.py
"""

import json
from pathlib import Path

from dicom_tools import (
    extract_dicom_info,
    load_dicom,
    anonymize_dataset,
    scan_directory,
)
from dicom_tools.viewer import show_dicom

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_dicom" / "ct_sample.dcm"


def main() -> None:
    print(f"Leyendo: {SAMPLE}\n")

    # 1. Extraer info de forma sencilla con una sola funcion
    info = extract_dicom_info(SAMPLE)
    print("--- Informacion del estudio ---")
    print(json.dumps(info.to_dict(), indent=2, ensure_ascii=False))

    # 2. Anonimizar antes de compartir/analizar
    ds = load_dicom(SAMPLE)
    anon = anonymize_dataset(ds)
    print(f"\nPaciente original: {ds.PatientName} | Anonimizado: {anon.PatientName}")

    # 3. Escanear una carpeta completa y obtener una tabla resumen
    df = scan_directory(SAMPLE.parent)
    print("\n--- Resumen de la carpeta ---")
    print(df[["file_path", "modality", "rows", "columns", "patient_id"]])

    # 4. Visualizar la imagen (aplica windowing automaticamente)
    show_dicom(SAMPLE)


if __name__ == "__main__":
    main()
