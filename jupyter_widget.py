from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
import subprocess
import socket
import sys

class JupyterWidget(QWidget):
    def __init__(self, switch_to_main_callback=None, extra_param=None):
        super().__init__()

        self.browser = QWebEngineView()

        # Add a startup page
        self.browser.setHtml('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Welcome</title>
            </head>
            <body>
                <h1>Welcome to the Jupyter Notebook Interface</h1>
                <p>Checking Jupyter Server status...</p>
            </body>
            </html>
        ''')

        # Button to go back to main menu if callback provided
        if switch_to_main_callback:
            self.back_button = QPushButton('Back to Main Menu')
            self.back_button.clicked.connect(switch_to_main_callback)
        else:
            self.back_button = None

        # Create layout for the widget
        layout = QVBoxLayout()

        # Add back button if it exists
        if self.back_button:
            layout.addWidget(self.back_button)
        
        # Add the web view
        layout.addWidget(self.browser)

        # Extra param usage example, add only if not None or empty
        if extra_param:
            self.extra_label = QLabel(f"Extra Param: {extra_param}")
            layout.addWidget(self.extra_label)

        self.setLayout(layout)

        self.jupyter_process = None
        self.check_server_and_start()

    def check_server_and_start(self):
        if not self.is_server_running():
            self.start_jupyter()
        else:
            self.load_jupyter_lab()

    def is_server_running(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8888))
        return result == 0

    def start_jupyter(self):
        import subprocess
        self.jupyter_process = subprocess.Popen(['jupyter', 'lab', '--no-browser'])
        QTimer.singleShot(2000, self.load_jupyter_lab)  # Adjust delay as needed

    def load_jupyter_lab(self):
        self.browser.setUrl(QUrl("http://localhost:8888/lab"))

    def stop_jupyter(self):
        if self.jupyter_process:
            self.jupyter_process.terminate()
            self.jupyter_process = None

    def closeEvent(self, event):
        self.stop_jupyter()  # Ensure the server is stopped
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Jupyter Notebook in PyQt6')
        self.resize(1600, 900)

        # Create the QWebEngineView
        self.browser = QWebEngineView()
        
        # Add a startup page
        self.browser.setHtml('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Welcome</title>
            </head>
            <body>
                <h1>Welcome to the Jupyter Notebook Interface</h1>
                <p>Checking Jupyter Server status...</p>                
            </body>
            </html>
        ''')

        # Layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.jupyter_process = None
        self.check_server_and_start()

    def check_server_and_start(self):
        if not self.is_server_running():
            self.start_jupyter()
        else:
            self.load_jupyter_lab()

    def is_server_running(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8888))
        return result == 0

    def start_jupyter(self):
        self.jupyter_process = subprocess.Popen(['jupyter', 'lab', '--no-browser'])
        QTimer.singleShot(2000, self.load_jupyter_lab)  # Adjust delay as needed

    def load_jupyter_lab(self):
        self.browser.setUrl(QUrl("http://localhost:8888/lab"))

    def stop_jupyter(self):
        if self.jupyter_process:
            self.jupyter_process.terminate()
            self.jupyter_process = None

    def closeEvent(self, event):
        self.stop_jupyter()  # Ensure the server is stopped
        event.accept()   

# Standalone example entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
