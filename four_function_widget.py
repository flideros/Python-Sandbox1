# ================================================
# UI for Four Function Calculator
# ================================================
from PyQt6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QPushButton,
                             QLabel, QWidget, QStyle, QFrame, QSizePolicy,
                             QComboBox)
from PyQt6.QtGui import QFont, QIcon, QMouseEvent
from PyQt6.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from calculator_services import CalculatorServices
from compute_services import ComputeServices
from calculator_implementation import create_calculate
from compute_implementation import create_compute
from ten_key_widget import TenKey
from enum import Enum

class FourFunctionCalculator(QWidget):
    def __init__(self):
        super().__init__()

        # Set up services and state        
        services = ComputeServices()
        self.services = services
        self.state = self.services.initial_state
        self.compute = create_compute(services)
        self.current_input = None
                
        self.send_ten_key_display = self.services.receive_ten_key_display
        self.get_digit_display = self.services.get_digit_display
  
        # ------Create Constants and Widgets---------
        # Constants for Styles
        grid_color = "#F5F5DC"         
        background_color = "#F6F7F9"
        memory_recall = "#8FBC8F"
        BUTTON_PADDING = "5px"
        BUTTON_FONT_SIZE = "14pt"
        BORDER_RADIUS = "5px"
        BORDER_COLOR = "#656565"
        HOVER_COLOR = "#c8c8c8"
        BUTTON_COLOR = "#ebebeb"
  
        # Style Sheets
        # Common Button Style
        button_style_base = f"""
            background-color: {BUTTON_COLOR};
            border: 1px solid {BORDER_COLOR}; 
            border-radius: {BORDER_RADIUS}; 
            padding: {BUTTON_PADDING};
        """
        # Style for Normal Buttons
        button_style = f"""
            QPushButton {{
                {button_style_base}
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};
                border: 1px solid {HOVER_COLOR};
            }}
        """
        # Style the combo box to look like a button with padding and height
        combo_box_style = f"""
            QComboBox {{
                background-color: #ebebeb;
                border: 1px solid #656565;
                border-radius: 5px;
                padding: 5px;
                font-size: 14pt;
                font-family: Arial, sans-serif;                
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            QComboBox::down-arrow {{
                width: 10px;
                height: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BUTTON_COLOR};
                border: 1px solid {BORDER_COLOR};
                selection-background-color: {HOVER_COLOR};
            }}
        """
        # Main layout
        self.vbox = QVBoxLayout()
        
        # Development Label
        self.label = QLabel('This is a label', self)
        self.vbox.addWidget(self.label)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create Choice combo box
        self.combo_box = QComboBox()
        self.combo_box.addItem("Sqrt")
        self.combo_box.addItem("Power")
        
        self.combo_box.setStyleSheet(combo_box_style)
        
        # Create the horizontal layout to hold the ten key and additional grid
        self.hbox = QHBoxLayout()
        
        # 10-key Widget
        self.ten_key = TenKey('digits_mr_decimal')
        self.ten_key.buttonClicked.connect(self.handleButtonClicked)
        self.ten_key.inputClicked.connect(lambda x: self.handleInputClicked(x))
        self.ten_key.result.hide()
        self.ten_key_grid_layout = QGridLayout()
        self.ten_key_grid_layout.addWidget(self.ten_key)        
                
        # 4x2 button grid layout
        self.function_button_grid_layout = QGridLayout()
        self.setup_function_buttons(button_style)
        self.function_button_grid_layout.setContentsMargins(0, 20, 20, 20)
        
        # 1x5 utility button grid layout
        self.utility_button_grid_layout = QGridLayout()
        self.setup_utility_buttons(button_style)
        self.utility_button_grid_layout.setContentsMargins(20, 20, 20, 0)
        
        # Add both grids to the horizontal layout
        self.hbox.addLayout(self.ten_key_grid_layout)
        self.hbox.addLayout(self.function_button_grid_layout)
        
        self.vbox.addLayout(self.utility_button_grid_layout)
        self.vbox.addLayout(self.hbox)
        
        self.setLayout(self.vbox)

    # ------Create Functions---------    
    def setup_function_buttons(self, button_style):        
        
        function_buttons = [
            ('/', 0, 0), ('(', 0, 1), 
            ('*', 1, 0), (')', 1, 1),
            ('+', 2, 0), ('FUNC', 2, 1), 
            ('-', 3, 0), ('Return', 3, 1)
        ]        
        for (text, row, col) in function_buttons:            
            button = QPushButton(text)
            button.setStyleSheet(button_style)
            button.setFont(QFont('Arial', 14))            
            self.function_button_grid_layout.addWidget(button, row, col)
            #button.clicked.connect(self.create_handler(text))
            #button.clicked.connect(self.handle_button_clicked)        
            
    def setup_utility_buttons(self, button_style):        
        def back_button(r,c):
            # Adding backspace button separately to set icon        
            back_button_icon = QIcon.fromTheme("back")        
            back_button = QPushButton()
            back_button.setIcon(back_button_icon)
            back_button.setIconSize(QSize(23, 23))
            back_button.setStyleSheet(button_style)
            self.utility_button_grid_layout.addWidget(back_button, r, c)
            #back_button.clicked.connect(self.create_handler('←'))
            #back_button.clicked.connect(self.handle_button_clicked)
                    
        utility_buttons = [
            ('Undo', 0, 0), ('Redo', 0, 1), ('Clear', 0, 2)
        ]        
        back_button(0,3)
        self.utility_button_grid_layout.addWidget(self.combo_box, 0, 4)
        
        for (text, row, col) in utility_buttons:            
            button = QPushButton(text)
            button.setStyleSheet(button_style)
            button.setFont(QFont('Arial', 14))            
            self.utility_button_grid_layout.addWidget(button, row, col)
            #button.clicked.connect(self.create_handler(text))
            #button.clicked.connect(self.handle_button_clicked

    @pyqtSlot(str)
    def handleInputClicked(self, input):        
        input_mapping = CalculatorServices.input_mapping        
        input_action, param = input_mapping.get(self.ten_key.inputClicked, (None, None))
        self.current_input = input
        print(f"Input clicked: {input}")
    
    @pyqtSlot(str)
    def handleButtonClicked(self, text: str):        
        print(f"Ten Key Window Button clicked: {text}")
        self.send_ten_key_display(text)        
        self.query_digit_display()
        self.label.setText(f"You clicked: {text} and service state is {self.query_digit_display()}")
        self.state = self.compute(self.current_input, self.state)
        
        print(f"Ten Key Window state: {self.state}")
        
    def query_digit_display(self) -> str:
        return self.get_digit_display()

class FourFunctionCalculator_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Four Function Calculator")
        self.setGeometry(100, 100, 500, 200) 
        self.FourFunctionCalculator = FourFunctionCalculator()
        self.setCentralWidget(self.FourFunctionCalculator)

# Standalone example entry point
if __name__ == "__main__":
    app = QApplication([])
    calculator_window = FourFunctionCalculator_Window()
    calculator_window.show()
    app.exec()
