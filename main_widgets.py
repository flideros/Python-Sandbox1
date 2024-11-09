from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt  

class ButtonLabelWidget(QWidget):
    def __init__(self, label_text, button_text, button_callback):
        super().__init__()

        # Create layout
        layout = QHBoxLayout()
        layout.setSpacing(10)  # Add spacing between label and button
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins if any

        # Define fixed height for consistency
        fixed_height = 40  # Adjust this value as needed for your design

        # Add label and set its size policy to ensure proper alignment
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.label.setFixedHeight(fixed_height)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignRight)

        # Add button
        self.button = QPushButton(button_text)
        self.button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.button.setFixedHeight(fixed_height)
        self.button.clicked.connect(button_callback)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)
