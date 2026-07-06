from dicom_tools import load_dicom
from dicom_tools.anonymizer import anonymize_dataset


def test_anonymize_dataset_clears_identifiers(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    anon = anonymize_dataset(ds)

    assert str(anon.PatientName) == "ANONYMOUS"
    assert anon.PatientID == "ANONYMOUS"
    assert anon.PatientBirthDate == ""


def test_anonymize_dataset_does_not_mutate_original(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    original_id = ds.PatientID

    anonymize_dataset(ds)

    assert ds.PatientID == original_id


def test_anonymize_dataset_custom_patient_id(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    anon = anonymize_dataset(ds, new_patient_id="STUDY-001")

    assert anon.PatientID == "STUDY-001"
