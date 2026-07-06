import numpy as np

from dicom_tools import load_dicom
from dicom_tools.pixels import get_pixel_array, apply_windowing, get_image_shape


def test_get_pixel_array_shape_matches_rows_columns(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    array = get_pixel_array(ds)

    assert array.shape == (ds.Rows, ds.Columns)


def test_apply_windowing_uses_dataset_window(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    array = get_pixel_array(ds)
    image = apply_windowing(array, ds=ds)

    assert image.dtype == np.uint8
    assert image.min() >= 0 and image.max() <= 255


def test_apply_windowing_explicit_values_override_dataset(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    array = get_pixel_array(ds)

    image = apply_windowing(array, window_center=0, window_width=100)
    assert image.shape == array.shape


def test_get_image_shape(sample_dicom_path):
    ds = load_dicom(sample_dicom_path)
    assert get_image_shape(ds) == (ds.Rows, ds.Columns)
