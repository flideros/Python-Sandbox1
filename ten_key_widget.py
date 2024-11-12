# ================================================
# UI for Ten Key Input and Display
# ================================================
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout, QPushButton, QLabel, QWidget, QStyle
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize
from calculator_services import CalculatorServices
from calculator_implementation import create_calculate
from enum import Enum

class TenKeyConfig(Enum):
   DEFAULT = 'default' # 10 digits, back, clear entry, decimal
   DIGITS_ONLY = 'digits_only' # 10 digits
   DIGITS_CE_BACK = 'digits_ce_back' # 10 digits, back, clear entry
   DIGITS_CE_DECIMAL = 'digits_ce_decimal' # 10 digits, clear entry, decimal
   
   
class TenKey(QWidget):
    def __init__(self, config='default'):
        super().__init__()
        
        # Set the Ten Key configuration
        self.config = TenKeyConfig(config)
        
        # Set up services
        services = CalculatorServices.create_services()
        self.calculate = create_calculate(services) 
        self.accumulate_non_zero_digit = services["accumulate_non_zero_digit"]
        self.accumulate_zero = services["accumulate_zero"]
        self.accumulate_separator = services["accumulate_separator"]
        self.get_number_from_accumulator = services["get_number_from_accumulator"]
        self.get_display_from_state = services["get_display_from_state"]
        self.get_pending_op_from_state = services["get_pending_op_from_state"]
        self.get_memo_from_state = services["get_memo_from_state"]

        # Initial state
        self.state = CalculatorServices.initial_state
        QIcon.setThemeName("Papirus")

        print("==============")
        print("Initial state:", self.state)
        print("==============")

        # ------Create Constants and Widgets---------
        # Constants for Styles
        grid_color = "#F5F5DC"         
        background_color = "#F6F7F9"          
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
        
        # Main Layout
        main_layout = QVBoxLayout()        
        self.grid = QGridLayout()
        self.grid.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(self.grid)
        
        # Set the main layout to the widget
        self.setLayout(main_layout)

        # Text Blocks
        self.result = QLabel("0")
        self.result.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.result.setStyleSheet(f"background-color: {background_color}; font-size: 27px;")
        self.grid.addWidget(self.result, 0, 0, 1, 3)
                        
        # Call to setup buttons
        self.setup_buttons(button_style)
        
    # ------Create Functions---------    
    def setup_buttons(self, button_style):
        # Buttons
        def back_button(r,c):
            # Adding backspace button separately to set icon        
            back_button_icon = QIcon.fromTheme("back")        
            back_button = QPushButton()
            back_button.setIcon(back_button_icon)
            back_button.setIconSize(QSize(23, 23))
            back_button.setStyleSheet(button_style)
            self.grid.addWidget(back_button, r, c)
            back_button.clicked.connect(self.create_handler('←'))
        
        def python_icon():
            # Adding python icon to empty grid space
            python_icon = QIcon.fromTheme("python")
            python_button = QPushButton() # Placing the icon in a QPushButton since it has .setIcon()
            python_button.setIcon(python_icon)
            python_button.setIconSize(QSize(23, 23))
            python_button.setStyleSheet(f"background-color: transparent; border: none; padding: 0;") # Hide the button
            self.grid.addWidget(python_button, 1, 2)
        
        if self.config == TenKeyConfig.DEFAULT:
            buttons = [
                ('1', 4, 0), ('2', 4, 1), ('3', 4, 2),
                ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
                ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
                ('CE', 5, 0),('0', 5, 1), ('.', 5, 2)
            ]
            back_button(1,0)
            python_icon()
            
        elif self.config == TenKeyConfig.DIGITS_ONLY:
            buttons = [
                ('1', 4, 0), ('2', 4, 1), ('3', 4, 2),
                ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
                ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
                ('0', 5, 1)
            ]        

        elif self.config == TenKeyConfig.DIGITS_CE_DECIMAL:
            buttons = [
                ('1', 4, 0), ('2', 4, 1), ('3', 4, 2),
                ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
                ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
                ('0', 5, 1), ('CE', 5, 0), ('.', 5, 2)
            ]
        
        elif self.config == TenKeyConfig.DIGITS_CE_BACK:
            buttons = [
                ('1', 4, 0), ('2', 4, 1), ('3', 4, 2),
                ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
                ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
                ('0', 5, 1), ('CE', 5, 0)
            ]
            back_button(5,2)
            
        for (text, row, col) in buttons:            
            button = QPushButton(text)
            button.setStyleSheet(button_style)
            button.setFont(QFont('Arial', 14))
            self.grid.addWidget(button, row, col)
            button.clicked.connect(self.create_handler(text))
    
    # Function to bind handler to an action
    def create_handler(self, text):
        def handler():
            self.handle_input(text)
        return handler

    # Function to route action to a handler
    def handle_input(self, input_text):
        input_mapping = CalculatorServices.ten_key_input_mapping        
        input_action, param = input_mapping.get(input_text, (None, None))
        
        if callable(input_action) and param is not None:
            input_action = input_action(param)
        
        print("Input action:", input_action)        
        print("Current state:", self.state)
        
        if input_action is not None:            
            self.state = self.calculate(input_action, self.state)
            
        self.update_display()

    # Function to display current state
    def update_display(self):
        print("==============")
        print("Output State:", self.state)
        print("Display Text:", self.get_display_from_state(self.state))
        print("Pending Op Text:", self.get_pending_op_from_state(self.state))
        print("Memo Text:", self.get_memo_from_state(self.state))
        print("==============")
        self.result.setText(self.get_display_from_state(self.state))
        
    def keyPressEvent(self, event):
        key = event.key()
        if self.config == TenKeyConfig.DEFAULT:
            key_mapping = {
                Qt.Key.Key_0: '0', Qt.Key.Key_1: '1', Qt.Key.Key_2: '2', Qt.Key.Key_3: '3',
                Qt.Key.Key_4: '4', Qt.Key.Key_5: '5', Qt.Key.Key_6: '6', Qt.Key.Key_7: '7',
                Qt.Key.Key_8: '8', Qt.Key.Key_9: '9', Qt.Key.Key_Period: '.', Qt.Key.Key_Backspace: '←',
                Qt.Key.Key_Delete: 'CE'
            }
        elif self.config == TenKeyConfig.DIGITS_ONLY:
            key_mapping = {
                Qt.Key.Key_0: '0', Qt.Key.Key_1: '1', Qt.Key.Key_2: '2', Qt.Key.Key_3: '3',
                Qt.Key.Key_4: '4', Qt.Key.Key_5: '5', Qt.Key.Key_6: '6', Qt.Key.Key_7: '7',
                Qt.Key.Key_8: '8', Qt.Key.Key_9: '9'
            }
        elif self.config == TenKeyConfig.DIGITS_CE_DECIMAL:
            key_mapping = {
                Qt.Key.Key_0: '0', Qt.Key.Key_1: '1', Qt.Key.Key_2: '2', Qt.Key.Key_3: '3',
                Qt.Key.Key_4: '4', Qt.Key.Key_5: '5', Qt.Key.Key_6: '6', Qt.Key.Key_7: '7',
                Qt.Key.Key_8: '8', Qt.Key.Key_9: '9', Qt.Key.Key_Delete: 'CE', Qt.Key.Key_Period: '.'
            }
        elif self.config == TenKeyConfig.DIGITS_CE_BACK:
            key_mapping = {
                Qt.Key.Key_0: '0', Qt.Key.Key_1: '1', Qt.Key.Key_2: '2', Qt.Key.Key_3: '3',
                Qt.Key.Key_4: '4', Qt.Key.Key_5: '5', Qt.Key.Key_6: '6', Qt.Key.Key_7: '7',
                Qt.Key.Key_8: '8', Qt.Key.Key_9: '9', Qt.Key.Key_Delete: 'CE', Qt.Key.Key_Backspace: '←'
            }
        if key in key_mapping:
            self.handle_input(key_mapping[key])

class TenKeyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ten Key Input and Display")
        self.setGeometry(100, 100, 400, 200)
        self.ten_key = TenKey('default')
        self.setCentralWidget(self.ten_key)

# Standalone example entry point
if __name__ == "__main__":
    app = QApplication([])
    calculator_window = TenKeyWindow()
    calculator_window.show()
    app.exec()
