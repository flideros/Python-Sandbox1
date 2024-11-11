from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QStackedWidget
import sys
from jupyter_widget import JupyterWidget
from main_widgets import ButtonLabelWidget  
from basic_calculator_widget import BasicCalculatorWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Frank Math Navigator')
        self.resize(250, 150)

        # Create stacked widget
        self.stacked_widget = QStackedWidget()

        # Create main menu layout
        self.main_menu = QWidget()
        self.main_layout = QVBoxLayout()
        QIcon.setThemeName("Papirus")

        # Add button
        self.jupyter_widget_btn = ButtonLabelWidget(
            label_text='Jupyter Lab',
            button_text='Launch',
            button_callback=self.show_jupyter)
        self.jupyter_widget_btn.button.setIcon(QIcon.fromTheme("jupyter"))
        self.jupyter_widget_btn.button.setIconSize(QSize(24, 24))
        
        self.basic_calculator_window_btn = ButtonLabelWidget(
            label_text='Basic Calculator',
            button_text='Launch',
            button_callback=self.show_calculator)
        self.basic_calculator_window_btn.button.setIcon(QIcon.fromTheme("accessories-calculator"))
        self.basic_calculator_window_btn.button.setIconSize(QSize(24, 24))
        
        self.main_layout.addWidget(self.jupyter_widget_btn)
        self.main_layout.addWidget(self.basic_calculator_window_btn)

        self.main_menu.setLayout(self.main_layout)

        # Add widgets to stacked widget
        self.stacked_widget.addWidget(self.main_menu)

        self.jupyter_widget = None

        self.setCentralWidget(self.stacked_widget)

    def show_jupyter(self):
        if self.jupyter_widget is None:
            self.resize(800, 600)
            self.jupyter_widget = JupyterWidget(self.show_main_menu, extra_param="Extra Info")
            self.stacked_widget.addWidget(self.jupyter_widget)
        self.stacked_widget.setCurrentWidget(self.jupyter_widget)

    def show_calculator(self):
        self.basic_calculator_window = BasicCalculatorWindow()
        self.basic_calculator_window.show()

    def show_main_menu(self):
        if self.jupyter_widget:
            self.resize(250, 150)
            self.jupyter_widget.stop_jupyter()
            self.jupyter_widget = None
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def closeEvent(self, event):
        if self.jupyter_widget:
            self.jupyter_widget.stop_jupyter()
        event.accept()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
