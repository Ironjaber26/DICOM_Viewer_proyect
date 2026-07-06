"""Small toolkit for reading, inspecting and visualizing DICOM images."""

from .reader import is_dicom_file, load_dicom
from .info import DicomInfo, extract_dicom_info
from .anonymizer import anonymize_dataset
from .batch import scan_directory
from .volume import Volume, load_volume

__all__ = [
    "is_dicom_file",
    "load_dicom",
    "DicomInfo",
    "extract_dicom_info",
    "anonymize_dataset",
    "scan_directory",
    "Volume",
    "load_volume",
]

__version__ = "0.1.0"
