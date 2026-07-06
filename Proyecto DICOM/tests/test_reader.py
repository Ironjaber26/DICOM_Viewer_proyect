from dicom_tools import is_dicom_file, load_dicom


def test_is_dicom_file_true_for_valid_file(sample_dicom_path):
    assert is_dicom_file(sample_dicom_path) is True


def test_is_dicom_file_false_for_missing_file(tmp_path):
    assert is_dicom_file(tmp_path / "does_not_exist.dcm") is False


def test_is_dicom_file_false_for_non_dicom_text_file(tmp_path):
    bogus = tmp_path / "not_dicom.txt"
    bogus.write_text("this is not a dicom file")
    assert is_dicom_file(bogus) is False


def test_load_dicom_returns_dataset(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    assert ds.Modality == "CT"
