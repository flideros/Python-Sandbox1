import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

class Backend(QObject):
    update_expression = pyqtSignal(str)

    @pyqtSlot(str)
    def receive_expression(self, expression):
        print(f"Received expression from frontend: {expression}")
        self.update_expression.emit(f"Updated expression: \\( {expression} \\)")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive MathJax in PyQt6")

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.web_view = QWebEngineView()

        self.channel = QWebChannel()
        self.backend = Backend()
        self.channel.registerObject("backend", self.backend)
        self.web_view.page().setWebChannel(self.channel)

        self.backend.update_expression.connect(self.update_mathjax_expression)

        self.web_view.setHtml(self.html_content())

        layout.addWidget(self.web_view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def html_content(self):
        return """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .output-box {
                        border: 1px solid #ccc;
                        padding: 10px;
                        margin: 10px;
                        font-family: Arial, sans-serif;
                    }
                    .math {
                        font-family: "Times New Roman", Times, serif;
                        color: #333;
                    }
                </style>
                <!-- Include MathJax 3.x -->
                <script>
                    window.MathJax = {
                        tex: {
                            inlineMath: [['$', '$'], ['\\(', '\\)']]
                        },
                        startup: {
                            typeset: false  // We will typeset manually
                        }
                    };
                </script>
                <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                <!-- Include QWebChannel -->
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <script type="text/javascript">
                    document.addEventListener("DOMContentLoaded", function() {
                        console.log('DOM fully loaded and parsed');
                        new QWebChannel(qt.webChannelTransport, function(channel) {
                            window.backend = channel.objects.backend;
                        });

                        window.sendExpression = function() {
                            console.log('sendExpression called');
                            var expression = document.getElementById("expression").value;
                            window.backend.receive_expression(expression);
                        }

                        window.updateExpression = function(expression) {
                            console.log('updateExpression called with: ' + expression);
                            var outputElement = document.getElementById("output");
                            outputElement.innerHTML = expression;
                            MathJax.typeset([outputElement]);
                        }
                    });
                </script>
            </head>
            <body>
                <div class="output-box">
                    <input id="expression" type="text" placeholder="Enter Math Expression"/>
                    <button onclick="sendExpression()">Send</button>
                </div>
                <div id="output" class="output-box math"></div>
            </body>
            </html>
        """

    @pyqtSlot(str)
    def update_mathjax_expression(self, expression):
        self.web_view.page().runJavaScript(f"updateExpression('{expression}')")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
