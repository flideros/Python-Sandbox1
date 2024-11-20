import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QDir

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        print(f'Console message: {message} (line {line} in {source})')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathQuill in PyQt6")
        self.setGeometry(100, 100, 800, 600)

        # Create a web view and set the custom page
        self.web_view = QWebEngineView(self)
        self.web_page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(self.web_page)
        self.setCentralWidget(self.web_view)

        # Load the HTML template using QUrl
        html_file_path = QDir.current().absoluteFilePath("/home/frank/Documents/Code/mathquill.html")  # Adjust the path
        print(f"Loading HTML file from: {html_file_path}")
        self.web_view.load(QUrl.fromLocalFile(html_file_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
