import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class MathRenderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Math Render App with MathJax')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.textEdit = QTextEdit(self)
        self.textEdit.setPlaceholderText('Type your math expression here...')
        self.textEdit.textChanged.connect(self.update_math)

        self.webView = QWebEngineView(self)
        self.webView.setMinimumHeight(400)  # Set a minimum height for the output box
        self.webView.setHtml(self.generate_html(''))

        self.layout.addWidget(self.textEdit)
        self.layout.addWidget(self.webView)

        self.setLayout(self.layout)

    def update_math(self):
        input_text = self.textEdit.toPlainText()
        rendered_html = self.generate_html(input_text)
        self.webView.setHtml(rendered_html)

    def generate_html(self, math_text):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" async
              src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js">
            </script>
        </head>
        <body>
            <p>$$ {math_text} $$</p>
        </body>
        </html>
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MathRenderApp()
    ex.show()
    sys.exit(app.exec())
