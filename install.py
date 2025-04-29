import os
import shutil
import maya.cmds as mc

def Install():
    prjPath = os.path.dirname(os.path.abspath(__file__))
    print(prjPath)
    pluginName = os.path.split(prjPath)[-1]
    mayaScriptPath = os.path.join(mc.internalVar(uad=True), "scripts")
    
    pluginDestinationPath = os.path.join(mayaScriptPath, pluginName)
    if os.path.exists(pluginDestinationPath):
        shutil.rmtree(pluginDestinationPath)
    
    os.makedirs(pluginDestinationPath, exist_ok=True)
    srcDirName = "src"
    assetDirName = "assets"
    shutil.copytree(os.path.join(prjPath, srcDirName), os.path.join(pluginDestinationPath, srcDirName))
    shutil.copytree(os.path.join(prjPath, assetDirName), os.path.join(pluginDestinationPath, assetDirName))
    shutil.copytree(os.path.join(prjPath, "vendor"), os.path.join(pluginDestinationPath, "vendor"))
    shutil.copy2(os.path.join(prjPath, "__init__.py"), os.path.join(pluginDestinationPath, "__init__.py"))

    def AddShelfBtn(scriptName):
        currentShelf = mc.tabLayout("ShelfLayout", q=True, selectTab=True)
        mc.setParent(currentShelf)
        icon = os.path.join(pluginDestinationPath, assetDirName, scriptName + ".PNG")
        mc.shelfButton(c=f"from {pluginName}.src import {scriptName};{scriptName}.Run()", image=icon)

    AddShelfBtn("LimbRiggingTool")
    AddShelfBtn("MayaToUE")
    AddShelfBtn("ProxyRigger")