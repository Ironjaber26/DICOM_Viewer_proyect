import pytest

from dicom_tools import load_volume


def test_load_volume_shape_matches_slices_and_size(sample_series_dir):
    vol = load_volume(sample_series_dir)
    assert vol.shape == (6, 32, 32)


def test_load_volume_spacing(sample_series_dir):
    vol = load_volume(sample_series_dir)
    z_spacing, row_spacing, col_spacing = vol.spacing
    assert z_spacing == pytest.approx(3.0)
    assert row_spacing == pytest.approx(0.5)
    assert col_spacing == pytest.approx(0.5)


def test_load_volume_orthogonal_views_have_expected_shapes(sample_series_dir):
    vol = load_volume(sample_series_dir)
    assert vol.axial(0).shape == (32, 32)
    assert vol.coronal(0).shape == (6, 32)
    assert vol.sagittal(0).shape == (6, 32)


def test_load_volume_rejects_mixed_series(tmp_path, sample_series_dir, sample_dicom_path):
    # sample_dicom_path belongs to a different series than sample_series_dir.
    # Work on a throwaway copy so we don't mutate the shared session fixture.
    import shutil

    mixed_dir = tmp_path / "mixed_series"
    shutil.copytree(sample_series_dir, mixed_dir)
    shutil.copy(sample_dicom_path, mixed_dir / "foreign_slice.dcm")

    with pytest.raises(ValueError, match="mezcla"):
        load_volume(mixed_dir)


def test_load_volume_from_multiframe_file(sample_multiframe_path):
    vol = load_volume(sample_multiframe_path)
    assert vol.shape == (5, 16, 16)


def test_load_volume_wraps_single_frame_file_as_one_slice_volume(sample_dicom_path):
    vol = load_volume(sample_dicom_path)
    assert vol.shape == (1, 128, 128)
    assert vol.is_single_slice is True


def test_load_volume_series_is_not_single_slice(sample_series_dir):
    vol = load_volume(sample_series_dir)
    assert vol.is_single_slice is False
