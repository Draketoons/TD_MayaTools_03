from PySide2.QtGui import QColor
import maya.cmds as mc
import maya.mel as mel
from maya.OpenMaya import MVector

from PySide2.QtWidgets import (QWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QLabel,
                               QSlider,
                               QPushButton,
                               QLineEdit,
                               QMessageBox,
                               QColorDialog
                               )
from PySide2.QtCore import Qt
from MayaUtils import QMayaWindow
    
class LimbRigger:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
        self.controllerColor = (0,0,0)

    def AutoFindJnts(self):
        self.root = mc.ls(sl=True, type="joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]

    def CreateFKControlForJnt(self, jntName):
        ctrlName = "arc_fk_" + jntName
        ctrlGrpName = ctrlName + "_grp"
        mc.circle(n=ctrlName, r=self.controllerSize, nr=(1,0,0))
        self.ApplyControllerColor(ctrlName)
        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName,  jntName)
        return ctrlName, ctrlGrpName

    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply = True)
        self.ApplyControllerColor(name)
        grpName = name + "_grp"
        mc.group(name, n=grpName)
        return name, grpName
    
    def CreatePlusController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p 0 0 0 -p 0 6 0 -p -6 6 0 -p -6 12 0 -p 0 12 0 -p 0 18 0 -p 6 18 0 -p 6 12 0 -p 12 12 0 -p 12 6 0 -p 6 6 0 -p 6 0 0 -p 0 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;")
        mc.scale(self.controllerSize/8, self.controllerSize/8, self.controllerSize/8)
        mc.makeIdentity(name, apply = True)
        self.ApplyControllerColor(name)
        grpName = name + "_grp"
        mc.group(name, n=grpName)
        return name, grpName
    
    def GetObjectLocation(self, objectName)->MVector:
        x, y, z = mc.xform(objectName, q=True, t=True, ws=True)
        return MVector(x, y, z)
    
    def PrintMVector(self, vectorToPrint):
        print(f"<{vectorToPrint.x}, {vectorToPrint.y}, {vectorToPrint.z}>")

    def ApplyControllerColor(self, ctrlName):
        shapes = mc.listRelatives(ctrlName, shapes=True, type="nurbsCurve")
        if not shapes:
            return
        
        for shape in shapes:
            mc.setAttr(f"{shape}.overrideEnabled", 1)
            mc.setAttr(f"{shape}.overrideRGBColors", 1)
            mc.setAttr(f"{shape}.overrideColorRGB", self.controllerColor[0], self.controllerColor[1], self.controllerColor[2])

    def RigLimb(self):
        print(f"Start Rigging the limb with {self.root},{self.mid},{self.end}")
        rootCtrl, rootCtrlName = self.CreateFKControlForJnt(self.root)
        midCtrl, midCtrlName = self.CreateFKControlForJnt(self.mid)
        endCtrl, endCtrlName = self.CreateFKControlForJnt(self.end)

        mc.parent(midCtrlName, rootCtrl)
        mc.parent(endCtrlName, midCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        rootJntLoc = self.GetObjectLocation(self.root)
        endJntLoc = self.GetObjectLocation(self.end)

        self.PrintMVector(rootJntLoc)
        self.PrintMVector(endJntLoc)

        rootToEndVec: MVector = endJntLoc - rootJntLoc

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sj=self.root, ee = self.end, sol="ikRPsolver")
        ikPoleVectorVals = mc.getAttr(ikHandleName + ".poleVector")[0]
        ikPoleVector = MVector(ikPoleVectorVals[0], ikPoleVectorVals[1], ikPoleVectorVals[2])
        self.PrintMVector(ikPoleVector)

        ikPoleVector.normalize()
        ikPoleVectorCtrlLoc = rootJntLoc + rootToEndVec / 2 + ikPoleVector * rootToEndVec.length()

        ikPoleVectorCtrlName = "ac_ik_" + self.mid
        mc.spaceLocator(n=ikPoleVectorCtrlName)
        ikPoleVectorCtrlGrp = ikPoleVectorCtrlName + "_grp"
        mc.group(ikPoleVectorCtrlName, n=ikPoleVectorCtrlGrp)
        mc.setAttr(ikPoleVectorCtrlGrp+".t", ikPoleVectorCtrlLoc.x, ikPoleVectorCtrlLoc.y, ikPoleVectorCtrlLoc.z, typ = "double3")
        mc.poleVectorConstraint(ikPoleVectorCtrlName, ikHandleName)

        ikfkBlendCtrlName = "ac_ikfk_blend_" + self.root
        ikfkBlendCtrlName, ikfkBlendGrp = self.CreatePlusController(ikfkBlendCtrlName)
        ikfkBlendCtrlLoc = rootJntLoc + MVector(rootJntLoc.x, rootJntLoc.y+5, rootJntLoc.z)
        mc.setAttr(ikfkBlendGrp+".t", ikfkBlendCtrlLoc.x, ikfkBlendCtrlLoc.y, ikfkBlendCtrlLoc.z, typ="double3")

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrlName, ln=ikfkBlendAttrName, min=0, max=1, k=True)
        ikfkBlendAttr = ikfkBlendCtrlName + "." + ikfkBlendAttrName

        mc.expression(s=f"{ikHandleName}.ikBlend = {ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}.v = {ikPoleVectorCtrlGrp}.v = {ikfkBlendAttr}")
        mc.expression(s=f"{rootCtrlName}.v = 1 - {ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{endCtrl}W0 = 1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}W1 = 1-{ikfkBlendAttr}")

        mc.parent(ikHandleName, ikEndCtrl)
        mc.setAttr(ikHandleName+".v", 0)

        topGrpName = self.root + "_rig_grp"
        mc.group([rootCtrlName, ikEndCtrlGrp, ikPoleVectorCtrlGrp, ikfkBlendGrp], n= topGrpName)

class ColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.colorPickerBtn = QPushButton()
        self.colorPickerBtn.setStyleSheet(f"background-color:black;")
        self.masterLayout.addWidget(self.colorPickerBtn)
        self.colorPickerBtn.clicked.connect(self.ColorPickerBtnClicked)
        self.color = QColor(0,0,0)

    def ColorPickerBtnClicked(self):
        self.color = QColorDialog.getColor()
        self.colorPickerBtn.setStyleSheet(f"background-color:{self.color.name()};")

class LimbRigToolWidget(QMayaWindow):
    def  __init__(self):
        super().__init__()
        self.rigger = LimbRigger()

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.tipLable = QLabel("Select the first joint for the limb, and then click 'Auto Find'")
        self.masterLayout.addWidget(self.tipLable)

        self.jointSelectionText = QLineEdit()
        self.masterLayout.addWidget(self.jointSelectionText)
        self.jointSelectionText.setEnabled(False)

        self.autoFindBtn = QPushButton("Auto Find")
        self.masterLayout.addWidget(self.autoFindBtn)
        self.autoFindBtn.clicked.connect(self.AutoFindBtnClicked)

        ctrlSliderLayout = QHBoxLayout()

        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeValueChanged)
        ctrlSizeSlider.setRange(1,30)
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSliderLayout.addWidget(ctrlSizeSlider)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        self.masterLayout.addWidget(self.ctrlSizeLabel)

        self.masterLayout.addLayout(ctrlSliderLayout)

        self.colorPicker = ColorPicker()
        self.masterLayout.addWidget(self.colorPicker)

        self.setColorBtn = QPushButton("Set Ctrl Color")
        self.masterLayout.addWidget(self.setColorBtn)
        self.setColorBtn.clicked.connect(self.SetColorBtnClicked)


        self.rigLimbBtn = QPushButton("Rig Limb")
        self.masterLayout.addWidget(self.rigLimbBtn)
        self.rigLimbBtn.clicked.connect(self.RigLimbBtnClicked)

        self.setWindowTitle("Limb Rigging Tool")
    
    def CtrlSizeValueChanged(self, newValue):
        self.rigger.controllerSize = newValue
    
    def RigLimbBtnClicked(self):
        color = self.colorPicker.color
        self.rigger.controllerColor = (color.redF(), color.greenF(), color.blueF())
        self.rigger.RigLimb()

    def SetColorBtnClicked(self):
        print("Set Color Button Clicked!")
        color = self.colorPicker.color
        self.rigger.controllerColor = (color.redF(), color.greenF(), color.blueF())
        ctrl = mc.ls(sl=True, type="nurbsCurve")[0]
        self.rigger.ApplyControllerColor(ctrl)

    def AutoFindBtnClicked(self):
        try:
            self.rigger.AutoFindJnts()
            self.jointSelectionText.setText(f"{self.rigger.root} {self.rigger.mid} {self.rigger.end}")
        except Exception as e:
            QMessageBox.critical(self, "Error", "Wrong Slection, please select the first joint of the limb!")

limbRigToolWidget = LimbRigToolWidget()
limbRigToolWidget.show()