import os
import sd
from PySide2 import QtCore, QtWidgets, QtUiTools
from PySide2.QtWidgets import QFileDialog
from sd.tools import io
from sd.ui.graphgrid import *
from sd.api.sbs.sdsbscompgraph import *
from sd.api.sdvaluecolorrgba import *
from sd.api.sdvalueusage import *
from sd.api.sdvaluearray import *
from sd.api.sdvalueenum import *
from sd.api.sdvaluebool import *
from sd.api.sdvaluestring import *
from sd.api.sdtypefloat2 import *
from sd.api.sdtypefloat3 import *
from sd.api.sdvaluefloat2 import *
from sd.api.sdvaluefloat3 import *
from sd.api.sdtypeusage import *
from sd.api.sdresourcebitmap import *
from sd.api.sdgraphobjectcomment import *
from sd.api.sbs import sdsbsarexporter
from sd.api.sdresourcebitmap import SDResourceBitmap
from sd.api.sdresource import EmbedMethod


# Get the context, application and the UI Manager.
ctx = sd.getContext()
app = ctx.getSDApplication()
uiMgr = app.getQtForPythonUIMgr()

cGridSize = GraphGrid.sGetFirstLevelSize()

# Create a new dialog. For shortcuts to work correctly
# it is important to parent the new dialog to Designer's main window.
mainWindow = uiMgr.getMainWindow()
dialog = QtWidgets.QDialog(parent=mainWindow)


# Define inputs and buttons for layout
# Input maps folder path
# TODO: Add a folder path selector button
inputMapsFolderPathLabel = QtWidgets.QLabel("Input Maps Folder Path:")
inputMapsFolderPath = QtWidgets.QLineEdit()
inputMapsFolderPath.setPlaceholderText("Enter folder path")
inputFolderSelectorButton = QtWidgets.QPushButton("Select Folder...")
# TODO: This is dev temp, remove afterwards
inputMapsFolderPath.setText("D:/Work/Quixel/Megascans/Assets/Downloaded/surface/rock_smooth_vepxaa1")

# SBSAR Material name input
# TODO: Make this feild a required feild
outputMaterialNameLabel = QtWidgets.QLabel("SBSAR Material Name:")
outputMaterialName = QtWidgets.QLineEdit()
outputMaterialName.setPlaceholderText("Enter material name")
# TODO: Set a better default name value
outputMaterialName.setText("SDPluginTestMaterial")

# Physical Size Inputs
physicalSizeLabel = QtWidgets.QLabel("Physical Size (m):")
physicalSizeX = QtWidgets.QLineEdit()
physicalSizeY = QtWidgets.QLineEdit()
physicalSizeZ = QtWidgets.QLineEdit()
physicalSizeX.setPlaceholderText("2")
physicalSizeY.setPlaceholderText("2")
physicalSizeZ.setPlaceholderText("0.25")
physicalSizeX.setText("2")
physicalSizeY.setText("2")
physicalSizeZ.setText("0.25")


# Output folder path input with default value
# TODO: Add a folder path selector button
outputFolderPathLabel = QtWidgets.QLabel("Output Folder Path (Optional):")
outputFolderPath = QtWidgets.QLineEdit()
outputFolderPath.setPlaceholderText("Output folder (optional)")
outputFolderSelectorButton = QtWidgets.QPushButton("Select Folder...")
# TODO: Set the default value to G Drive folder
outputFolderPath.setText("G:/Shared drives/Project-Y_Source/Substance_Suite/Resources/MegascansMaterials")

# TODO: Add two buttons
# Import Textures - Only imports input textures into the graph
# Export SBSAR - Exports a SBSAR file to the output folder

# Button to trigger texture import
importButton = QtWidgets.QPushButton("Import Textures")

# ... Add functionality to import button

# Add all elements to a layout
layout = QtWidgets.QGridLayout()  # Use a QGridLayout
# layout = QtWidgets.QVBoxLayout()
layout.addWidget(inputMapsFolderPathLabel, 0, 0)
layout.addWidget(inputMapsFolderPath, 0, 1)
layout.addWidget(outputMaterialNameLabel, 1, 0)
layout.addWidget(outputMaterialName, 1, 1)
# layout.addWidget(QtWidgets.QLabel(""), 2, 0)  # Empty row for spacing
layout.addWidget(outputFolderPathLabel, 6, 0)
layout.addWidget(outputFolderPath, 6, 1)
# Add physical size label and input fields (single line)
layout.addWidget(physicalSizeLabel, 3, 0)  # Row 3, Column 0
# Use QSpacerItem to separate size fields and align labels horizontally
# layout.addItem(QtWidgets.QSpacerItem(40, 20), 3, 1)  # Spacer between label and fields
layout.addWidget(physicalSizeX, 3, 1)  # Row 3, Column 2
layout.addWidget(physicalSizeY, 4, 1)  # Row 3, Column 3
layout.addWidget(physicalSizeZ, 5, 1)  # Row 3, Column 4

# Add buttons to the layout
layout.addWidget(inputFolderSelectorButton, 0, 2)
layout.addWidget(outputFolderSelectorButton, 6, 2)

layout.addWidget(importButton)

progressBar = QtWidgets.QProgressBar(dialog)
progressBar.setMinimum(0)
progressBar.setMaximum(100)
layout.addWidget(progressBar, 8, 0, 1, 2)

# Add the layout to plugin's UI window
dialog.setLayout(layout)
dialog.resize(600, 400)

# Show the dialog (non-modal).
def importMegascans():
    dialog.show()

def addMenu():
    # Create a new menu.
    menu = uiMgr.newMenu(menuTitle="Megascans2Substance", objectName="m2s.menu")
    # Create a new action.
    act = QtWidgets.QAction("Import Megascans", menu)
    act.triggered.connect(importMegascans)

    # Add the action to the menu.
    menu.addAction(act)

def removeMenu():
    print('Remove Menu called')
    # TODO: This is not working, fix it!
    uiMgr.deleteMenu('m2s.menu')
    # # Get the main menu bar
    # main_menu_bar = uiMgr.getMainWindow().menuBar()
    #
    # # Find and remove the menu by its object name
    # for index in range(main_menu_bar.count()):
    #     menu_item = main_menu_bar.itemAt(index).menu()
    #     if menu_item.objectName() == "m2s.menu":
    #         main_menu_bar.removeAction(menu_item.menuAction())
    #         break

# Get the current graph from the UI Manager
graph = uiMgr.getCurrentGraph()
sdPackage = graph.getPackage()
exporter = sdsbsarexporter.SDSBSARExporter.sNew()
# Adjust as needed # TODO: Provide option in the menu
exporter.setCompressionMode(sdsbsarexporter.SDCompressionMode.NoCompression)


def importTextures(mapsFolderPath, materialName, outputFolder, physicalSizeX, physicalSizeY, physicalSizeZ):
    # ... Validate input parameters ...

    progressValue = 0
    progressBar.setValue(progressValue)
    # Map types and keywords
    mapTypes = {
        "Albedo": ["albedo"],
        "Normal": ["normal", "nrm"],
        "Roughness": ["roughness", "rough"],
        "Metallic": ["metallic", "metal"],
        "Ambient Occlusion": ["ambientocclusion", "ao"],
        "Displacement": ["displacement", "disp"],
    }

    # Map types and corresponding output slots
    mapTypesToSlots = {
        "Albedo": {
            "input_map_name": "Albedo.png",
            "nodeIdentifier": "basecolor",
            "nodeLabel": "Base Color",
            "colorMode": "Color",
            "defaultColorValue": 0.5,
            "slot_index": 1,
        },
        "Normal": {
            "input_map_name": "Normal.png",
            "nodeIdentifier": "normal",
            "nodeLabel": "Normal",
            "colorMode": "Color",
            "defaultColorValue": 0.5,
            "slot_index": 2,
        },
        "Roughness": {
            "input_map_name": "Roughness.png",
            "nodeIdentifier": "roughness",
            "nodeLabel": "Roughness",
            "colorMode": "Grayscale",
            "defaultColorValue": 0.25,
            "slot_index": 3,
        },
        "Metallic": {
            "input_map_name": "Metallic.png",
            "nodeIdentifier": "metallic",
            "nodeLabel": "Metallic",
            "colorMode": "Grayscale",
            "defaultColorValue": 0.0,
            "slot_index": 4,
        },
        "Ambient Occlusion": {
            "input_map_name": "AmbientOcclusion.png",
            "nodeIdentifier": "ambientocclusion",
            "nodeLabel": "Ambient Occlusion",
            "colorMode": "Grayscale",
            "defaultColorValue": 1.0,
            "slot_index": 5,
        },
        "Displacement": {
            "input_map_name": "Displacement.png",
            "nodeIdentifier": "height",
            "nodeLabel": "Displacement",
            "colorMode": "Grayscale",
            "defaultColorValue": 0.5,
            "slot_index": 6,
        },
    }

    # key: value :: node identifier : GraphNodeId
    outputNodeIds = {
        "basecolor": "",
        "normal": "",
        "roughness": "",
        "metallic": "",
        "ambientocclusion": "",
        "height": ""
    }

    # map node indetifiers to node ids, although bad naming from Adobe api programmers
    graphNodes = graph.getNodes()
    for i in range(graphNodes.getSize()):
        currentNode = graphNodes.getItem(i)
        id = 'identifier'
        category = SDPropertyCategory.Annotation
        identifierProperty = currentNode.getPropertyFromId(id, category)
        valueObject = currentNode.getPropertyValue(identifierProperty)
        if valueObject:
            outputNodeIds[valueObject.get()] = currentNode.getIdentifier()

    progressValue = progressValue + 30
    progressBar.setValue(progressValue)

    for mapType, keywords in mapTypes.items():
        mapFound = True
        # Find the first matching filename with any extension
        for filename in os.listdir(mapsFolderPath):
            if any(keyword.lower() in filename.lower() for keyword in keywords):
                mapPath = os.path.join(mapsFolderPath, filename)
                if os.path.exists(mapPath):
                    break  # Found a match, stop searching
        else:
            print(f"Warning: Missing map of type: {mapType}")
            mapFound = False
            # continue


        if mapFound:
            # Create bitmap node from the found file
            linkedSDResourceBitmap = SDResourceBitmap.sNewFromFile(sdPackage, mapPath, EmbedMethod.Linked)
            # bitmap resource identifier
            bitmapResourceIdentifier = materialName + "_" + mapType
            #       - Change the resource identifier
            linkedSDResourceBitmap.setIdentifier(bitmapResourceIdentifier)

            #   - Instantiate the bitmap resource to the graph to have a node that will refers the created bitmap resource
            sdSBSCompNodeBitmap = graph.newInstanceNode(linkedSDResourceBitmap)
            sdSBSCompNodeBitmap.setPosition(float2(-2 * cGridSize, -cGridSize))
            # set the color mode of bitmap
            id = 'colorswitch'
            category = SDPropertyCategory.Input
            colorSwitchProperty = sdSBSCompNodeBitmap.getPropertyFromId(id, category)
            value = (mapTypesToSlots[mapType]["colorMode"] == 'Color')
            sdValueObject = SDValueBool.sNew(value)
            sdSBSCompNodeBitmap.setPropertyValue(colorSwitchProperty, sdValueObject)
            inputNode = sdSBSCompNodeBitmap
        else:
            if (mapType == 'Normal'):
                sdSBSCompNodeNormal = graph.newNode('sbs::compositing::normal')
                sdGraphObjectComment = SDGraphObjectComment.sNewAsChild(sdSBSCompNodeNormal)
                # sdGraphObjectComment.setPosition(float2(-cGridSize * 0.5, cGridSize * 0.5))
                sdGraphObjectComment.setDescription(f'This is an auto-generated default node for {mapType}')
                sdSBSCompNodeNormal.setInputPropertyValueFromId('input2alpha', SDValueBool.sNew(False))
                inputNode = sdSBSCompNodeNormal
            else:
                # Create a uniform color node
                sdSBSCompNodeUniform = graph.newNode('sbs::compositing::uniform')
                # Create New Comment attached on a Node
                sdGraphObjectComment = SDGraphObjectComment.sNewAsChild(sdSBSCompNodeUniform)
                # sdGraphObjectComment.setPosition(float2(-cGridSize * 0.5, cGridSize * 0.5))
                sdGraphObjectComment.setDescription(f'This is an auto-generated default node for {mapType}')
                colorSpaceValue = (mapTypesToSlots[mapType]["colorMode"] == 'Color')
                sdSBSCompNodeUniform.setInputPropertyValueFromId('colorswitch', SDValueBool.sNew(colorSpaceValue))
                defaultColorValue = mapTypesToSlots[mapType]["defaultColorValue"]
                sdValueColorRGBA = SDValueColorRGBA.sNew(ColorRGBA(defaultColorValue, defaultColorValue, defaultColorValue, 1.0))
                sdSBSCompNodeUniform.setInputPropertyValueFromId('outputcolor', sdValueColorRGBA)
                inputNode = sdSBSCompNodeUniform

        # ... Connect the node to your desired output nodes ...
        # Find the corresponding output node based on map type
        outputNodeIdentifier = mapTypesToSlots[mapType]["nodeIdentifier"]
        outputNodeLabel = mapTypesToSlots[mapType]["nodeLabel"]
        outputNodeForMap = graph.getNodeFromId(outputNodeIds[outputNodeIdentifier])

        # Connect map node to output node slot
        if outputNodeForMap:
            print('OUTPUT NODE FOUND!')
            # Set bitmap node position
            inputNode.setPosition(float2(outputNodeForMap.getPosition().x - (4*cGridSize), outputNodeForMap.getPosition().y))
            outputId = 'unique_filter_output'
            targetId = 'inputNodeOutput'
            connection = inputNode.newPropertyConnectionFromId(outputId, outputNodeForMap, targetId)

        progressValue = progressValue + 10
        progressBar.setValue(progressValue)

    # ... Set other material properties and connections ...
    graph.setAnnotationPropertyValueFromId('physical_size', SDValueFloat3.sNew(float3(float(physicalSizeX)*100, float(physicalSizeY)*100, float(physicalSizeZ)*100)))

    graph.setAnnotationPropertyValueFromId('author', SDValueString.sNew('Monastic Hill Studios'))
    graph.setAnnotationPropertyValueFromId('author_url', SDValueString.sNew('monastichill.com'))
    graph.setAnnotationPropertyValueFromId('identifier', SDValueString.sNew(materialName))

    sbsarOutputFilePath = os.path.join(outputFolder, materialName + ".sbsar")
    exporter.exportPackageToSBSAR(sdPackage, sbsarOutputFilePath)
    print("Material saved as:", "output_folder/" + materialName + ".sbsar")

    progressBar.setValue(100)
    dialog.close()


importButton.clicked.connect(lambda: importTextures(
    inputMapsFolderPath.text(),
    outputMaterialName.text(),
    outputFolderPath.text(),
    physicalSizeX.text(),
    physicalSizeY.text(),
    physicalSizeZ.text()
))

def selectInputFolder():
    folderPath = QFileDialog.getExistingDirectory(dialog, "Select Input Maps Folder")
    if folderPath:
        inputMapsFolderPath.setText(folderPath)

def selectOutputFolder():
    folderPath = QFileDialog.getExistingDirectory(dialog, "Select Output Folder")
    if folderPath:
        outputFolderPath.setText(folderPath)

inputFolderSelectorButton.clicked.connect(selectInputFolder)
outputFolderSelectorButton.clicked.connect(selectOutputFolder)

# TODO: Cleanup all created resources and nodes after completion of operations. Need to keep the default project clean.

# Plugin entry point. Called by Designer when loading a plugin.
def initializeSDPlugin():
    print("Hello!")
    addMenu()


def uninitializeSDPlugin():
    print("Bye!")
    removeMenu()
