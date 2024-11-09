# ================================================
# UI for Calculator
# ================================================
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout, QPushButton, QLabel, QWidget, QStyle
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize
from calculator_services import CalculatorServices
from calculator_implementation import create_calculate  

class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        # Set up services
        services = CalculatorServices.create_services()
        self.calculate = create_calculate(services) 
        self.accumulate_non_zero_digit = services["accumulate_non_zero_digit"]
        self.accumulate_zero = services["accumulate_zero"]
        self.accumulate_separator = services["accumulate_separator"]
        self.do_math_operation = services["do_math_operation"]
        self.get_number_from_accumulator = services["get_number_from_accumulator"]
        self.get_display_from_state = services["get_display_from_state"]
        self.get_pending_op_from_state = services["get_pending_op_from_state"]
        self.get_memo_from_state = services["get_memo_from_state"]

        # Initial state
        self.state = CalculatorServices.initial_state
        QIcon.setThemeName("Papirus")

        print("==============")
        print("Initial state:", self.state)
        print("get_display_from_state:", self.get_display_from_state)
        print("get_pending_op_from_state:", self.get_pending_op_from_state)
        print("get_memo_from_state:", self.get_memo_from_state)
        print("==============")

        # ------Create Constants and Widgets---------
        # Constants for Styles
        grid_color = "#F5F5DC" 
        button_color = "#ebebeb"  
        button_hover_color = "#d2d2d2"
        background_color = "#F6F7F9"  
        operation_button_color = "#b0b0b0" 
        operation_button_border_color = "#656565" 
        operation_hover_background_color = "#c8c8c8" 
        operation_button_font = QFont('Arial', 16, QFont.Weight.Bold)
        BUTTON_PADDING = "5px"
        BUTTON_FONT_SIZE = "14pt"
        BORDER_RADIUS = "5px"
        BORDER_COLOR = "#656565"
        HOVER_COLOR = "#c8c8c8"        

        # Style Sheets
        # Common Button Style
        button_style_base = f"""
            background-color: {button_color};
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
                background-color: {button_hover_color};
                border: 1px solid {button_hover_color};
            }}
        """
        # Style for Operation Buttons
        operation_button_style = f"""
            QPushButton {{
                {button_style_base}
                background-color: {operation_button_color};
                font-family: '{operation_button_font.family()}';
                font-size: {operation_button_font.pointSize()}pt;
                font-weight: {operation_button_font.weight()};
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};
                border: 1px solid {operation_button_border_color};
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
        self.grid.addWidget(self.result, 0, 0, 1, 5)

        self.memo = QLabel("")
        self.memo.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.memo.setStyleSheet(f"background-color: {background_color}; font-size: 17px;")
        self.grid.addWidget(self.memo, 0, 5, 1, 1)

        self.helper = QLabel("")
        self.helper.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.helper.setStyleSheet(f"background-color: {background_color};")
        self.grid.addWidget(self.helper, 1, 0, 1, 6)
                        
        # Call to setup buttons
        self.setup_buttons(button_style, operation_button_style)
        
    # ------Create Functions---------    
    def setup_buttons(self, button_style, operation_button_style):
        # Buttons
        buttons = [
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('0', 5, 1), ('.', 5, 2),
            ('+', 4, 3), ('-', 3, 3), ('*', 2, 3), ('/', 1, 3), ('=', 5, 3),
            ('√', 1, 4), ('±', 2, 4), ('1/x', 3, 4), ('%', 4, 4),
            ('C', 1, 1), ('CE', 1, 0), ('MC', 5, 0), ('MR', 5, 5),
            ('MS', 4, 5), ('M+', 3, 5), ('M-', 2, 5)
        ]
        
        # Identify operation buttons for style application.
        operation_buttons = ['+', '-', '*', '/']
        
        # Adding backspace button separately to set icon        
        back_button_icon = QIcon.fromTheme("back")        
        back_button = QPushButton()
        back_button.setIcon(back_button_icon)
        back_button.setIconSize(QSize(23, 23))
        back_button.setStyleSheet(button_style)
        self.grid.addWidget(back_button, 1, 2)
        back_button.clicked.connect(self.create_handler('←'))
        
        # Adding python icon to empty grid space
        python_icon = QIcon.fromTheme("accessories-calculator")
        python_button = QPushButton() # Placing the icon in a QPushButton since it has .setIcon()
        python_button.setIcon(python_icon)
        python_button.setIconSize(QSize(23, 23))
        python_button.setStyleSheet(f"background-color: transparent; border: none; padding: 0;") # Hide the button
        self.grid.addWidget(python_button, 5, 4)
        
        for (text, row, col) in buttons:            
            button = QPushButton(text)
            if text in operation_buttons:
                button.setStyleSheet(operation_button_style)
            else:  
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
        input_mapping = CalculatorServices.input_mapping        
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
        self.helper.setText(self.get_pending_op_from_state(self.state))
        self.memo.setText(self.get_memo_from_state(self.state))

class CalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setGeometry(100, 100, 400, 200)
        self.calculator = Calculator()
        self.setCentralWidget(self.calculator)

# Standalone example entry point
if __name__ == "__main__":
    app = QApplication([])
    calculator_window = CalculatorWindow()
    calculator_window.show()
    app.exec()
