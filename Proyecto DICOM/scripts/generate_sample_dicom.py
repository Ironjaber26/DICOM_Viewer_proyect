"""Generate a small synthetic DICOM file for demos/tests.

No real patient data is used anywhere in this repository: this script
builds a fake CT-like image (a circle on a noisy background) with
made-up metadata, so the rest of the toolkit can be exercised without
needing access to real clinical images.
"""

from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_dicom" / "ct_sample.dcm"


def _build_pixel_data(size: int = 128) -> np.ndarray:
    rng = np.random.default_rng(seed=42)
    y, x = np.ogrid[:size, :size]
    center = size / 2
    radius = size / 3

    circle_mask = (x - center) ** 2 + (y - center) ** 2 <= radius**2
    background = rng.normal(loc=-800, scale=20, size=(size, size))
    tissue = rng.normal(loc=40, scale=15, size=(size, size))

    image = np.where(circle_mask, tissue, background)
    return image.astype(np.int16)


def generate_sample_dicom(output_path: Path = OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pixel_array = _build_pixel_data()

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(output_path), {}, file_meta=file_meta, preamble=b"\0" * 128)

    # --- Paciente (datos ficticios, solo para pruebas) ---
    ds.PatientName = "Paciente^Prueba"
    ds.PatientID = "SIM0001"
    ds.PatientBirthDate = "19900101"
    ds.PatientSex = "O"
    ds.PatientAge = "035Y"

    # --- Estudio / Serie ---
    ds.StudyDate = "20260101"
    ds.StudyTime = "120000"
    ds.StudyDescription = "Estudio simulado de torax"
    ds.SeriesDescription = "Serie simulada - corte axial"
    ds.Modality = "CT"
    ds.BodyPartExamined = "CHEST"

    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

    # --- Equipo ---
    ds.Manufacturer = "SimulatedScanners Inc."
    ds.ManufacturerModelName = "SimCT 1000"
    ds.InstitutionName = "Laboratorio de Practica"

    # --- Geometria / pixeles ---
    ds.Rows, ds.Columns = pixel_array.shape
    ds.PixelSpacing = [0.5, 0.5]
    ds.SliceThickness = 1.0
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1  # signed
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.RescaleSlope = 1
    ds.RescaleIntercept = 0
    ds.WindowCenter = 40
    ds.WindowWidth = 400

    ds.PixelData = pixel_array.tobytes()

    ds.save_as(str(output_path), enforce_file_format=True)
    return output_path


if __name__ == "__main__":
    path = generate_sample_dicom()
    print(f"Archivo DICOM de ejemplo generado en: {path}")
