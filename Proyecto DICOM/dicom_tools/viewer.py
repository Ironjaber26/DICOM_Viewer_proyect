"""Quick visualization helpers built on matplotlib."""

from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from .reader import load_dicom
from .pixels import get_pixel_array, apply_windowing
from .info import DicomInfo, extract_dicom_info
from .volume import Volume

PathLike = Union[str, Path]


def _format_patient_overlay(info: DicomInfo) -> str:
    """Build a short, human-friendly patient/study summary block."""
    lines = [f"{info.patient_name or 'Sin nombre'}  (ID: {info.patient_id or '?'})"]

    demographics = " | ".join(v for v in (info.patient_sex, info.patient_age) if v)
    if demographics:
        lines.append(demographics)

    study_line = " - ".join(v for v in (info.modality, info.body_part_examined) if v)
    if study_line:
        lines.append(study_line)

    if info.study_description:
        lines.append(info.study_description)

    if info.study_date and len(info.study_date) == 8:
        lines.append(f"Estudio: {info.study_date[:4]}-{info.study_date[4:6]}-{info.study_date[6:]}")

    if info.institution_name:
        lines.append(info.institution_name)

    return "\n".join(lines)


def _draw_patient_overlay(fig, info: DicomInfo) -> None:
    """Draw patient/study info in the figure's margin (not over the image).

    Placed with ``fig.transFigure`` (figure-relative coordinates) instead
    of on an ``Axes``, so it lives in the reserved top margin and never
    overlaps the pixel data - and, since it belongs to the figure and not
    the axes, it survives ``ax.clear()`` calls (no need to redraw it on
    every slice change).
    """
    fig.text(
        0.01,
        0.99,
        _format_patient_overlay(info),
        transform=fig.transFigure,
        va="top",
        ha="left",
        color="#1c1c1c",
        fontsize=8.5,
        family="monospace",
        linespacing=1.5,
        bbox=dict(facecolor="#eef6ff", alpha=0.9, edgecolor="#4fa8ff", boxstyle="round,pad=0.4"),
    )


def show_dicom(
    source: PathLike,
    window_center: Optional[float] = None,
    window_width: Optional[float] = None,
    show_info: bool = True,
    save_path: Optional[PathLike] = None,
    frame: Optional[int] = None,
) -> None:
    """Display a single DICOM image with an optional metadata title.

    Parameters
    ----------
    source:
        Path to the ``.dcm`` file.
    window_center, window_width:
        Optional manual windowing values. Defaults to the values stored
        in the file (or full min/max range if none are present).
    show_info:
        If True, adds a title with patient/study/modality info.
    save_path:
        If given, saves the figure to this path instead of only
        displaying it.
    frame:
        For multi-frame files (e.g. "Enhanced" MR/CT storage, or
        ultrasound cine loops, where one single .dcm file bundles many
        frames instead of one file per slice), which frame to show.
        Defaults to the middle frame. Ignored for single-frame files.
    """
    ds = load_dicom(source)
    array = get_pixel_array(ds)
    num_frames = int(getattr(ds, "NumberOfFrames", 1) or 1)

    frame_index: Optional[int] = None
    if array.ndim == 3 and num_frames > 1:
        frame_index = num_frames // 2 if frame is None else frame
        if not (0 <= frame_index < num_frames):
            raise ValueError(f"frame {frame_index} fuera de rango (0-{num_frames - 1})")
        array = array[frame_index]

    image = apply_windowing(array, window_center, window_width, ds=ds)

    plt.figure(figsize=(6, 6))
    plt.imshow(image, cmap="gray")
    plt.axis("off")

    if show_info:
        info = extract_dicom_info(ds)
        title = f"{info.modality or '?'} | {info.body_part_examined or '?'} | {info.rows}x{info.columns}"
        if frame_index is not None:
            title += f" | corte {frame_index}/{num_frames - 1}"
        plt.title(title, fontsize=10)

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=150)
    plt.show()


def show_volume_slices(
    volume: Volume,
    window_center: Optional[float] = None,
    window_width: Optional[float] = None,
    save_path: Optional[PathLike] = None,
) -> None:
    """Show the three orthogonal middle-slices of a 3D volume.

    Axial (top-down), coronal (front-back) and sagittal (left-right) are
    the standard three views used to inspect a CT/MRI volume. Aspect
    ratio is corrected using the real voxel spacing so slices with
    non-cubic voxels (e.g. thick axial slices) aren't distorted.
    """
    z_spacing, row_spacing, col_spacing = volume.spacing
    depth, rows, cols = volume.shape

    axial = apply_windowing(volume.axial(depth // 2), window_center, window_width)
    coronal = apply_windowing(volume.coronal(rows // 2), window_center, window_width)
    sagittal = apply_windowing(volume.sagittal(cols // 2), window_center, window_width)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8))
    fig.subplots_adjust(top=0.78)

    axes[0].imshow(axial, cmap="gray", aspect=row_spacing / col_spacing)
    axes[0].set_title(f"Axial (corte {depth // 2}/{depth})")

    axes[1].imshow(coronal, cmap="gray", aspect=z_spacing / col_spacing)
    axes[1].set_title(f"Coronal (fila {rows // 2}/{rows})")

    axes[2].imshow(sagittal, cmap="gray", aspect=z_spacing / row_spacing)
    axes[2].set_title(f"Sagital (columna {cols // 2}/{cols})")

    for ax in axes:
        ax.axis("off")

    _draw_patient_overlay(fig, volume.patient_info)

    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=150)
    plt.show()


def explore_volume(
    volume: Volume,
    window_center: Optional[float] = None,
    window_width: Optional[float] = None,
) -> None:
    """Interactive viewer for a 3D volume.

    Controls
    --------
    - Rueda del mouse (scroll): avanza/retrocede un corte en el plano actual.
    - Teclas ``a`` / ``c`` / ``s``: cambia entre plano axial / coronal / sagital.

    Requiere un backend interactivo de matplotlib (una ventana real);
    no sirve de nada con un backend no interactivo como ``Agg``.
    """
    # matplotlib ya usa 'c' y 's' como atajos por defecto (atras en el
    # historial de vista, guardar figura). Sin quitarlos de aqui, presionar
    # esas teclas dispara AMBAS cosas a la vez (ej. 's' ademas de cambiar
    # de plano abre el dialogo de guardar). 'a' no tiene atajo por defecto.
    for keymap, key in (("keymap.back", "c"), ("keymap.save", "s")):
        if key in plt.rcParams.get(keymap, []):
            plt.rcParams[keymap].remove(key)

    depth, rows, cols = volume.shape
    z_spacing, row_spacing, col_spacing = volume.spacing
    can_switch_planes = not volume.is_single_slice

    planes = {
        "axial": {"get": volume.axial, "count": depth, "aspect": row_spacing / col_spacing, "label": "Axial"},
        "coronal": {"get": volume.coronal, "count": rows, "aspect": z_spacing / col_spacing, "label": "Coronal"},
        "sagittal": {"get": volume.sagittal, "count": cols, "aspect": z_spacing / row_spacing, "label": "Sagital"},
    }
    state = {"plane": "axial", "index": depth // 2}

    fig, ax = plt.subplots(figsize=(6, 6.8))
    fig.subplots_adjust(top=0.8)
    _draw_patient_overlay(fig, volume.patient_info)

    def render() -> None:
        plane = planes[state["plane"]]
        index = state["index"]
        slice_2d = apply_windowing(plane["get"](index), window_center, window_width)

        ax.clear()
        ax.imshow(slice_2d, cmap="gray", aspect=plane["aspect"])
        hint = "scroll: navegar   |   teclas a/c/s: cambiar de plano"
        if not can_switch_planes:
            hint = "scroll: navegar (imagen de un solo corte, no hay otros planos)"
        ax.set_title(f"{plane['label']} | corte {index}/{plane['count'] - 1}\n{hint}")
        ax.axis("off")
        fig.canvas.draw_idle()

    def on_scroll(event) -> None:
        plane = planes[state["plane"]]
        step = 1 if event.button == "up" else -1
        state["index"] = int(np.clip(state["index"] + step, 0, plane["count"] - 1))
        render()

    def on_key(event) -> None:
        if not can_switch_planes:
            return
        new_plane = {"a": "axial", "c": "coronal", "s": "sagittal"}.get(event.key)
        if new_plane and new_plane != state["plane"]:
            state["plane"] = new_plane
            state["index"] = planes[new_plane]["count"] // 2
            render()

    fig.canvas.mpl_connect("scroll_event", on_scroll)
    fig.canvas.mpl_connect("key_press_event", on_key)

    render()
    plt.show()
