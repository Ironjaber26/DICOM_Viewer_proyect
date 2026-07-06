"""Show the three orthogonal planes (axial/coronal/sagittal) of a
DICOM volume side by side, at their central slice.

Works with either:
  - A folder containing one file per slice (a classic DICOM series).
  - A single multi-frame DICOM file (e.g. Enhanced MR/CT storage,
    ultrasound cine loops).

Examples
--------
    python scripts/view_planes.py data/sample_dicom/series
    python scripts/view_planes.py "D:/Descargas/IMG-0005-00001.dcm"
    python scripts/view_planes.py archivo.dcm --window-center 40 --window-width 400
    python scripts/view_planes.py archivo.dcm --save planos.png
"""

import argparse

from dicom_tools import load_volume
from dicom_tools.viewer import show_volume_slices


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Muestra los 3 planos (axial/coronal/sagital) de un volumen DICOM."
    )
    parser.add_argument("path", help="Carpeta con una serie, o un archivo .dcm multi-frame")
    parser.add_argument("--window-center", type=float, default=None, help="Centro de ventana (contraste)")
    parser.add_argument("--window-width", type=float, default=None, help="Ancho de ventana (contraste)")
    parser.add_argument("--save", default=None, help="Guardar la imagen en esta ruta en vez de solo mostrarla")
    args = parser.parse_args()

    volume = load_volume(args.path)
    print(f"Volumen cargado: shape={volume.shape}, spacing(mm)={volume.spacing}")
    show_volume_slices(
        volume,
        window_center=args.window_center,
        window_width=args.window_width,
        save_path=args.save,
    )


if __name__ == "__main__":
    main()
