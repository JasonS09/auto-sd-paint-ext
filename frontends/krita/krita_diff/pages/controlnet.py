from krita import QPixmap, QImage, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, Qt

from functools import partial
from ..defaults import CONTROLNET_PREPROCESSOR_SETTINGS
from ..script import script
from ..widgets import QLabel, StatusBar, ImageLoaderLayout, QCheckBox, TipsLayout, QComboBoxLayout, QSpinBoxLayout
from ..utils import img_to_b64, b64_to_img

class ControlNetPage(QWidget):                                                      
    name = "ControlNet"

    def __init__(self, *args, **kwargs):
        super(ControlNetPage, self).__init__(*args, **kwargs)
        self.status_bar = StatusBar()
        self.controlnet_unit = QComboBoxLayout(
            script.cfg, "controlnet_unit_list", "controlnet_unit", label="Unit:"
        )
        self.controlnet_unit.qcombo.setEditable(False)
        self.controlnet_unit_layout_list = list(ControlNetUnitSettings(i) 
                                                for i in range(len(script.cfg("controlnet_unit_list"))))

        self.units_stacked_layout = QStackedLayout()
        
        for unit_layout in self.controlnet_unit_layout_list:
            self.units_stacked_layout.addWidget(unit_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.status_bar)
        layout.addLayout(self.controlnet_unit)
        layout.addLayout(self.units_stacked_layout)
        self.setLayout(layout)

    def controlnet_unit_changed(self, selected: str):
        self.units_stacked_layout.setCurrentIndex(int(selected))

    def cfg_init(self):
        self.controlnet_unit.cfg_init()
        
        for controlnet_unit_layout in self.controlnet_unit_layout_list:
            controlnet_unit_layout.cfg_init()

    def cfg_connect(self):
        self.controlnet_unit.cfg_connect()

        for controlnet_unit_layout in self.controlnet_unit_layout_list:
            controlnet_unit_layout.cfg_connect()

        self.controlnet_unit.qcombo.currentTextChanged.connect(self.controlnet_unit_changed)
        script.status_changed.connect(lambda s: self.status_bar.set_status(s))

class ControlNetUnitSettings(QWidget):    
    def __init__(self, cfg_unit_number: int = 0, *args, **kwargs):
        super(ControlNetUnitSettings, self).__init__(*args, **kwargs)           
        self.unit = cfg_unit_number

        #Top checkbox
        self.enable = QCheckBox(
            script.cfg, f"controlnet{self.unit}_enable", f"Enable ControlNet {self.unit}"
        )

        self.image_loader = ImageLoaderLayout()
        input_image = script.cfg(f"controlnet{self.unit}_input_image", str)
        self.image_loader.preview.setPixmap(
            QPixmap.fromImage(b64_to_img(input_image) if input_image else QImage())
        )

        #Main settings
        self.invert_input_color = QCheckBox(
            script.cfg, f"controlnet{self.unit}_invert_input_color", "Invert input color"
        )
        self.RGB_to_BGR = QCheckBox(
            script.cfg, f"controlnet{self.unit}_RGB_to_BGR", "RGB to BGR"
        )
        self.low_vram = QCheckBox(
            script.cfg, f"controlnet{self.unit}_low_vram", "Low VRAM"
        )
        self.guess_mode = QCheckBox(
            script.cfg, f"controlnet{self.unit}_guess_mode", "Guess mode"
        )

        #Tips
        self.tips = TipsLayout(
            ["Invert colors if your image has white background.",
             "Selection will be used as input if no image has been uploaded or pasted.",
             "Remember to set multi-controlnet in the backend as well if you want to use more than one unit."]
        )

        #Preprocessor list
        self.preprocessor_layout = QComboBoxLayout(
            script.cfg, "controlnet_preprocessor_list", f"controlnet{self.unit}_preprocessor", label="Preprocessor:"
        )

        #Model list
        self.model_layout = QComboBoxLayout(
            script.cfg, "controlnet_model_list", f"controlnet{self.unit}_model", label="Model:"
        )

        #Refresh button
        self.refresh_button = QPushButton("Refresh")

        self.weight_layout = QSpinBoxLayout(
            script.cfg, f"controlnet{self.unit}_weight", label="Weight:", min=0, max=2, step=0.05
        )
        self.guidance_start_layout = QSpinBoxLayout(
            script.cfg, f"controlnet{self.unit}_guidance_start", label="Guidance start:", min=0, max=1, step=0.01
        )
        self.guidance_end_layout = QSpinBoxLayout(
            script.cfg, f"controlnet{self.unit}_guidance_end", label="Guidance end:", min=0, max=1, step=0.01
        )

        #Preprocessor settings
        self.annotator_resolution = QSpinBoxLayout(
            script.cfg, 
            f"controlnet{self.unit}_preprocessor_resolution", 
            label="Preprocessor resolution:", 
            min=64, 
            max=2048, 
            step=1
        )
        self.threshold_a = QSpinBoxLayout(
            script.cfg,
            f"controlnet{self.unit}_threshold_a",
            label="Threshold A:",
            min=1,
            max=255,
            step=1
        )
        self.threshold_b = QSpinBoxLayout(
            script.cfg,
            f"controlnet{self.unit}_threshold_b",
            label="Threshold B:",
            min=1,
            max=255,
            step=1
        )

        #Preview annotator
        self.annotator_preview = QLabel()
        self.annotator_preview.setAlignment(Qt.AlignCenter)
        self.annotator_preview_button = QPushButton("Preview annotator")
        self.annotator_clear_button = QPushButton("Clear preview")

        main_settings_layout = QHBoxLayout()
        main_settings_layout.addWidget(self.invert_input_color)
        main_settings_layout.addWidget(self.RGB_to_BGR)
        main_settings_layout.addWidget(self.low_vram)
        main_settings_layout.addWidget(self.guess_mode)

        guidance_layout = QHBoxLayout()
        guidance_layout.addLayout(self.guidance_start_layout)
        guidance_layout.addLayout(self.guidance_end_layout)

        threshold_layout = QHBoxLayout()
        threshold_layout.addLayout(self.threshold_a)
        threshold_layout.addLayout(self.threshold_b)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.enable)
        layout.addLayout(self.image_loader)
        layout.addLayout(self.tips)
        layout.addLayout(main_settings_layout)
        layout.addLayout(self.preprocessor_layout)
        layout.addLayout(self.model_layout)
        layout.addWidget(self.refresh_button)
        layout.addLayout(self.weight_layout)
        layout.addLayout(guidance_layout)
        layout.addLayout(self.annotator_resolution)
        layout.addLayout(threshold_layout)
        layout.addWidget(self.annotator_preview)
        layout.addWidget(self.annotator_preview_button)
        layout.addWidget(self.annotator_clear_button)
        layout.addStretch()

        self.setLayout(layout)

    def set_preprocessor_options(self, selected: str):
        if selected in CONTROLNET_PREPROCESSOR_SETTINGS:
            self.show_preprocessor_options()
            self.annotator_resolution.qlabel.setText(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["resolution_label"] \
                if "resolution_label" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else "Preprocessor resolution:")
            
            if "threshold_a_label" in CONTROLNET_PREPROCESSOR_SETTINGS[selected]:
                self.threshold_a.qlabel.show()
                self.threshold_a.qspin.show()
                self.threshold_a.qlabel.setText(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_a_label"])
                self.threshold_a.qspin.setMinimum(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_a_min_value"] \
                    if "threshold_a_min_value" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else 0)
                self.threshold_a.qspin.setMaximum(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_a_max_value"] \
                    if "threshold_a_max_value" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else 0)
                self.threshold_a.qspin.setValue(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_a_value"] \
                    if "threshold_a_value" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else self.threshold_a.qspin.minimum())
                self.threshold_a.qspin.setSingleStep(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_step"] \
                    if "threshold_step" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else 1)
            else:
                self.threshold_a.qlabel.hide()
                self.threshold_a.qspin.hide()
            
            if "threshold_b_label" in CONTROLNET_PREPROCESSOR_SETTINGS[selected]:
                self.threshold_b.qlabel.show()
                self.threshold_b.qspin.show()
                self.threshold_b.qlabel.setText(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_b_label"])
                self.threshold_b.qspin.setMinimum(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_b_min_value"] \
                    if "threshold_b_min_value" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else 0)
                self.threshold_b.qspin.setMaximum(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_b_max_value"] \
                    if "threshold_b_max_value" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else 0)
                self.threshold_b.qspin.setValue(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_b_value"] \
                    if "threshold_b_value" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else self.threshold_b.qspin.minimum())
                self.threshold_b.qspin.setSingleStep(CONTROLNET_PREPROCESSOR_SETTINGS[selected]["threshold_b_step"] \
                    if "threshold_b_step" in CONTROLNET_PREPROCESSOR_SETTINGS[selected] else 1)
            else:
                self.threshold_b.qlabel.hide()
                self.threshold_b.qspin.hide()
        else:
            self.hide_preprocessor_options(selected)
    
    def hide_preprocessor_options(self, selected: str):
        #Hide all annotator settings if no annotator chosen.
        #if there is an annotator that hasn't been listed in defaults,
        #just show resolution option. Users may be able to play
        #with new unsupported annotators, but they may or not work.
        if selected == "none":
            self.annotator_resolution.qlabel.hide()
            self.annotator_resolution.qspin.hide()

        self.threshold_a.qlabel.hide()
        self.threshold_a.qspin.hide()
        self.threshold_b.qlabel.hide()
        self.threshold_b.qspin.hide()

    def show_preprocessor_options(self):
        self.annotator_resolution.qlabel.show()
        self.annotator_resolution.qspin.show()
        self.threshold_a.qlabel.show()
        self.threshold_a.qspin.show()
        self.threshold_b.qlabel.show()
        self.threshold_b.qspin.show()

    def enable_changed(self, state):
        if state == 1 or state == 2:
            script.action_update_controlnet_config()

    def image_loaded(self):
        image = self.image_loader.preview.pixmap().toImage().convertToFormat(QImage.Format_RGBA8888)
        script.cfg.set(f"controlnet{self.unit}_input_image", img_to_b64(image))
           
    def cfg_init(self):  
        self.enable.cfg_init()
        self.invert_input_color.cfg_init()
        self.RGB_to_BGR.cfg_init()
        self.low_vram.cfg_init()
        self.guess_mode.cfg_init()
        self.preprocessor_layout.cfg_init()
        self.model_layout.cfg_init()
        self.weight_layout.cfg_init()
        self.guidance_start_layout.cfg_init()
        self.guidance_end_layout.cfg_init()
        self.annotator_resolution.cfg_init()
        self.threshold_a.cfg_init()
        self.threshold_b.cfg_init()
        self.set_preprocessor_options(self.preprocessor_layout.qcombo.currentText())

        if (self.preprocessor_layout.qcombo.currentText() == "none"):
            self.annotator_preview_button.setEnabled(False)
        else:
            self.annotator_preview_button.setEnabled(True)

    def cfg_connect(self):
        self.enable.cfg_connect()
        self.invert_input_color.cfg_connect()
        self.RGB_to_BGR.cfg_connect()
        self.low_vram.cfg_connect()
        self.guess_mode.cfg_connect()
        self.preprocessor_layout.cfg_connect()
        self.model_layout.cfg_connect()
        self.weight_layout.cfg_connect()
        self.guidance_start_layout.cfg_connect()
        self.guidance_end_layout.cfg_connect()
        self.annotator_resolution.cfg_connect()
        self.threshold_a.cfg_connect()
        self.threshold_b.cfg_connect()
        self.enable.stateChanged.connect(self.enable_changed)
        self.image_loader.import_button.released.connect(self.image_loaded)
        self.image_loader.paste_button.released.connect(self.image_loaded)
        self.image_loader.clear_button.released.connect(
            partial(script.cfg.set, f"controlnet{self.unit}_input_image", "")
        )
        self.preprocessor_layout.qcombo.currentTextChanged.connect(self.set_preprocessor_options)
        self.preprocessor_layout.qcombo.currentTextChanged.connect(
            lambda: self.annotator_preview_button.setEnabled(False) if 
                self.preprocessor_layout.qcombo.currentText() == "none" else self.annotator_preview_button.setEnabled(True)
        )
        self.refresh_button.released.connect(lambda: script.action_update_controlnet_config())
        self.annotator_preview_button.released.connect(
            lambda: script.action_preview_controlnet_annotator(self.annotator_preview)
        )
        self.annotator_clear_button.released.connect(lambda: self.annotator_preview.setPixmap(QPixmap()))