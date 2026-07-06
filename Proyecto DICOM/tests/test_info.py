from dicom_tools import extract_dicom_info, load_dicom


def test_extract_dicom_info_from_path(sample_dicom_path):
    info = extract_dicom_info(sample_dicom_path)

    assert info.modality == "CT"
    assert info.rows == 128
    assert info.columns == 128
    assert info.pixel_spacing == [0.5, 0.5]
    assert info.body_part_examined == "CHEST"


def test_extract_dicom_info_from_dataset(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    info = extract_dicom_info(ds)

    assert info.patient_id == "SIM0001"


def test_to_dict_is_json_friendly(sample_dicom_path):
    info = extract_dicom_info(sample_dicom_path)
    data = info.to_dict()

    assert data["modality"] == "CT"
    assert isinstance(data["pixel_spacing"], list)


def test_missing_tag_defaults_to_none(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    del ds.InstitutionName
    info = extract_dicom_info(ds)

    assert info.institution_name is None
