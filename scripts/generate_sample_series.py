"""Generate a synthetic multi-slice DICOM series (a small 3D volume).

Unlike ``generate_sample_dicom.py`` (a single image), this creates
several files that all share the same SeriesInstanceUID/StudyInstanceUID
and have consistent ImagePositionPatient/InstanceNumber metadata - the
same way a real CT/MRI series is exported from a PACS. Stacking them in
order reconstructs a synthetic sphere, so slicing the resulting volume
along different axes actually looks like something.
"""

from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_dicom" / "series"


def _slice_pixels(size: int, z: int, depth: int, radius: float) -> np.ndarray:
    """A cross-section of a sphere at height ``z`` (out of ``depth``)."""
    rng = np.random.default_rng(seed=z)
    center = size / 2
    z_center = depth / 2
    # ``z`` counts slices (0..depth), but ``radius`` is in pixel units
    # (0..size). Without rescaling, dz barely moves relative to radius
    # and the "sphere" looks like a cylinder - rescale dz to the same
    # pixel scale as x/y so the cross-section actually shrinks with height.
    dz = (z - z_center) * (size / depth)
    circle_radius_sq = max(radius**2 - dz**2, 0)

    y, x = np.ogrid[:size, :size]
    dist_sq = (x - center) ** 2 + (y - center) ** 2

    background = rng.normal(loc=-800, scale=20, size=(size, size))
    tissue = rng.normal(loc=40, scale=15, size=(size, size))

    inside_sphere = dist_sq <= circle_radius_sq
    image = np.where(inside_sphere, tissue, background)
    return image.astype(np.int16)


def generate_sample_series(
    output_dir: Path = OUTPUT_DIR,
    num_slices: int = 20,
    size: int = 128,
    slice_thickness: float = 3.0,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    study_uid = generate_uid()
    series_uid = generate_uid()
    radius = size / 3

    for i in range(num_slices):
        pixel_array = _slice_pixels(size, i, num_slices, radius)

        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.CTImageStorage
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        out_path = output_dir / f"slice_{i:04d}.dcm"
        ds = FileDataset(str(out_path), {}, file_meta=file_meta, preamble=b"\0" * 128)

        ds.PatientName = "Paciente^Prueba"
        ds.PatientID = "SIM0002"
        ds.PatientBirthDate = "19900101"
        ds.PatientSex = "O"

        ds.StudyDate = "20260101"
        ds.StudyDescription = "Estudio simulado - serie completa"
        ds.SeriesDescription = "Serie simulada - volumen esferico"
        ds.Modality = "CT"
        ds.BodyPartExamined = "CHEST"

        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = series_uid
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

        ds.Manufacturer = "SimulatedScanners Inc."
        ds.InstitutionName = "Laboratorio de Practica"

        # --- Metadata clave para poder ordenar y apilar la serie ---
        ds.InstanceNumber = i + 1
        ds.SliceLocation = i * slice_thickness
        ds.ImagePositionPatient = [0.0, 0.0, i * slice_thickness]
        ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]

        ds.Rows, ds.Columns = pixel_array.shape
        ds.PixelSpacing = [0.5, 0.5]
        ds.SliceThickness = slice_thickness
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 1
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.RescaleSlope = 1
        ds.RescaleIntercept = 0
        ds.WindowCenter = 40
        ds.WindowWidth = 400

        ds.PixelData = pixel_array.tobytes()
        ds.save_as(str(out_path), enforce_file_format=True)

    return output_dir


if __name__ == "__main__":
    path = generate_sample_series()
    print(f"Serie DICOM sintetica generada en: {path}")
