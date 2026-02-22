import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSizePolicy, QVBoxLayout, QPushButton, QDialog, QFormLayout, QLabel, QCheckBox
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QSize, Qt
from PyQt6.QtGui import QPalette, QColor

from sliders import MultiSlider
from reorderable import ReorderTray

class DecisionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("◌ 	◍ 	◎")

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
        self.criteria.insideDeleted.connect(self.criterionDeleted)
        layout.addWidget(self.criteria)


    def multisliders(self):
        return [crit.mslider for crit in self.criteria.getItems()]

    @pyqtSlot()
    def blankCriterion(self, reorderable):
        mslider = MultiSlider(150, 500)
        mslider.addHandles(self.options.getNames())
        mslider.changeForward.connect(self.newForward)

        criterion = Criterion(mslider, self.criteria.getItems, reorderable)
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

    @pyqtSlot(QWidget)
    def criterionDeleted(self, crit):
        for c in self.criteria.getItems():
            c.receives -= {crit}
            c.updateInfluences(c.influences - {crit})


class Criterion(QWidget):

    updateValues = pyqtSignal(dict)
    
    def __init__(self, mslider, critGetter, reorderable):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.mslider = mslider
        self.mslider.updateValues.connect(self.valuesUpdated)
        layout.addWidget(self.mslider)

        self.critGetter = critGetter

        self.rname = ""
        reorderable.nameChanged.connect(self.setName)
        
        self.configButton = QPushButton("◊◊◊")
        layout.addWidget(self.configButton)

        self.influences = set()
        self.receives = set()

        self.configButton.pressed.connect(self.openConfig)

    def setName(self, idx, oldname, newname):
        self.rname = newname
        
    def openConfig(self):
        CriterionConfig(self).exec()

    def getValues(self):
        return self.mslider.getValues()

    def setValues(self, update):
        self.mslider.setValues(update)

    @pyqtSlot(dict)
    def valuesUpdated(self, update):
        self.updateValues.emit(update)
        for r in self.receives:
            r.recalc()

    def recalc(self):        
        sum_dict = {n: 0 for n in self.getValues()}
        for i in self.influences:
            o_vals = i.getValues()
            for n in o_vals:
                sum_dict[n] += o_vals[n]
        for n in sum_dict:
            sum_dict[n] //= len(self.influences)
        self.setValues(sum_dict)

    def updateInfluences(self, new_influences):
        self.mslider.setReadOnly(len(new_influences) > 0)
        
        for to_connect in new_influences - self.influences:
            to_connect.receives.add(self)
        for to_disconnect in self.influences - new_influences:
            to_disconnect.receives.remove(self)
        self.influences = new_influences

        if len(self.influences) > 0:
            self.recalc()
        

class CriterionConfig(QDialog):
    def __init__(self, criterion):
        super().__init__()

        self.criterion = criterion
        layout = QVBoxLayout()
        self.setLayout(layout)
        sublayout = QHBoxLayout()
        layout.addLayout(sublayout)
        
        self.influenceChecks = QVBoxLayout()
        sublayout.addLayout(self.influenceChecks)

        self.viewSlider = MultiSlider(150, 250)
        self.viewSlider.setReadOnly(True)
        sublayout.addWidget(self.viewSlider)

        self.confirmButton = QPushButton("🞠🞠🞠")
        self.confirmButton.pressed.connect(self.confirmChanges)
        layout.addWidget(self.confirmButton)
        
        self.setWindowTitle(f"◊ {self.criterion.rname} ◊") 

        downstream = self.findDownstream(self.criterion)

        crits = self.criterion.critGetter()
        self.checkboxes = {}
        for crit in crits:
            cb = QCheckBox(crit.rname)

            if crit in self.criterion.influences:
                cb.setChecked(True)
            if crit in downstream:
                cb.setEnabled(False)
            
            self.checkboxes[cb] = crit
            self.influenceChecks.addWidget(cb)
                

    def makeInfluenceCheck(self, crit):
        check = QCheckBox(crit.rname)
        return check

    def confirmChanges(self):
        new_influences = {self.checkboxes[cb] for cb in self.checkboxes if cb.isChecked()}
        self.criterion.updateInfluences(new_influences)
        self.done(QDialog.DialogCode.Accepted)

    def findDownstream(self, me):
        ret = {me}
        for r in me.receives:
            ret = ret.union(self.findDownstream(r))
        return ret

            

if __name__ == "__main__":
    app = QApplication(sys.argv)

    palette = QApplication.palette()
    palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(255, 190, 190))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(190, 190, 255))
    
    QApplication.setPalette(palette)

    window = DecisionWindow()
    window.show()

    sys.exit(app.exec())
