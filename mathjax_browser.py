import sys
import threading
import web_server
import signal
import os

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

# Comment out the unused MathJax source to avoid conflits. 127.0.0.1
pageSource = """
<html><head>
<script id="MathJax-script" async src="http://localhost:5000/es5/tex-mml-svg.js"></script>
<!--script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script-->
</script></head>
<body>
<p><mathjax style="font-size:2.3em">$$u = \int_{-\infty}^{\infty}(awesome)\cdot du$$</mathjax></p>
<p>
  When \(a \\neq 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
  \[x = {-b \pm \sqrt{b^2-4ac} \over 2a}.\]
</p>
</body></html>
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.browser = QWebEngineView()
        self.browser.setHtml(pageSource)        
        self.setCentralWidget(self.browser)
    
    def closeEvent(self, event):
        # Send SIGTERM to stop the Flask server
        os.kill(os.getpid(), signal.SIGTERM)
        event.accept()
        
def run_flask():
    # Execute the script
    web_server.app.run(port=5000, debug=True, use_reloader=False)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

flask_thread = threading.Thread(target = run_flask)
flask_thread.start()

sys.exit(app.exec())