import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from sliders import MultiSlider

class DecisionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Decision Axes")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        slider_row = QHBoxLayout()
        layout.addLayout(slider_row)

        options = ["hey", "wow", "omg", "aah", ":))"]

        self.all_sliders = []
        for i in range(5):
            mslider = MultiSlider(100, 300)
            mslider.addHandles(options)
            mslider.changeForward.connect(self.newForward)
            slider_row.addWidget(mslider)
            self.all_sliders.append(mslider)

    @pyqtSlot(str)
    def newForward(self, name):
        for slider in self.all_sliders:
            slider.bringForward(name)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DecisionWindow()
    window.show()

    sys.exit(app.exec())
