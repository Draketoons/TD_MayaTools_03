from MayaUtils import *
from PySide2.QtWidgets import QPushButton, QVBoxLayout
import maya.cmds as mc
import importlib
import MayaUtils
importlib.reload(MayaUtils)

class ProxyRigger:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.jnts = []

    def CreateProxyRigFromSelectedMesh(self):
        mesh = mc.ls(sl=True)[0]
        if not IsMesh(mesh):
            raise TypeError(f"{mesh} is not a mesh!")
        
        self.model = mesh
        modelShape = mc.listRelatives(self.model, s=True)[0]
        print(f"found mesh {mesh} and shape {modelShape}")

        skin = GetAllConnectIn(modelShape, GetUpperStream, 10, IsSkin)
        if not skin:
            raise Exception(f"{mesh} has no skin!")
        self.skin = skin[0]

        jnts = GetAllConnectIn(modelShape, GetUpperStream, 10, IsJoint)
        if not jnts:
            raise Exception(f"{mesh} has no joints binded!")
        self.jnts = jnts

        print(f"mesh: {self.model}, skin: {self.skin}, joints: {self.jnts}")

        jntVertMap = self.GenerateVrtDict()
        segments = []
        ctrls = []
        for jnt, verts in jntVertMap.items():
            print(f"joint {jnt} controls {verts} primarily")
    
    def GenerateVrtDict(self):
        dict = {}
        for jnt in self.jnts:
            dict[jnt] = []
        
        verts = mc.ls(f"{self.model}.vtx[*]", fl=True)
        for vert in verts:
            owningJnt = self.GetJntWithMaxInfluence(vert, self.skin)
            dict[owningJnt].append(vert)
        
        return dict
    
    def GetJntWithMaxInfluence(self, vert, skin):
        weights = mc.skinPercent(skin, vert, q=True, v=True)
        jnts = mc.skinPercent(skin, vert, q=True, t=None)

        maxWeightIndex = 0
        maxWeight = weights[0]

        for i in range(1, len(weights)):
            if weights[i] > maxWeight:
                maxWeight = weights[i]
                maxWeightIndex = i

        return jnts[maxWeightIndex]

class ProxyRiggerWidget(QMayaWindow):
    def __init__(self):
        super().__init__()
        self.proxyRigger = ProxyRigger()
        self.setWindowTitle("Proxy Rigger")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        generateProxyRigBtn = QPushButton("Generate Proxy Rig")
        self.masterLayout.addWidget(generateProxyRigBtn)
        generateProxyRigBtn.clicked.connect(self.GenerateProxyRigBtnClicked)

    def GenerateProxyRigBtnClicked(self):
        self.proxyRigger.CreateProxyRigFromSelectedMesh()

    def GetWindowHash(self):
        return "2401e835b25f8769cba309ce93c2b157"

proxyRiggerWidget = ProxyRiggerWidget()
proxyRiggerWidget.show()