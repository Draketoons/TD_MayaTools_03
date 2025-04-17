from PySide2.QtWidgets import (QVBoxLayout,
                               QLineEdit,
                               QPushButton,
                               QMessageBox,
                               QListWidget)
from MayaUtils import *
import maya.cmds as mc

class MayaToUE:
    def __init__(self):
        self.meshes = []
        self.rootJnt = ""
    
    def SetSelectedAsRootJnt(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("No Joint Selected! Select the Root Joint of the Rig")
        
        selectedJnt = selection[0]
        if not IsJoint(selectedJnt):
            raise Exception(f"{selectedJnt} is not a joint! Please select the root joint of the rig!")
        
        self.rootJnt = selectedJnt
    
    def AddRootJoint(self):
        if (not self.rootJnt) or (not mc.objExists(self.rootJnt)):
            raise Exception("No Root Joint Assigned! Please Set Root Joint")
        
        currentRootJntPosX, currentRootJntPosY, currentRootJntPosZ = mc.xform(self.rootJnt, q=True, t=True, ws=True)
        if currentRootJntPosX == 0 and currentRootJntPosY == 0 and currentRootJntPosZ == 0:
            raise Exception("Rig already has a set root joint at the origin")
        
        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName
    
    def AddMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("No mesh selected! please select a mesh")
        
        meshes = set()

        for sel in selection:
            if IsMesh(sel):
                meshes.add(sel)
        
        if len(meshes) == 0:
            raise Exception("No mesh selected!")
        
        self.meshes = list(meshes)

class MayaToUEWidget(QMayaWindow):
    def GetWindowHash(self):
        return "MayaToUEMC04172025"
    
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.setWindowTitle("Maya to UE")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectionAsRootJntBtn = QPushButton("Set Root Joint")
        setSelectionAsRootJntBtn.clicked.connect(self.SetSelectionAsRootJntBtnClicked)
        self.masterLayout.addWidget(setSelectionAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntButtonClicked)
        self.masterLayout.addWidget(addRootJntBtn)

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        self.meshList.setFixedHeight(80)
        addMeshBtn = QPushButton("Add Meshes")
        addMeshBtn.clicked.connect(self.AddMeshButtonClicked)
        self.masterLayout.addWidget(addMeshBtn)
    
    def AddMeshButtonClicked(self):
        try:
            self.mayaToUE.AddMeshes()
            self.meshList.clear()
            self.meshList.addItems(self.mayaToUE.meshes)
        except Exception as e:
            QMessageBox().critical(self, "Error", f"{e}")

    def AddRootJntButtonClicked(self):
        try:
            self.mayaToUE.AddRootJoint()
            self.rootJntText.setText(self.mayaToUE.rootJnt)
        except Exception as e:
            QMessageBox().critical(self, "Error", f"{e}")
    
    def SetSelectionAsRootJntBtnClicked(self):
        try:
            self.mayaToUE.SetSelectedAsRootJnt()
            self.rootJntText.setText(self.mayaToUE.rootJnt)
        except Exception as e:
            QMessageBox().critical(self, "Error", f"{e}")

MayaToUEWidget().show()