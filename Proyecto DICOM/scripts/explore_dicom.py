"""Interactively explore a DICOM volume: scroll through slices and
switch between axial/coronal/sagital planes.

Works with either:
  - A folder containing one file per slice (a classic DICOM series).
  - A single multi-frame DICOM file (e.g. Enhanced MR/CT storage,
    ultrasound cine loops).

Examples
--------
    python scripts/explore_dicom.py data/sample_dicom/series
    python scripts/explore_dicom.py "D:/Descargas/IMG-0005-00001.dcm"
    python scripts/explore_dicom.py archivo.dcm --window-center 40 --window-width 400

Controles en la ventana:
    - Rueda del mouse: avanza/retrocede de corte.
    - Teclas a / c / s: cambia entre plano axial / coronal / sagital.
"""

import argparse

from dicom_tools import load_volume
from dicom_tools.viewer import explore_volume


def main() -> None:
    parser = argparse.ArgumentParser(description="Explora un volumen DICOM interactivamente.")
    parser.add_argument("path", help="Carpeta con una serie, o un archivo .dcm multi-frame")
    parser.add_argument("--window-center", type=float, default=None, help="Centro de ventana (contraste)")
    parser.add_argument("--window-width", type=float, default=None, help="Ancho de ventana (contraste)")
    args = parser.parse_args()

    volume = load_volume(args.path)
    print(f"Volumen cargado: shape={volume.shape}, spacing(mm)={volume.spacing}")
    explore_volume(volume, window_center=args.window_center, window_width=args.window_width)


if __name__ == "__main__":
    main()
