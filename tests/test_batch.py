from dicom_tools import scan_directory


def test_scan_directory_finds_dicom_files(sample_dicom_path):
    df = scan_directory(sample_dicom_path.parent)

    assert len(df) == 1
    assert df.iloc[0]["modality"] == "CT"
    assert df.iloc[0]["file_path"].endswith("ct_sample.dcm")


def test_scan_directory_empty_folder_returns_empty_dataframe(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    df = scan_directory(empty_dir)

    assert df.empty
