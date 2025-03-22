import sys
import platform
import subprocess
import psutil
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal

def get_motherboard_name():
    """
    Returns a shortened version of the motherboard/baseboard name if possible.
    If it can't retrieve it, returns 'Unknown Board'.
    """
    try:
        system_name = platform.system()
        mb_name = "Unknown Board"

        if system_name == "Windows":
            # Use wmic to get baseboard product info
            cmd = "wmic baseboard get product"
            output = subprocess.check_output(cmd, shell=True).decode(errors="ignore")
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            if len(lines) > 1:
                mb_name = lines[1]
        elif system_name == "Linux":
            # Read from /sys/class/dmi/id/board_name if available
            try:
                with open("/sys/class/dmi/id/board_name", "r") as f:
                    mb_name = f.read().strip()
            except FileNotFoundError:
                pass
        else:
            mb_name = "Unknown Board"

        # Shorten if necessary
        if len(mb_name) > 20:
            mb_name = mb_name[:20] + "..."

        return mb_name

    except Exception:
        return "Unknown Board"

class MoreInfoWindow(QDialog):
    dark_mode_changed = pyqtSignal(bool)  # Signal to notify about dark mode change

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.setWindowTitle("System Information")
        self.setFixedSize(700, 400)
        
        self.dark_mode = dark_mode
        self.apply_dark_mode()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        image_label = QLabel(self)
        pixmap = QPixmap("Os.png")
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(image_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(10)
        
        os_version = platform.system() + " " + platform.release()
        cpu_info = platform.processor() or "Unknown CPU"
        memory_info = f"{int(psutil.virtual_memory().total / (1024**3))} GB"
        disk_info = "System Drive"
        display_info = "Unknown Display"
        graphics_info = "Unknown GPU"
        bootloader_info = "UEFI"
        
        info_texts = [
            ("macOS Version", os_version),
            ("Chip", cpu_info),
            ("Memory", memory_info),
            ("Startup Disk", disk_info),
            ("Display", display_info),
            ("Graphics", graphics_info),
            ("Bootloader", bootloader_info)
        ]
        
        for title, value in info_texts:
            label = QLabel(f"<b>{title}:</b> {value}")
            label.setStyleSheet("font-size: 14px;")
            text_layout.addWidget(label)
        
        text_layout.addStretch()
        
        self.dark_mode_button = QPushButton("Toggle Dark Mode")
        self.dark_mode_button.setFixedSize(140, 30)
        self.dark_mode_button.setStyleSheet(
            "background-color: #555; color: white; border-radius: 5px; padding: 5px;"
        )
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        text_layout.addWidget(self.dark_mode_button, 0, Qt.AlignLeft)
        
        copyright_label = QLabel("\u00a9 2024 Apple Inc. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignLeft)
        copyright_label.setStyleSheet("font-size: 12px; color: gray;")
        text_layout.addWidget(copyright_label)
        
        main_layout.addLayout(text_layout)
        self.setLayout(main_layout)
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_dark_mode()
        self.dark_mode_changed.emit(self.dark_mode)  # Emit signal to parent window

    def apply_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: #1E1E1E; color: white;")
        else:
            self.setStyleSheet("background-color: white; color: black;")

class AboutThisMac(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About This Mac (Replica)")
        self.setFixedSize(400, 550)

        self.dark_mode = False  # Start with light mode
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. Top Image (Laptop placeholder)
        self.laptop_label = QLabel()
        pixmap = QPixmap("device.png")
        pixmap = pixmap.scaled(200, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.laptop_label.setPixmap(pixmap)
        self.laptop_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.laptop_label)

        # 2. Motherboard name as title
        mb_name = get_motherboard_name()
        self.mac_title = QLabel(mb_name)
        font_title = QFont("Arial", 18, QFont.Bold)
        self.mac_title.setFont(font_title)
        self.mac_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.mac_title)

        # 3. Info section (chip, memory, disk, serial, OS)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        cpu_info = platform.processor() or "Unknown CPU"
        total_memory = psutil.virtual_memory().total / (1024**3)
        os_info = platform.system() + " " + platform.release()
        serial_number = "X0ZYZ1ZYZX"
        startup_disk = "System Drive"

        chip_label = QLabel(f"<b>Chip</b>: {cpu_info}")
        memory_label = QLabel(f"<b>Memory</b>: {int(total_memory)} GB")
        startup_label = QLabel(f"<b>Startup disk</b>: {startup_disk}")
        serial_label = QLabel(f"<b>Serial number</b>: {serial_number}")
        os_label = QLabel(f"<b>OS</b>: {os_info}")

        for lbl in [chip_label, memory_label, startup_label, serial_label, os_label]:
            lbl.setStyleSheet("font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            info_layout.addWidget(lbl)

        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        main_layout.addWidget(info_widget, 0, Qt.AlignCenter)

        # 4. “More Info...” button with macOS style (no border)
        self.more_info_button = QPushButton("More Info...")
        self.more_info_button.setFixedSize(120, 30)
        self.more_info_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """)
        self.more_info_button.clicked.connect(self.show_more_info)
        main_layout.addWidget(self.more_info_button, 0, Qt.AlignCenter)

        self.setLayout(main_layout)

    def show_more_info(self):
        self.more_info_window = MoreInfoWindow(self, self.dark_mode)
        self.more_info_window.dark_mode_changed.connect(self.update_dark_mode)  # Connect signal
        self.more_info_window.exec_()

    def update_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self.apply_dark_mode()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_dark_mode()

    def apply_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: #1E1E1E; color: white;")
        else:
            self.setStyleSheet("background-color: white; color: black;")

def main():
    app = QApplication(sys.argv)
    about_dialog = AboutThisMac()
    about_dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
