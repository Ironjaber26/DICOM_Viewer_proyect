import matplotlib.pyplot as plt
import pytest
from matplotlib.backend_bases import KeyEvent, MouseEvent

from dicom_tools import load_volume
from dicom_tools.viewer import explore_volume, show_dicom, show_volume_slices


def test_show_dicom_single_frame_file(sample_dicom_path, tmp_path):
    out = tmp_path / "out.png"
    show_dicom(sample_dicom_path, save_path=out)
    assert out.exists()


def test_show_dicom_multiframe_defaults_to_middle_frame(sample_multiframe_path, tmp_path):
    out = tmp_path / "out.png"
    show_dicom(sample_multiframe_path, save_path=out)
    assert out.exists()


def test_show_dicom_multiframe_explicit_frame(sample_multiframe_path, tmp_path):
    out = tmp_path / "out.png"
    show_dicom(sample_multiframe_path, frame=0, save_path=out)
    assert out.exists()


def test_show_dicom_multiframe_out_of_range_frame_raises(sample_multiframe_path):
    with pytest.raises(ValueError, match="fuera de rango"):
        show_dicom(sample_multiframe_path, frame=999)


def test_explore_volume_scroll_and_key_navigation(sample_series_dir, monkeypatch):
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    volume = load_volume(sample_series_dir)
    explore_volume(volume)

    fig = plt.gcf()
    ax = fig.axes[0]
    initial_title = ax.get_title()
    assert "Axial" in initial_title

    scroll_up = MouseEvent("scroll_event", fig.canvas, x=0, y=0, button="up")
    fig.canvas.callbacks.process("scroll_event", scroll_up)
    assert ax.get_title() != initial_title

    switch_to_coronal = KeyEvent("key_press_event", fig.canvas, key="c")
    fig.canvas.callbacks.process("key_press_event", switch_to_coronal)
    assert "Coronal" in ax.get_title()

    plt.close(fig)


def test_explore_volume_ignores_plane_switch_for_single_slice(sample_dicom_path, monkeypatch):
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    volume = load_volume(sample_dicom_path)  # una sola imagen -> volumen de 1 corte
    assert volume.is_single_slice

    explore_volume(volume)

    fig = plt.gcf()
    ax = fig.axes[0]
    assert "Axial" in ax.get_title()

    switch_to_coronal = KeyEvent("key_press_event", fig.canvas, key="c")
    fig.canvas.callbacks.process("key_press_event", switch_to_coronal)
    assert "Axial" in ax.get_title()  # el cambio de plano se ignoro

    plt.close(fig)


def test_explore_volume_disables_conflicting_default_keymaps(sample_series_dir, monkeypatch):
    # 'c' y 's' vienen mapeados por defecto en matplotlib a "atras" y
    # "guardar figura"; deben quedar libres para usarse como cambio de plano.
    plt.rcParams["keymap.back"] = ["left", "c", "backspace"]
    plt.rcParams["keymap.save"] = ["s", "ctrl+s"]
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    volume = load_volume(sample_series_dir)
    explore_volume(volume)

    assert "c" not in plt.rcParams["keymap.back"]
    assert "s" not in plt.rcParams["keymap.save"]

    plt.close(plt.gcf())


def test_explore_volume_shows_patient_overlay(sample_series_dir, monkeypatch):
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    volume = load_volume(sample_series_dir)
    explore_volume(volume)

    fig = plt.gcf()
    assert len(fig.texts) == 1  # vive en la figura, no en el eje de la imagen
    assert volume.patient_info.patient_id in fig.texts[0].get_text()
    assert len(fig.axes[0].texts) == 0  # y no se pisa con la imagen

    plt.close(fig)


def test_explore_volume_patient_overlay_survives_slice_navigation(sample_series_dir, monkeypatch):
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    volume = load_volume(sample_series_dir)
    explore_volume(volume)
    fig = plt.gcf()

    scroll_up = MouseEvent("scroll_event", fig.canvas, x=0, y=0, button="up")
    fig.canvas.callbacks.process("scroll_event", scroll_up)

    assert len(fig.texts) == 1  # el overlay no se duplica ni desaparece al navegar

    plt.close(fig)


def test_show_volume_slices_shows_patient_overlay(sample_series_dir, tmp_path):
    volume = load_volume(sample_series_dir)
    out = tmp_path / "planes.png"
    show_volume_slices(volume, save_path=out)

    fig = plt.gcf()
    assert len(fig.texts) == 1
    assert volume.patient_info.patient_id in fig.texts[0].get_text()
    assert len(fig.axes[0].texts) == 0  # no se pisa con la imagen axial

    plt.close(fig)
