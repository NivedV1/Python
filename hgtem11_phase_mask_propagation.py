from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)
from scipy.special import eval_hermite

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gs_phase_app.models import OpticalConfig
from gs_phase_app.solver import (
    centered_coordinate_bounds,
    extract_camera_view,
    fourier_plane_sampling,
    propagate_angular_spectrum,
)


DEFAULTS: dict[str, float | int | str] = {
    "wavelength_nm": 1064.0,
    "focal_length_mm": 20.0,
    "beam_waist_mm": 1.0,
    "slm_width_px": 1072,
    "slm_height_px": 1024,
    "slm_pitch_x_um": 8.0,
    "slm_pitch_y_um": 8.0,
    "camera_width_px": 600,
    "camera_height_px": 600,
    "camera_pitch_x_um": 5.5,
    "camera_pitch_y_um": 5.5,
    "hg_mode": "HG11",
    "z_span_mm": 10.0,
    "z_samples": 101,
}


def fft2c(field: np.ndarray) -> np.ndarray:
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(field), norm="ortho"))


def _hg_axis_factor(coordinate: np.ndarray, beam_waist_m: float, order: int) -> np.ndarray:
    if order < 0:
        raise ValueError(f"Unsupported HG order: {order}")
    scaled_coordinate = (np.sqrt(2.0) * coordinate) / beam_waist_m
    return eval_hermite(order, scaled_coordinate)


def build_hg_mode_amplitude(config: OpticalConfig, mode_name: str) -> np.ndarray:
    ny, nx = config.slm_shape
    x = (np.arange(nx) - (nx - 1) / 2.0) * config.slm_pitch_x_m
    y = ((ny - 1) / 2.0 - np.arange(ny)) * config.slm_pitch_y_m
    x_grid, y_grid = np.meshgrid(x, y)

    cleaned_mode = "".join(ch for ch in mode_name.strip().upper().replace("TEM", "").replace("HG", "") if ch.isdigit())
    if len(cleaned_mode) != 2:
        raise ValueError(f"Unsupported mode name: {mode_name}")

    x_order = int(cleaned_mode[0])
    y_order = int(cleaned_mode[1])
    w0 = config.beam_waist_m
    amplitude = _hg_axis_factor(x_grid, w0, x_order) * _hg_axis_factor(y_grid, w0, y_order)
    amplitude *= np.exp(-(x_grid * x_grid + y_grid * y_grid) / (w0 * w0))
    amplitude /= np.max(np.abs(amplitude)) + 1e-12
    return amplitude.astype(np.float64)


def load_phase_mask_image(image_path: str | Path, shape: tuple[int, int]) -> tuple[np.ndarray, str]:
    image = Image.open(image_path).convert("L")
    image_array = np.asarray(image, dtype=np.uint8)
    unique_values = np.unique(image_array)

    is_binary_like = unique_values.size <= 2
    resample_method = Image.Resampling.NEAREST if is_binary_like else Image.Resampling.BILINEAR
    image = image.resize((shape[1], shape[0]), resample_method)
    resized = np.asarray(image, dtype=np.uint8)

    if is_binary_like:
        low_value = int(unique_values.min())
        high_value = int(unique_values.max())
        threshold = (low_value + high_value) / 2.0
        binary_mask = (resized > threshold).astype(np.float64)
        phase_mask = binary_mask * np.pi
        description = f"binary 0/pi mask detected from levels {low_value} and {high_value}"
        return phase_mask, description

    phase_mask = (resized.astype(np.float64) / 255.0) * (2.0 * np.pi)
    return phase_mask, "grayscale 0..2pi mask"


class PlotPanel(QWidget):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(title)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def show_image(
        self,
        data: np.ndarray,
        extent: tuple[float, float, float, float],
        title: str,
        cmap: str,
        x_label: str,
        y_label: str,
    ) -> None:
        self.ax.clear()
        self.ax.set_title(title)
        self.ax.imshow(
            data,
            origin="lower",
            extent=extent,
            cmap=cmap,
            aspect="auto",
            interpolation="nearest",
        )
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.canvas.draw_idle()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("HG TEM11 Phase-Mask Propagation")
        self.resize(1600, 950)

        self.phase_mask_path: Path | None = None
        self.selected_mode = str(DEFAULTS["hg_mode"])
        self.precomputed_z_intensities: list[np.ndarray] = []
        self.precomputed_z_values_m: list[float] = []
        self.phase_panel: PlotPanel | None = None
        self.source_panel: PlotPanel | None = None
        self.fourier_panel: PlotPanel | None = None
        self.z_scan_panel: PlotPanel | None = None
        self.plots_layout: QGridLayout | None = None
        self.status_label: QLabel | None = None
        self.z_slider: QSlider | None = None
        self.z_value_label: QLabel | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)

        controls = self._build_controls()
        root_layout.addWidget(controls, 0)

        plots_host = QWidget()
        self.plots_layout = QGridLayout(plots_host)
        self.plots_layout.setColumnStretch(0, 1)
        self.plots_layout.setColumnStretch(1, 1)
        self.plots_layout.setRowStretch(0, 1)
        self.plots_layout.setRowStretch(1, 1)

        self.phase_panel = PlotPanel("Loaded Phase Mask")
        self.source_panel = PlotPanel("HG TEM11 Input Beam Intensity")
        self.fourier_panel = PlotPanel("Fourier Plane Intensity (Camera View)")
        self.z_scan_panel = PlotPanel("Intensity at z = 0.000 mm")
        self.plots_layout.addWidget(self.phase_panel, 0, 0)
        self.plots_layout.addWidget(self.source_panel, 0, 1)
        self.plots_layout.addWidget(self.fourier_panel, 1, 0)
        self.plots_layout.addWidget(self.z_scan_panel, 1, 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(plots_host)
        root_layout.addWidget(scroll, 1)

        self.setCentralWidget(root)

    def _build_controls(self) -> QWidget:
        box = QGroupBox("Simulation Controls")
        layout = QVBoxLayout(box)

        form = QFormLayout()

        self.wavelength_nm = self._double_spin(100.0, 5000.0, 3, float(DEFAULTS["wavelength_nm"]))
        self.focal_length_mm = self._double_spin(1.0, 5000.0, 3, float(DEFAULTS["focal_length_mm"]))
        self.beam_waist_mm = self._double_spin(0.001, 50.0, 4, float(DEFAULTS["beam_waist_mm"]))
        self.slm_width_px = self._int_spin(16, 8192, int(DEFAULTS["slm_width_px"]))
        self.slm_height_px = self._int_spin(16, 8192, int(DEFAULTS["slm_height_px"]))
        self.slm_pitch_x_um = self._double_spin(0.01, 500.0, 4, float(DEFAULTS["slm_pitch_x_um"]))
        self.slm_pitch_y_um = self._double_spin(0.01, 500.0, 4, float(DEFAULTS["slm_pitch_y_um"]))
        self.camera_width_px = self._int_spin(16, 8192, int(DEFAULTS["camera_width_px"]))
        self.camera_height_px = self._int_spin(16, 8192, int(DEFAULTS["camera_height_px"]))
        self.camera_pitch_x_um = self._double_spin(0.01, 500.0, 4, float(DEFAULTS["camera_pitch_x_um"]))
        self.camera_pitch_y_um = self._double_spin(0.01, 500.0, 4, float(DEFAULTS["camera_pitch_y_um"]))
        self.z_span_mm = self._double_spin(0.001, 1000.0, 3, float(DEFAULTS["z_span_mm"]))
        self.z_samples = self._int_spin(3, 2001, int(DEFAULTS["z_samples"]))
        self.mode_combo = QComboBox()
        self.mode_combo.setEditable(True)
        self.mode_combo.addItems(["HG00", "HG01", "HG10", "HG11", "HG20", "HG02", "HG21", "HG12", "HG22"])
        self.mode_combo.setCurrentText(self.selected_mode)
        self.mode_combo.currentTextChanged.connect(self._update_mode)

        form.addRow("Wavelength (nm)", self.wavelength_nm)
        form.addRow("Focal length (mm)", self.focal_length_mm)
        form.addRow("Beam waist (mm)", self.beam_waist_mm)
        form.addRow("SLM width (px)", self.slm_width_px)
        form.addRow("SLM height (px)", self.slm_height_px)
        form.addRow("SLM pitch x (um)", self.slm_pitch_x_um)
        form.addRow("SLM pitch y (um)", self.slm_pitch_y_um)
        form.addRow("Camera width (px)", self.camera_width_px)
        form.addRow("Camera height (px)", self.camera_height_px)
        form.addRow("Camera pitch x (um)", self.camera_pitch_x_um)
        form.addRow("Camera pitch y (um)", self.camera_pitch_y_um)
        form.addRow("Input laser mode", self.mode_combo)
        form.addRow("z span each side (mm)", self.z_span_mm)
        form.addRow("z samples", self.z_samples)
        layout.addLayout(form)

        file_row = QHBoxLayout()
        self.phase_path_label = QLabel("No phase mask selected")
        self.phase_path_label.setWordWrap(True)
        load_button = QPushButton("Load Phase Mask")
        load_button.clicked.connect(self._choose_phase_mask)
        file_row.addWidget(load_button)
        file_row.addWidget(self.phase_path_label, 1)
        layout.addLayout(file_row)

        run_button = QPushButton("Run Propagation")
        run_button.clicked.connect(self._run_propagation)
        layout.addWidget(run_button)

        self.z_value_label = QLabel("z = 0.000 mm")
        layout.addWidget(self.z_value_label)

        self.z_slider = QSlider(Qt.Orientation.Horizontal)
        self.z_slider.setEnabled(False)
        self.z_slider.valueChanged.connect(self._update_z_plane_view)
        layout.addWidget(self.z_slider)

        self.status_label = QLabel("Choose a phase-mask image, then run the propagation.")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch(1)
        return box

    def _update_mode(self, mode_name: str) -> None:
        self.selected_mode = mode_name.strip().upper() or "HG00"

    def _double_spin(self, min_value: float, max_value: float, decimals: int, value: float) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(min_value, max_value)
        box.setDecimals(decimals)
        box.setSingleStep(max(10 ** (-decimals), 0.1))
        box.setValue(value)
        return box

    def _int_spin(self, min_value: int, max_value: int, value: int) -> QSpinBox:
        box = QSpinBox()
        box.setRange(min_value, max_value)
        box.setValue(value)
        return box

    def _choose_phase_mask(self) -> None:
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select phase-mask image",
            str(PROJECT_ROOT),
            "Images (*.bmp *.png *.jpg *.jpeg *.tif *.tiff)",
        )
        if not selected_path:
            return

        self.phase_mask_path = Path(selected_path)
        self.phase_path_label.setText(self.phase_mask_path.name)
        if self.status_label is not None:
            self.status_label.setText(f"Loaded phase mask: {self.phase_mask_path.name}")

    def _optical_config(self) -> OpticalConfig:
        config = OpticalConfig(
            wavelength_m=self.wavelength_nm.value() * 1e-9,
            focal_length_m=self.focal_length_mm.value() * 1e-3,
            beam_waist_m=self.beam_waist_mm.value() * 1e-3,
            slm_width_px=self.slm_width_px.value(),
            slm_height_px=self.slm_height_px.value(),
            slm_pitch_x_m=self.slm_pitch_x_um.value() * 1e-6,
            slm_pitch_y_m=self.slm_pitch_y_um.value() * 1e-6,
            camera_width_px=self.camera_width_px.value(),
            camera_height_px=self.camera_height_px.value(),
            camera_pitch_x_m=self.camera_pitch_x_um.value() * 1e-6,
            camera_pitch_y_m=self.camera_pitch_y_um.value() * 1e-6,
        )
        config.validate()
        return config

    def _z_sampling(self) -> tuple[np.ndarray, int]:
        sample_count = self.z_samples.value()
        if sample_count % 2 == 0:
            sample_count += 1
            self.z_samples.setValue(sample_count)

        z_span_m = self.z_span_mm.value() * 1e-3
        z_values_m = np.linspace(-z_span_m, z_span_m, sample_count)
        return z_values_m, sample_count // 2

    def _update_z_plane_view(self, slider_index: int) -> None:
        if (
            self.z_scan_panel is None
            or self.z_value_label is None
            or not self.precomputed_z_intensities
            or not self.precomputed_z_values_m
        ):
            return

        z_m = self.precomputed_z_values_m[slider_index]
        intensity = self.precomputed_z_intensities[slider_index]
        (cam_x_min, cam_x_max), (cam_y_min, cam_y_max) = centered_coordinate_bounds(
            self.camera_width_px.value(),
            self.camera_height_px.value(),
        )
        cam_extent = (cam_x_min, cam_x_max, cam_y_min, cam_y_max)
        self.z_scan_panel.show_image(
            intensity,
            cam_extent,
            f"Intensity at z = {z_m * 1e3:.3f} mm",
            "inferno",
            "x (camera px centered)",
            "y (camera px centered)",
        )
        self.z_value_label.setText(f"z = {z_m * 1e3:.3f} mm")

    def _run_propagation(self) -> None:
        if self.phase_mask_path is None:
            QMessageBox.warning(self, "Missing phase mask", "Select a phase-mask image first.")
            return

        try:
            config = self._optical_config()
            z_values_m, center_index = self._z_sampling()
            phase_mask, mask_description = load_phase_mask_image(self.phase_mask_path, config.slm_shape)
            source_amp = build_hg_mode_amplitude(config, self.selected_mode)
            field_slm = source_amp * np.exp(1.0j * phase_mask)

            fourier_field = fft2c(field_slm)
            fourier_intensity = np.abs(fourier_field) ** 2
            source_intensity = np.abs(source_amp) ** 2

            fourier_camera = extract_camera_view(fourier_intensity, config)
            dx_f, dy_f = fourier_plane_sampling(config)

            (slm_x_min, slm_x_max), (slm_y_min, slm_y_max) = centered_coordinate_bounds(
                config.slm_width_px,
                config.slm_height_px,
            )
            slm_extent = (slm_x_min, slm_x_max, slm_y_min, slm_y_max)

            (cam_x_min, cam_x_max), (cam_y_min, cam_y_max) = centered_coordinate_bounds(
                config.camera_width_px,
                config.camera_height_px,
            )
            cam_extent = (cam_x_min, cam_x_max, cam_y_min, cam_y_max)

            if self.phase_panel is not None:
                self.phase_panel.show_image(
                    phase_mask,
                    slm_extent,
                    "Loaded Phase Mask",
                    "gray",
                    "x (SLM px centered)",
                    "y (SLM px centered)",
                )
            if self.source_panel is not None:
                self.source_panel.show_image(
                    source_intensity,
                    slm_extent,
                    f"{self.selected_mode} Input Beam Intensity",
                    "viridis",
                    "x (SLM px centered)",
                    "y (SLM px centered)",
                )
            if self.fourier_panel is not None:
                self.fourier_panel.show_image(
                    fourier_camera,
                    cam_extent,
                    "Fourier Plane Intensity (Camera View)",
                    "inferno",
                    "x (camera px centered)",
                    "y (camera px centered)",
                )

            self.precomputed_z_values_m = [float(z_m) for z_m in z_values_m]
            self.precomputed_z_intensities = []
            for z_m in z_values_m:
                if abs(z_m) < 1e-15:
                    intensity = fourier_camera.copy()
                else:
                    propagated = propagate_angular_spectrum(
                        fourier_field,
                        dx_f,
                        dy_f,
                        config.wavelength_m,
                        float(z_m),
                    )
                    intensity = extract_camera_view(np.abs(propagated) ** 2, config)
                self.precomputed_z_intensities.append(intensity)

            if self.z_slider is not None:
                self.z_slider.blockSignals(True)
                self.z_slider.setEnabled(True)
                self.z_slider.setMinimum(0)
                self.z_slider.setMaximum(len(self.precomputed_z_intensities) - 1)
                self.z_slider.setValue(center_index)
                self.z_slider.blockSignals(False)
            self._update_z_plane_view(center_index)

            if self.status_label is not None:
                self.status_label.setText(
                    f"Completed propagation for {self.selected_mode} across {len(self.precomputed_z_intensities)} precomputed z positions using {self.phase_mask_path.name} ({mask_description})."
                )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Propagation failed", str(exc))
            if self.status_label is not None:
                self.status_label.setText(f"Failed: {exc}")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
