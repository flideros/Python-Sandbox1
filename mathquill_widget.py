import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy, QSpacerItem
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QDir, pyqtSlot, QObject, Qt

class Bridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(str)
    def latexUpdated(self, latex):
        self.parent().update_latex_output(latex)

    @pyqtSlot(int)
    def adjustHeight(self, height):
        self.parent().adjust_web_view_height(height)

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = Bridge(parent)

    def javaScriptConsoleMessage(self, level, message, line, source):
        print(f'Console message: {message} (line {line} in {source})')

class MathQuillWidget(QWidget):
    latexChanged = pyqtSlot(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Reference to the main window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        layout.setSpacing(5)  # Adjust spacing as needed, e.g., 5 pixels

        self.web_view = QWebEngineView(self)
        self.web_page = CustomWebEnginePage(self)
        self.web_view.setPage(self.web_page)
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.web_view.setFixedHeight(50)  # Initial and minimum height
        self.web_view.setMinimumHeight(50)  # Set minimum height to 50 pixels

        layout.addWidget(self.web_view, 0, Qt.AlignmentFlag.AlignBottom)

        self.frame = QFrame(self)
        self.frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)  # Set frame layout margins to 0
        self.frame_layout.setSpacing(5)  # Adjust spacing within frame

        self.latex_label = QLabel("LaTeX Output: ")
        self.latex_label.setFixedHeight(20)  # Fixing the height for a single line of text
        self.latex_label.setVisible(False)  # Hide label by default
        self.frame_layout.addWidget(self.latex_label)

        self.parsed_label = QLabel("Parsed LaTeX: ")
        self.parsed_label.setFixedHeight(20)  # Fixing the height for a single line of text
        self.parsed_label.setVisible(False)  # Hide label by default
        self.frame_layout.addWidget(self.parsed_label)

        layout.addWidget(self.frame)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        html_file_path = QDir.current().absoluteFilePath("mathquill_template.html")
        self.web_view.load(QUrl.fromLocalFile(html_file_path))

        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.web_page.bridge)
        self.web_page.setWebChannel(self.channel)

    def update_latex_output(self, latex):
        self.latex_label.setText(f"LaTeX Output: {latex}")
        self.parsed_label.setText(f"Parsed LaTeX: {self.parse_latex(latex)}")
        if self.parent_window:
            self.parent_window.update_main_text_input(latex)

    def parse_latex(self, latex):
        parsed_latex = latex.replace('\\frac', '/').replace('{', '').replace('}', '')
        return parsed_latex

    def set_latex(self, latex):
        script = f"window.updateMathQuill('{latex}');"
        self.web_view.page().runJavaScript(script)

    def get_latex_output(self):
        return self.latex_label.text()

    def get_parsed_latex(self):
        return self.parsed_label.text()

    def toggle_frame(self, visible):
        self.frame.setVisible(visible)
        self.latex_label.setVisible(visible)
        self.parsed_label.setVisible(visible)

    def adjust_web_view_height(self, height):
        self.web_view.setFixedHeight(max(height, 50))  # Ensure the height doesn't go below 50 pixels

'''


if __name__ == "__main__":
    app = QApplication(sys.argv)
    math_quill_widget = MathQuillWidget()
    math_quill_widget.show()
    sys.exit(app.exec())
'''

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QScrollArea, QLabel, QSizePolicy, QSpacerItem
from PyQt6.QtCore import Qt, QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathQuill in PyQt6")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.latex_input = QLineEdit()
        self.latex_input.setPlaceholderText("Enter LaTeX here...")
        self.layout.addWidget(self.latex_input)

        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_widget.setLayout(self.scroll_area_layout)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

        

        update_widget_button = QPushButton("Update Last MathQuill Widget")
        update_widget_button.clicked.connect(self.update_last_widget)
        self.layout.addWidget(update_widget_button)

        toggle_frame_button = QPushButton("Toggle Frame Visibility")
        toggle_frame_button.clicked.connect(self.toggle_last_widget_frame)
        self.layout.addWidget(toggle_frame_button)

        add_widget_button = QPushButton("Add MathQuill Widget")
        add_widget_button.clicked.connect(self.add_mathquill_widget)
        self.layout.addWidget(add_widget_button)

        # Add a taller, stretchable label to push the first widget to the bottom
        self.stretch_label = QLabel("")
        self.stretch_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stretch_label.setMinimumHeight(400)  # Ensure the label is tall enough to push down the widget
        self.scroll_area_layout.addWidget(self.stretch_label)
        
        self.add_mathquill_widget()

    def add_mathquill_widget(self):
        widget = MathQuillWidget(self)
        self.scroll_area_layout.insertWidget(self.scroll_area_layout.count(), widget)  # Insert above the stretch label
        QTimer.singleShot(100, self.scroll_to_bottom)  # Ensure the scrollbar updates correctly

    def update_last_widget(self):
        if self.scroll_area_layout.count() > 1:
            widget = self.scroll_area_layout.itemAt(self.scroll_area_layout.count() - 1).widget()
            latex = self.latex_input.text()
            widget.set_latex(latex)

    def toggle_last_widget_frame(self):
        if self.scroll_area_layout.count() > 1:
            widget = self.scroll_area_layout.itemAt(self.scroll_area_layout.count() - 1).widget()
            widget.toggle_frame(not widget.frame.isVisible())

    def update_main_text_input(self, latex):
        self.latex_input.setText(latex)

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
