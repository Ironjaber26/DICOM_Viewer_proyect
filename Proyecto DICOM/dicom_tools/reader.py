"""Basic loading helpers for DICOM files."""

from pathlib import Path
from typing import Union

import pydicom
from pydicom.dataset import FileDataset
from pydicom.errors import InvalidDicomError

PathLike = Union[str, Path]


def is_dicom_file(path: PathLike) -> bool:
    """Return True if the file at ``path`` can be parsed as DICOM.

    Uses ``force=False`` so files without the standard DICM preamble
    (common with some exported files) are still rejected safely.
    """
    try:
        pydicom.dcmread(str(path), stop_before_pixels=True)
        return True
    except (InvalidDicomError, FileNotFoundError, IsADirectoryError):
        return False


def load_dicom(path: PathLike, force: bool = False) -> FileDataset:
    """Read a DICOM file and return the parsed dataset.

    Parameters
    ----------
    path:
        Path to the ``.dcm`` file.
    force:
        If True, attempt to read the file even if it is missing the
        128-byte preamble / "DICM" magic word (useful for some raw
        exports from PACS systems).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    return pydicom.dcmread(str(path), force=force)
