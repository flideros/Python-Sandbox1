# ================================================
# UI for Four Function Calculator
# ================================================
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout, QPushButton, QLabel, QWidget, QStyle, QFrame
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

        self.ten_key = TenKey('digits_mr_decimal')
        self.ten_key.buttonClicked.connect(self.handleButtonClicked)
        self.ten_key.inputClicked.connect(lambda x: self.handleInputClicked(x))
        self.ten_key.result.hide()
        
        services = ComputeServices()
        self.services = services
        self.state = self.services.initial_state
        self.compute = create_compute(services)
        self.current_input = None
                
        self.send_ten_key_display = self.services.receive_ten_key_display
        self.get_digit_display = self.services.get_digit_display
               
        self.vbox = QVBoxLayout()
        self.label = QLabel('This is a label', self)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.ten_key)
        
        self.setLayout(self.vbox)

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
        
        self.setWindowTitle("Ten Key Input and Display")
        self.setGeometry(100, 100, 400, 200) 
        self.FourFunctionCalculator = FourFunctionCalculator()
        self.setCentralWidget(self.FourFunctionCalculator)

# Standalone example entry point
if __name__ == "__main__":
    app = QApplication([])
    calculator_window = FourFunctionCalculator_Window()
    calculator_window.show()
    app.exec()
