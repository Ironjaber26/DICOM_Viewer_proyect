"""Print the metadata summary of a DICOM file from the command line.

Example
-------
    python scripts/show_info.py "D:/Descargas/IMG-0005-00001.dcm"
"""

import argparse
import json

from dicom_tools import extract_dicom_info


def main() -> None:
    parser = argparse.ArgumentParser(description="Muestra la metadata de un archivo DICOM.")
    parser.add_argument("path", help="Ruta al archivo .dcm")
    args = parser.parse_args()

    info = extract_dicom_info(args.path)
    print(json.dumps(info.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
