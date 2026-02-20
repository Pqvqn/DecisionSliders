import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QSize, Qt

from sliders import MultiSlider
from reorderable import ReorderTray

class DecisionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Decision Axes")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        self.options = ReorderTray(2, True, None, "options")
        self.options.entryChanged.connect(self.optionsChanged)
        self.options.setFixedWidth(220)
        self.options.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.options)

        self.criteria = ReorderTray(-1, False, self.blankSlider, "criteria")
        self.criteria.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        layout.addWidget(self.criteria)

    @pyqtSlot()
    def blankSlider(self):
        mslider = MultiSlider(150, 500)
        mslider.addHandles([x[0] for x in self.options.getItems()])
        mslider.changeForward.connect(self.newForward)
        return mslider

    @pyqtSlot(str)
    def newForward(self, name):
        for crit, slider in self.criteria.getItems():
            slider.bringForward(name)

    @pyqtSlot(str, str)
    def optionsChanged(self, oldname, newname):
        if oldname == "":
            for crit, slider in self.criteria.getItems():
                slider.addHandle(newname)
        elif newname == "":
            for crit, slider in self.criteria.getItems():
                slider.deleteHandle(oldname)
        else:
            for crit, slider in self.criteria.getItems():
                slider.renameHandle(oldname, newname)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DecisionWindow()
    window.show()

    sys.exit(app.exec())
