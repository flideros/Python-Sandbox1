import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy, QSpacerItem
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QDir, pyqtSlot, pyqtSignal, QObject, Qt, QEvent

class MathJaxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MathJax Pop-Out Window')
        self.setGeometry(500, 300, 500, 300) 
        
        self.web_view = QWebEngineView(self)
        self.web_page = CustomWebEnginePage(self)
        self.web_view.setPage(self.web_page)
        
        html_file_path = QDir.current().absoluteFilePath("mathjax_pop-out.html")
        self.web_view.load(QUrl.fromLocalFile(html_file_path))
        
        self.setCentralWidget(self.web_view)
        
        # Setup QWebChannel
        self.bridge = self
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().loadFinished.connect(self.inject_script)
    
        self.latex_content = ""
        
    def load_mathjax_content(self, latex_content):
        # load latex content to self                
        self.latex_content = latex_content        

    def inject_script(self):
        latex_content = self.latex_content
        script = f"""
        document.getElementById('math-content').innerHTML = '$$' + `{latex_content}` + '$$';
        MathJax.typesetPromise([document.getElementById('math-content')]);
        """
        self.web_view.page().runJavaScript(script)

'''
Bridge Class: This class allows the Python side to receive updates from the
JavaScript side and vice versa. For example, it enables updating the LaTeX output
in the main application when changes occur in the MathQuill input field.
'''
class Bridge(QObject):
    clicked = pyqtSignal() # Signal to emit when the web view is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

    @pyqtSlot(str)
    def print_message(self, message):
        print(f"Received message from JS: {message}")
    
    @pyqtSlot(str)
    def latexUpdated(self, latex):
        self.parent().update_latex_output(latex)

    @pyqtSlot(str)
    def updateResult(self, result):
        self.parent().update_result_content(result)
        
    @pyqtSlot()
    def clickedSignal(self):
        self.clicked.emit()
        
    @pyqtSlot()
    def openMathJaxWindow(self):
        self.main_window.open_mathjax_window()
        
'''
CustomWebEnginePage Class: This custom class primarily helps to manage communication
and handle JavaScript console messages. It ensures that any messages or errors from the
JavaScript side can be debugged and traced in the Python console.
'''
class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = Bridge(parent)

    def javaScriptConsoleMessage(self, level, message, line, source):
        pass #print(f'Console message: {message} (line {line} in {source})')

class MathQuillWidget(QWidget):
    latexChanged = pyqtSlot(str)
    clicked = pyqtSignal(int) # Signal to be emitted when the widget is clicked
    
    def __init__(self, widget_id, parent=None):
        super().__init__(parent)        
        self.widget_id = widget_id
        self.parent_window = parent  # Reference to the main window
        self.id_label = QLabel(f"MathQuill Widget {widget_id}")
        self.result_latex = ''
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        layout.setSpacing(5)  # Adjust spacing as needed, e.g., 5 pixels

        self.web_view = QWebEngineView(self)
        
        self.web_page = CustomWebEnginePage(self)
        self.web_view.setPage(self.web_page)
        # Set size policy to expanding for both directions
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.web_view.setFixedHeight(65)  # Initial and minimum height
        self.web_view.setMinimumHeight(65)  # Set minimum height to 50 pixels

        layout.addWidget(self.web_view, 0, Qt.AlignmentFlag.AlignBottom)
        
        # Install an event filter on the web view to capture mouse events
        self.web_view.installEventFilter(self)

        self.frame = QFrame(self)
        self.frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)  # Set frame layout margins to 0
        self.frame_layout.setSpacing(0)  # Adjust spacing within frame
        self.frame.setVisible(False)  # Hide frame by default

        self.latex_label = QLabel("LaTeX Output: ")
        self.latex_label.setFixedHeight(20)  # Fixing the height for a single line of text
        self.latex_label.setVisible(False)  # Hide label by default
        self.frame_layout.addWidget(self.latex_label)

        self.parsed_label = QLabel("Parsed LaTeX: ")
        self.parsed_label.setFixedHeight(20)  # Fixing the height for a single line of text
        self.parsed_label.setVisible(False)  # Hide label by default
        self.frame_layout.addWidget(self.parsed_label)
        self.frame_layout.addWidget(self.id_label)
        
        layout.addWidget(self.frame)       

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        html_file_path = QDir.current().absoluteFilePath("mathquill_template2.html")
        self.web_view.load(QUrl.fromLocalFile(html_file_path))

        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.web_page.bridge)
        self.web_page.setWebChannel(self.channel)
        
        # Connect the clicked signal from the bridge to the widget's clicked signal
        self.web_page.bridge.clicked.connect(self.handle_click)
    
    def set_cursor_position(self,stack_count): 
        # Execute JavaScript to set cursor position in MathQuill
        self.web_view.page().runJavaScript("window.mathField.focus(); window.mathField.__controller.cursor.insAtRightEnd(window.mathField.__controller.root);")        
        count = 0
        while count < stack_count:
            self.set_cursor_position_left()
            count+=1
        
    def set_cursor_position_left(self): 
        # Execute JavaScript to set cursor position in MathQuill        
        self.web_view.page().runJavaScript("window.focusAndMoveLeft();")
    
    def handle_click(self): self.clicked.emit(self.widget_id)
    
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

    def toggle_frame(self, visible=None):
        if visible is None:
            visible = not self.frame.isVisible()
        self.frame.setVisible(visible)
        self.latex_label.setVisible(visible)
        self.parsed_label.setVisible(visible)

    def adjust_web_view_height(self, height):
        self.web_view.setFixedHeight((height, 65))  # Ensure the height doesn't go below 50 pixels

    @pyqtSlot(str)
    def update_result_content(self, result):
        self.result_latex = result
        script = f"""
        document.getElementById('result-value').innerHTML ='$$' + `{result}` + '$$';
        MathJax.typesetPromise([document.getElementById('result-value')]);
        """
        self.web_view.page().runJavaScript(script)
    
    def open_mathjax_window(self):
       latex_content = self.result_latex       
       self.mathjax_window = MathJaxWindow()
       self.mathjax_window.show()
       self.mathjax_window.load_mathjax_content(latex_content)       

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QScrollArea, QLabel, QSizePolicy, QSpacerItem
from PyQt6.QtCore import Qt, QTimer

class CustomScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        
    def wheelEvent(self, event):
        visible_height = self.viewport().height()
        widget_height = 65
        num_visible_widgets = visible_height // widget_height

        if self.widget().layout().count() > num_visible_widgets + 2: 
            super().wheelEvent(event)
        else:
            event.ignore()

class MathQuillStackWidget(QWidget):
    latexUpdated = pyqtSignal(str)
    resultUpdated = pyqtSignal(str)
    widgetClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MathQuillStack in PyQt6")
        self.setGeometry(100, 100, 800, 600)
        
        self.control_visibility = False  # Control visibility variable

        self.layout = QVBoxLayout(self)

        self.latex_input = QLineEdit()
        self.latex_input.setPlaceholderText("Enter LaTeX here...")
        self.layout.addWidget(self.latex_input)

        self.result_input = QLineEdit()
        self.result_input.setPlaceholderText("Enter result here...")
        self.layout.addWidget(self.result_input)

        self.scroll_area = CustomScrollArea()        
        self.scroll_area.setObjectName('scroll_area')
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        
        self.scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 8px; /* Reduced width */
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(173, 216, 230, 0.5);  /* Light blue with 50% opacity */
                min-height: 20px;
                border-radius: 4px; /* Slightly smaller radius */
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(135, 206, 235, 0.5);  /* Slightly darker light blue with 50% opacity on hover */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f1f1f1;
                height: 8px; /* Reduced height */
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: rgba(173, 216, 230, 0.5);  /* Light blue with 50% opacity */
                min-width: 20px;
                border-radius: 4px; /* Slightly smaller radius */
            }
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(135, 206, 235, 0.5);  /* Slightly darker light blue with 50% opacity on hover */
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)
        
        self.widgets_dict = {} # Dictionary to keep track of widgets

        self.update_widget_button = QPushButton("Update Last MathQuill Widget")
        self.update_widget_button.clicked.connect(self.update_last_widget)
        self.layout.addWidget(self.update_widget_button)

        self.update_result_button = QPushButton("Update Result of Last MathQuill Widget")
        self.update_result_button.clicked.connect(self.update_result)
        self.layout.addWidget(self.update_result_button)

        self.toggle_frame_button = QPushButton("Toggle Frame Visibility")
        self.toggle_frame_button.clicked.connect(self.toggle_last_widget_frame)
        self.layout.addWidget(self.toggle_frame_button)

        self.add_widget_button = QPushButton("Add MathQuill Widget")
        self.add_widget_button.clicked.connect(self.add_mathquill_widget)
        self.layout.addWidget(self.add_widget_button)

        # Set visibility based on control_visibility
        self.set_controls_visibility(self.control_visibility)
        
        # Get screen height and set minimum height for the layout
        screen_height = QApplication.primaryScreen().size().height()
        self.scroll_area_widget.setMinimumHeight(screen_height)

        # Add a taller, stretchable label to push the first widget to the bottom
        self.stretch_label = QLabel("")
        self.stretch_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stretch_label.setMinimumHeight(400)  # Ensure the label is tall enough to push down the widget
        self.scroll_area_layout.addWidget(self.stretch_label)

        # Add a stretchable space to push the widgets to the bottom
        self.scroll_area_layout.addStretch(1)

        self.add_mathquill_widget()

    def set_controls_visibility(self, visible):
        """Set the visibility of inputs and buttons."""
        self.latex_input.setVisible(visible)
        self.result_input.setVisible(visible)
        self.update_widget_button.setVisible(visible)
        self.update_result_button.setVisible(visible)
        self.toggle_frame_button.setVisible(visible)
        self.add_widget_button.setVisible(visible)

    def add_mathquill_widget(self):
        widget_id = self.scroll_area_layout.count()
        widget = MathQuillWidget(widget_id)
        widget.clicked.connect(self.handle_widget_click)
        self.scroll_area_layout.insertWidget(self.scroll_area_layout.count(), widget)  # Insert above the stretch label
        self.widgets_dict[widget_id] = widget.widget_id # Add widget to dictionary
        QTimer.singleShot(100, self.scroll_to_bottom)  # Ensure the scrollbar updates correctly

    def handle_widget_click(self, widget_id):
        self.widgetClicked.emit(widget_id)
    
    def update_last_widget(self,stack_count):
        if self.scroll_area_layout.count() > 1:
            widget = self.scroll_area_layout.itemAt(self.scroll_area_layout.count() - 1).widget()
            latex = self.latex_input.text()
            widget.set_latex(latex)
            widget.set_cursor_position(stack_count)

    def update_result(self):
        if self.scroll_area_layout.count() > 1:
            widget = self.scroll_area_layout.itemAt(self.scroll_area_layout.count() - 1).widget()
            result = self.result_input.text()
            widget.update_result_content(result)

    def toggle_last_widget_frame(self):
        if self.scroll_area_layout.count() > 1:
            widget = self.scroll_area_layout.itemAt(self.scroll_area_layout.count() - 1).widget()
            widget.toggle_frame(not widget.frame.isVisible())

    def update_main_text_input(self, latex):
        self.latex_input.setText(latex)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(100, self.scroll_to_bottom) # Ensure the scrollbar updates correctly
    
    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
      
class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application Window")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
              
        self.mathquill_stack_widget = MathQuillStackWidget(self)
        self.mathquill_stack_widget.set_controls_visibility(True)
        layout.addWidget(self.mathquill_stack_widget)
        
        self.clicked_label = QLabel("Clicked Widget ID: None")
        layout.addWidget(self.clicked_label)

        # Optionally connect signals and slots if needed
        self.mathquill_stack_widget.latexUpdated.connect(self.handle_latex_update)
        self.mathquill_stack_widget.resultUpdated.connect(self.handle_result_update)
        self.mathquill_stack_widget.widgetClicked.connect(self.update_label)

    def update_label(self, widget_id):
        self.clicked_label.setText(f"Clicked Widget ID: {widget_id}")
    
    def handle_latex_update(self, latex):
        print("LaTeX Updated:", latex)

    def handle_result_update(self, result):
        print("Result Updated:", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainAppWindow()
    window.show()
    sys.exit(app.exec())
