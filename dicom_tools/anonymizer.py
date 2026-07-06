"""Basic de-identification of direct patient identifiers.

This is a teaching/demo implementation, NOT a certified DICOM
de-identification tool. It only clears the most common identifying
tags (PS3.15 Basic Application Confidentiality Profile, partial).
For real clinical/research use, rely on a validated tool (e.g. RSNA
CTP, dcmtk, or pydicom's own de-identification recipes) and confirm
which profile your IRB/ethics committee requires.
"""

import copy
from typing import Iterable, Optional

from pydicom.dataset import FileDataset

# Date-valued (VR "DA") tags need an empty string, not free text, or
# pydicom will raise/warn about an invalid value.
DATE_TAGS = ("PatientBirthDate",)

DEFAULT_TAGS_TO_CLEAR = (
    "PatientName",
    "PatientID",
    "PatientAddress",
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "OperatorsName",
) + DATE_TAGS


def anonymize_dataset(
    ds: FileDataset,
    tags_to_clear: Iterable[str] = DEFAULT_TAGS_TO_CLEAR,
    replacement: str = "ANONYMOUS",
    new_patient_id: Optional[str] = None,
) -> FileDataset:
    """Return a copy of ``ds`` with common identifying tags cleared.

    The original dataset is not modified.
    """
    anon = copy.deepcopy(ds)

    for tag in tags_to_clear:
        if tag in anon:
            value = "" if tag in DATE_TAGS else replacement
            setattr(anon, tag, value)

    if new_patient_id is not None:
        anon.PatientID = new_patient_id

    return anon
