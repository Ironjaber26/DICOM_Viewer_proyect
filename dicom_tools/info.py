"""Extract a friendly summary of the key metadata inside a DICOM file."""

from collections.abc import Sequence
from dataclasses import dataclass, asdict
from typing import Any, Optional, Union
from pathlib import Path

from pydicom.dataset import FileDataset

from .reader import load_dicom

PathLike = Union[str, Path]


def _get(ds: FileDataset, tag: str, default: Any = None) -> Any:
    """Safely read a DICOM attribute, returning ``default`` if absent."""
    value = getattr(ds, tag, default)
    if value is None:
        return value
    # pydicom's MultiValue (e.g. PixelSpacing) is a Sequence but not a
    # plain list/tuple; convert it to one. Everything else that isn't a
    # basic python type (PersonName, etc.) gets cast to str.
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [float(v) if isinstance(v, (int, float)) else str(v) for v in value]
    if not isinstance(value, (int, float, str)):
        value = str(value)
    return value


@dataclass
class DicomInfo:
    """Flat, easy-to-read summary of a DICOM dataset.

    Grouped the same way a radiologist/tech would think about the file:
    who the patient is, what study/series it belongs to, what equipment
    produced it, and the geometry of the pixel data.
    """

    # --- Paciente ---
    patient_name: Optional[str]
    patient_id: Optional[str]
    patient_birth_date: Optional[str]
    patient_sex: Optional[str]
    patient_age: Optional[str]

    # --- Estudio / Serie ---
    study_date: Optional[str]
    study_time: Optional[str]
    study_description: Optional[str]
    series_description: Optional[str]
    modality: Optional[str]
    body_part_examined: Optional[str]

    # --- Equipo ---
    manufacturer: Optional[str]
    manufacturer_model_name: Optional[str]
    institution_name: Optional[str]

    # --- Imagen / geometría ---
    rows: Optional[int]
    columns: Optional[int]
    number_of_frames: Optional[int]
    pixel_spacing: Optional[list]
    slice_thickness: Optional[float]
    bits_allocated: Optional[int]
    photometric_interpretation: Optional[str]

    # --- Identificadores DICOM ---
    sop_instance_uid: Optional[str]
    study_instance_uid: Optional[str]
    series_instance_uid: Optional[str]

    def to_dict(self) -> dict:
        """Return the info as a plain dict (handy for pandas/JSON)."""
        return asdict(self)


def extract_dicom_info(source: Union[PathLike, FileDataset]) -> DicomInfo:
    """Get a simple, structured summary of a DICOM file's metadata.

    Parameters
    ----------
    source:
        Either a path to a ``.dcm`` file, or an already-loaded
        ``pydicom`` dataset (e.g. returned by ``load_dicom``).

    Returns
    -------
    DicomInfo
        Dataclass with the most commonly needed fields already
        extracted and safely defaulted to ``None`` when missing.

    Example
    -------
    >>> info = extract_dicom_info("data/sample_dicom/ct_sample.dcm")
    >>> info.modality
    'CT'
    >>> info.to_dict()["rows"]
    128
    """
    ds = source if isinstance(source, FileDataset) else load_dicom(source)

    return DicomInfo(
        patient_name=_get(ds, "PatientName"),
        patient_id=_get(ds, "PatientID"),
        patient_birth_date=_get(ds, "PatientBirthDate"),
        patient_sex=_get(ds, "PatientSex"),
        patient_age=_get(ds, "PatientAge"),
        study_date=_get(ds, "StudyDate"),
        study_time=_get(ds, "StudyTime"),
        study_description=_get(ds, "StudyDescription"),
        series_description=_get(ds, "SeriesDescription"),
        modality=_get(ds, "Modality"),
        body_part_examined=_get(ds, "BodyPartExamined"),
        manufacturer=_get(ds, "Manufacturer"),
        manufacturer_model_name=_get(ds, "ManufacturerModelName"),
        institution_name=_get(ds, "InstitutionName"),
        rows=_get(ds, "Rows"),
        columns=_get(ds, "Columns"),
        number_of_frames=_get(ds, "NumberOfFrames"),
        pixel_spacing=_get(ds, "PixelSpacing"),
        slice_thickness=_get(ds, "SliceThickness"),
        bits_allocated=_get(ds, "BitsAllocated"),
        photometric_interpretation=_get(ds, "PhotometricInterpretation"),
        sop_instance_uid=_get(ds, "SOPInstanceUID"),
        study_instance_uid=_get(ds, "StudyInstanceUID"),
        series_instance_uid=_get(ds, "SeriesInstanceUID"),
    )
