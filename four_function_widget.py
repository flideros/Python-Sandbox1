# ================================================
# UI for Four Function Calculator
# ================================================
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QPushButton,
                             QLabel, QWidget, QStyle, QFrame, QSizePolicy,
                             QComboBox, QStyledItemDelegate)
from PyQt6.QtGui import QFont, QIcon, QMouseEvent
from PyQt6.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from calculator_services import CalculatorServices
from compute_services import ComputeServices
from calculator_implementation import create_calculate
from compute_implementation import create_compute
from ten_key_widget import TenKey
from mathquill_widget import MathQuillStackWidget
from enum import Enum

class FourFunctionCalculator(QWidget):
    resetSignal = pyqtSignal()
    
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
        
        # Dictionary to store buttons with (row, column) as key
        self.buttons = {}
  
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
        BUTTON_COLOR = "#d8e0d8"
  
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
                background-color: {BUTTON_COLOR};
                border: 1px solid #656565;
                border-radius: 5px;
                padding: 5 10px;
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
                selection-color: black; 
            }}
            QComboBox QAbstractItemView::item:selected {{
                color: black; 
            }}
            QComboBox QAbstractItemView::item:hover {{
                color: black; 
                background-color: lightgray; 
            }}
        """
        # Main layout
        self.vbox = QVBoxLayout()
        
        # Development Label
        self.label = QLabel('This is a label', self)
        self.vbox.addWidget(self.label)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Math Quill widget for math output and input
        self.mathquill_stack_widget = MathQuillStackWidget(self)
        # self.mathquill_stack_widget.set_controls_visibility(True)
        self.vbox.addWidget(self.mathquill_stack_widget)
        
        self.mathquill_stack_widget.widgetClicked.connect(self.update_label)
        
        # Create Choice combo box
        self.combo_box = QComboBox()
        self.combo_box.addItem("Select")
        self.combo_box.addItems(["Sqrt", "Power"])
        self.combo_box.currentTextChanged.connect(self.update_button_text)
        self.combo_box.setStyleSheet(combo_box_style)
        
        # Create the horizontal layout to hold the ten key and additional grid
        self.hbox = QHBoxLayout()
        
        # 10-key Widget
        self.ten_key = TenKey('digits_mr_decimal')#,BUTTON_COLOR) # set the 10-key button color or use default
        self.resetSignal.connect(self.ten_key.reset_input)
        self.ten_key.button_color = BUTTON_COLOR
        self.ten_key.buttonClicked.connect(self.handleTenKeyButtonClicked)
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
            if text == 'FUNC':
                button.setEnabled(False) # Initially disabled
                button.setToolTip("Select a function first")
            self.function_button_grid_layout.addWidget(button, row, col)
            button.clicked.connect(self.create_handler(text))
            self.buttons[(row, col)] = button
            
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

    def update_button_text(self, text):
        if text != "Select":
            button = self.buttons[(2, 1)]
            self.buttons[(2, 1)].setText(text)
            self.buttons[(2, 1)].setEnabled(True) # Enable the button when a function is selected
            self.buttons[(2, 1)].setToolTip("") # Remove the tooltip when active
            self.combo_box.setCurrentIndex(0) # Reset the combo box to display "Select"

    # Function to bind handler to an action
    def create_handler(self, text):
        def handler():
            self.handleInputClicked(text)
        return handler

    def emitResetSignal(self): # 10-Key subscribes to this signal to clear the digit accumulator
        self.resetSignal.emit() 

    @pyqtSlot(str)
    def handleInputClicked(self, input_text):        
        input_mapping = ComputeServices.input_mapping        
        input_action, param = input_mapping.get(input_text, (None, None))
        
        if callable(input_action) and param is not None:
            input_action = input_action(param)
        
        if input_action is not None:             
            self.state = self.compute(input_action, self.state)
        
        self.current_input = input_text
        
        handle_return_input = self.services.handle_return(self.state)
        
        if handle_return_input == True and input_text == 'Return':
            self.resetSignal.emit() # Emit the reset signal
            self.mathquill_stack_widget.add_mathquill_widget()                        
            
        output_text, result = self.services.get_display_from_state("Error:")(self.state)
        # Update mathquill output for non-digit input
        if input_text in ['-','+','/','*','(',')']:
            # Emit the reset signal
            self.resetSignal.emit()             
            # Update mathquil expression
            self.mathquill_stack_widget.latex_input.setText(output_text)
            self.mathquill_stack_widget.update_last_widget()
        # Update mathquil result for non-digit input
        if result is not None:
            self.mathquill_stack_widget.result_input.setText(result)
            self.mathquill_stack_widget.update_result()
    
    @pyqtSlot(str)
    def handleTenKeyButtonClicked(self, text: str):
        self.send_ten_key_display(text)        
        self.query_digit_display()
        self.label.setText(f"You clicked: {text} and service state is {self.query_digit_display()}")
        
        self.state = self.compute(self.current_input, self.state)
        
        # Get latex from servies and state.         
        output_text, result = self.services.get_display_from_state("Error:")(self.state)
        self.mathquill_stack_widget.latex_input.setText(output_text)
        self.mathquill_stack_widget.update_last_widget()
        
        # Update mathquil result for digit input
        if result is not None:
            self.mathquill_stack_widget.result_input.setText(result)
            self.mathquill_stack_widget.update_result()        
                        
    def query_digit_display(self) -> str:
        return self.get_digit_display()
    
    def update_label(self, widget_id):
        self.label.setText(f"Clicked Widget ID: {widget_id}")

class FourFunctionCalculator_Window(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Four Function Calculator")
        self.setGeometry(100, 100, 800, 600) 
        self.FourFunctionCalculator = FourFunctionCalculator()
        self.setCentralWidget(self.FourFunctionCalculator)

# Standalone example entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator_window = FourFunctionCalculator_Window()
    calculator_window.show()
    app.exec()
