"""Scan a folder of DICOM files and summarize them as a table."""

from pathlib import Path
from typing import Union

import pandas as pd

from .reader import is_dicom_file
from .info import extract_dicom_info

PathLike = Union[str, Path]


def scan_directory(folder: PathLike, recursive: bool = True) -> pd.DataFrame:
    """Walk ``folder`` and return one row of metadata per DICOM file found.

    Non-DICOM files are silently skipped. Useful for getting a quick
    overview of a study/series export (how many files, which
    modalities, which patients, etc.).
    """
    folder = Path(folder)
    pattern = "**/*" if recursive else "*"

    rows = []
    for path in folder.glob(pattern):
        if not path.is_file() or not is_dicom_file(path):
            continue
        info = extract_dicom_info(path).to_dict()
        info["file_path"] = str(path)
        rows.append(info)

    columns = ["file_path"] + [c for c in rows[0].keys() if c != "file_path"] if rows else None
    return pd.DataFrame(rows, columns=columns)
