import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSizePolicy, QVBoxLayout, QPushButton, QDialog
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

        self.options = ReorderTray(2, True, None, "▰")
        self.options.entryChanged.connect(self.optionsChanged)
        self.options.setFixedWidth(220)
        self.options.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.options)

        self.criteria = ReorderTray(-1, False, self.blankCriterion, "▥")
        self.criteria.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        layout.addWidget(self.criteria)


    def multisliders(self):
        return [crit.mslider for n, crit in self.criteria.getItems()]

    @pyqtSlot()
    def blankCriterion(self):
        mslider = MultiSlider(150, 500)
        mslider.addHandles([x[0] for x in self.options.getItems()])
        mslider.changeForward.connect(self.newForward)

        criterion = Criterion(mslider, self.multisliders)
        return criterion

    @pyqtSlot(str)
    def newForward(self, name):
        for mslider in self.multisliders():
            mslider.bringForward(name)

    @pyqtSlot(str, str)
    def optionsChanged(self, oldname, newname):
        if oldname == "":
            for mslider in self.multisliders():
                mslider.addHandle(newname)
        elif newname == "":
            for mslider in self.multisliders():
                mslider.deleteHandle(oldname)
        else:
            for mslider in self.multisliders():
                mslider.renameHandle(oldname, newname)


class Criterion(QWidget):
    def __init__(self, mslider, critGetter):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.mslider = mslider
        layout.addWidget(self.mslider)

        self.configButton = QPushButton("◊◇◊")
        layout.addWidget(self.configButton)
        self.configPopup = CriterionConfig(critGetter)

        self.configButton.pressed.connect(self.openConfig)
        
    def openConfig(self):
        self.configPopup.exec()

class CriterionConfig(QDialog):
    def __init__(self, critGetter):
        super().__init__()

        self.critGetter = critGetter
        self.inputCrits = set()
        self.visited = False
        

    def refillOptions(self):
        all_crit = self.critGetter()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DecisionWindow()
    window.show()

    sys.exit(app.exec())
