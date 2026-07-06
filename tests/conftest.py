import sys
from pathlib import Path

import matplotlib
import numpy as np
import pydicom
import pytest
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

# Backend sin ventana: los tests de viewer.py no deben abrir una GUI.
matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.generate_sample_dicom import generate_sample_dicom  # noqa: E402
from scripts.generate_sample_series import generate_sample_series  # noqa: E402


@pytest.fixture(scope="session")
def sample_dicom_path(tmp_path_factory) -> Path:
    out_dir = tmp_path_factory.mktemp("dicom_samples")
    return generate_sample_dicom(out_dir / "ct_sample.dcm")


@pytest.fixture(scope="session")
def sample_series_dir(tmp_path_factory) -> Path:
    out_dir = tmp_path_factory.mktemp("dicom_series")
    return generate_sample_series(out_dir / "series", num_slices=6, size=32)


@pytest.fixture(scope="session")
def sample_multiframe_path(tmp_path_factory) -> Path:
    """A tiny synthetic multi-frame DICOM (like an Enhanced MR/US cine)."""
    out_path = tmp_path_factory.mktemp("dicom_multiframe") / "multiframe.dcm"

    num_frames, size = 5, 16
    rng = np.random.default_rng(seed=0)
    pixel_array = rng.integers(0, 1000, size=(num_frames, size, size), dtype=np.int16)

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.EnhancedMRImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(out_path), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.Modality = "MR"
    ds.Rows, ds.Columns = size, size
    ds.NumberOfFrames = num_frames
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.RescaleSlope = 1
    ds.RescaleIntercept = 0
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

    ds.PixelData = pixel_array.tobytes()
    ds.save_as(str(out_path), enforce_file_format=True)
    return out_path
