"""View any DICOM file from the command line.

Examples
--------
    python scripts/view_dicom.py data/sample_dicom/ct_sample.dcm
    python scripts/view_dicom.py C:/ruta/a/otro_archivo.dcm
    python scripts/view_dicom.py archivo.dcm --window-center 40 --window-width 400
    python scripts/view_dicom.py archivo.dcm --save salida.png
    python scripts/view_dicom.py archivo_multiframe.dcm --frame 90
"""

import argparse

from dicom_tools.viewer import show_dicom


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualiza un archivo DICOM.")
    parser.add_argument("path", help="Ruta al archivo .dcm a mostrar")
    parser.add_argument("--window-center", type=float, default=None, help="Centro de ventana (contraste)")
    parser.add_argument("--window-width", type=float, default=None, help="Ancho de ventana (contraste)")
    parser.add_argument("--no-info", action="store_true", help="No mostrar el titulo con metadata")
    parser.add_argument("--save", default=None, help="Guardar la imagen en esta ruta en vez de solo mostrarla")
    parser.add_argument(
        "--frame", type=int, default=None,
        help="Numero de cuadro a mostrar en archivos multi-frame (por defecto, el cuadro central)",
    )
    args = parser.parse_args()

    show_dicom(
        args.path,
        window_center=args.window_center,
        window_width=args.window_width,
        show_info=not args.no_info,
        save_path=args.save,
        frame=args.frame,
    )


if __name__ == "__main__":
    main()
