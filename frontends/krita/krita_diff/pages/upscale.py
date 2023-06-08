from krita import QPushButton, QVBoxLayout, QWidget, QHBoxLayout

from ..script import script
from ..widgets import QCheckBox, QComboBoxLayout, QLabel, StatusBar, QSpinBoxLayout


# TODO: Become SD Upscale tab.
class UpscalePage(QWidget):
    name = "Upscale"

    def __init__(self, *args, **kwargs):
        super(UpscalePage, self).__init__(*args, **kwargs)

        self.status_bar = StatusBar()

        self.upscaler_layout = QComboBoxLayout(
            script.cfg, "upscaler_list", "upscale_upscaler_name", label="Upscaler:"
        )

        self.note = QLabel(
            """
NOTE:<br/>
 - txt2img & img2img will use the <em>Quick Config</em> Upscaler when needing to scale up.<br/>
 - Upscaling manually is only useful if the image was resized via Krita.<br/>
 - img2img prompt and settings will influence the upscaling result!<br/>
            """
        )
        self.note.setWordWrap(True)

        # Tiled Diffusion
        self.tiled_diffusion_title = QLabel("<em>Tiled Diffusion</em>")

        self.diffusion_method = QComboBoxLayout(
            script.cfg, "tiled_diffusion_method_list", "tiled_diffusion_method", label="Method:"
        )

        self.latent_tile_width = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_latent_tile_width",
            label="Latent tile width:",
            min=16,
            max=256,
            step=16,
        )
        self.latent_tile_height = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_latent_tile_height",
            label="Latent tile height:",
            min=16,
            max=256,
            step=16,
        )

        tiled_diffusion_second_row_layout = QHBoxLayout()
        tiled_diffusion_second_row_layout.addLayout(self.latent_tile_width)
        tiled_diffusion_second_row_layout.addLayout(self.latent_tile_height)

        self.latent_tile_overlap = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_latent_tile_overlap",
            label="Latent tile overlap:",
            min=0,
            max=256,
            step=4,
        )
        self.latent_tile_batch_size = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_latent_tile_batch_size",
            label="Latent tile batch size:",
            min=1,
            max=8,
            step=1,
        )
        self.scale_factor = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_scale_factor",
            label="Scale factor:",
            min=1,
            max=8,
            step=0.05,
        )

        tiled_diffusion_third_row_layout = QHBoxLayout()
        tiled_diffusion_third_row_layout.addLayout(self.latent_tile_overlap)
        tiled_diffusion_third_row_layout.addLayout(self.latent_tile_batch_size)
        tiled_diffusion_third_row_layout.addLayout(self.scale_factor)

        # Noise inversion
        self.noise_inversion_title = QLabel("<em>Noise inversion</em>")
        self.enable_noise_inversion = QCheckBox(script.cfg, "tiled_diffusion_enable_noise_inversion", "Enable")
        self.inversion_steps = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_inversion_steps",
            label="Inversion steps:",
            min=1,
            max=100,
            step=1,
        )

        tiled_diffusion_fourth_row_layout = QHBoxLayout()
        tiled_diffusion_fourth_row_layout.addWidget(self.enable_noise_inversion)
        tiled_diffusion_fourth_row_layout.addLayout(self.inversion_steps)

        self.retouch = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_retouch",
            label="Retouch:",
            min=0.0,
            max=100.0,
            step=0.1,
        )
        self.renoise_strength = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_renoise_strength",
            label="Renoise strength:",
            min=0.0,
            max=2.0,
            step=0.01,
        )
        self.renoise_kernel_size = QSpinBoxLayout(
            script.cfg,
            "tiled_diffusion_renoise_kernel_size",
            label="Renoise kernel size:",
            min=2,
            max=512,
            step=1
         )

        tiled_diffusion_fifth_row_layout = QHBoxLayout()
        tiled_diffusion_fifth_row_layout.addLayout(self.retouch)
        tiled_diffusion_fifth_row_layout.addLayout(self.renoise_strength)
        tiled_diffusion_fifth_row_layout.addLayout(self.renoise_kernel_size)

        self.btn = QPushButton("Start upscaling")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.status_bar)
        layout.addWidget(self.note)
        layout.addLayout(self.upscaler_layout)
        layout.addLayout(self.diffusion_method)
        layout.addLayout(tiled_diffusion_second_row_layout)
        layout.addLayout(tiled_diffusion_third_row_layout)
        layout.addWidget(self.noise_inversion_title)
        layout.addLayout(tiled_diffusion_fourth_row_layout)
        layout.addLayout(tiled_diffusion_fifth_row_layout)
        layout.addWidget(self.btn)
        layout.addStretch()

        self.setLayout(layout)

    def cfg_init(self):
        self.upscaler_layout.cfg_init()
        self.diffusion_method.cfg_init()
        self.latent_tile_width.cfg_init()
        self.latent_tile_height.cfg_init()
        self.latent_tile_overlap.cfg_init()
        self.latent_tile_batch_size.cfg_init()
        self.scale_factor.cfg_init()
        self.enable_noise_inversion.cfg_init()
        self.inversion_steps.cfg_init()
        self.retouch.cfg_init()
        self.renoise_strength.cfg_init()
        self.renoise_kernel_size.cfg_init()
        self.note.setVisible(not script.cfg("minimize_ui", bool))

    def cfg_connect(self):
        self.upscaler_layout.cfg_connect()
        self.diffusion_method.cfg_connect()
        self.latent_tile_width.cfg_connect()
        self.latent_tile_height.cfg_connect()
        self.latent_tile_overlap.cfg_connect()
        self.latent_tile_batch_size.cfg_connect()
        self.scale_factor.cfg_connect()
        self.enable_noise_inversion.cfg_connect()
        self.inversion_steps.cfg_connect()
        self.retouch.cfg_connect()
        self.renoise_strength.cfg_connect()
        self.renoise_kernel_size.cfg_connect()
        self.btn.released.connect(lambda: script.action_upscale())
        script.status_changed.connect(lambda s: self.status_bar.set_status(s))
