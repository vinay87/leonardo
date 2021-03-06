from __future__ import division
import math
import json
import os
from PyQt4 import QtGui, QtCore
from QColorPanel import QColorPanel
import subprocess

class PositionWidget(QtGui.QWidget):
    def __init__(self):
        super(PositionWidget, self).__init__()
        self.clip = QtGui.QApplication.clipboard()
        self.row_widgets = {}
        self.createUI()
        self.changedCoords = False

    def createUI(self):
        self.use_enforced_coordinates = QtGui.QPushButton("Enforce All Coordinates")
        self.use_enforced_USP_coordinates = QtGui.QPushButton("Enforce USP Coordinates")
        self.use_calculated_coordinates = QtGui.QPushButton("Calculate Coordinates")
        
        self.use_enforced_coordinates.setCheckable(True)
        self.use_enforced_USP_coordinates.setCheckable(True)
        self.use_calculated_coordinates.setCheckable(True)

        self.use_calculated_coordinates.setChecked(True)

        self.buttons_group = QtGui.QButtonGroup()
        self.buttons_group.setExclusive(True)
        self.buttons_group.addButton(self.use_calculated_coordinates)
        self.buttons_group.addButton(self.use_enforced_USP_coordinates)
        self.buttons_group.addButton(self.use_enforced_coordinates)

        buttons_layout = QtGui.QHBoxLayout()
        buttons_layout.addWidget(self.use_calculated_coordinates)
        buttons_layout.addWidget(self.use_enforced_USP_coordinates)
        buttons_layout.addWidget(self.use_enforced_coordinates)
        
        self.use_enforced_coordinates.setToolTip("Select this option to override all the calculated coordiates with the coordinates shown below.")
        self.use_enforced_USP_coordinates.setToolTip("Select this option to override only the USP icons' calculated coordiates with the coordinates shown below.\nParent images will be placed depending on your chosen location, in accordance with the dimensions.")
        self.use_calculated_coordinates.setToolTip("Select this option if you'd like Leonardo to calculate the coordinates of the icon and image positions completely.\nThere is a great chance of an overlap happening due to this option.")


        self.show_position_markers = QtGui.QCheckBox("Show Position Markers for USPs")
        self.export_coordinates_button = QtGui.QPushButton("Export Coordinates to JSON")
        self.export_coordinates_button.clicked.connect(self.exportCoordinates)
        self.load_coordinates_button = QtGui.QPushButton("Load Coordinates from JSON")
        self.load_coordinates_button.clicked.connect(self.loadCoordinates)
        more_buttons_layout = QtGui.QHBoxLayout()
        more_buttons_layout.addWidget(self.export_coordinates_button)
        more_buttons_layout.addWidget(self.load_coordinates_button)

        self.position_table = QtGui.QTableWidget()
        self.position_table.setRowCount(11)
        self.position_table.setColumnCount(3)
        self.parent_label = "Parent"
        self.position_table.setItem(0, 0, QtGui.QTableWidgetItem(str(self.parent_label)))
        x_parent = QtGui.QSpinBox()
        y_parent = QtGui.QSpinBox()
        self.position_table.setCellWidget(0, 1, x_parent)
        self.position_table.setCellWidget(0, 2, y_parent)
        self.position_table.setItem(0, 3, QtGui.QTableWidgetItem("NA"))
        self.position_table.setItem(0, 4, QtGui.QTableWidgetItem("NA"))
        self.row_widgets[self.parent_label] = [x_parent, y_parent, 0, 0]
        
        for row in range(11)[1:]:
            label = "USP-%d"%row
            x = QtGui.QSpinBox()
            y = QtGui.QSpinBox()
            icon_size = QtGui.QSpinBox()
            font_panel = QColorPanel()
            self.position_table.setItem(row, 0, QtGui.QTableWidgetItem(str(label)))
            self.position_table.setCellWidget(row, 1, x)
            self.position_table.setCellWidget(row, 2, y)
            self.position_table.setCellWidget(row, 3, icon_size)
            self.position_table.setCellWidget(row, 4, font_panel)

            self.row_widgets[label] = [x, y, icon_size, font_panel]
        self.position_table.resizeRowsToContents()
        for column_counter in range(3):
            self.position_table.setColumnWidth(column_counter, 90)

        self.position_table.setHorizontalHeaderLabels(["Feature","X","Y", "Size\nw.r.t Height", "Colors"])
        self.layout = QtGui.QVBoxLayout()
        self.layout.addLayout(buttons_layout)
        self.layout.addWidget(self.show_position_markers)
        self.layout.addLayout(more_buttons_layout)
        self.layout.addWidget(self.position_table)
        for label in self.row_widgets.keys():
            limit  = 100000
            self.row_widgets[label][0].setRange(-1*limit, limit)
            self.row_widgets[label][0].valueChanged.connect(self.changeCoords)
            self.row_widgets[label][1].setRange(-1*limit, limit)
            self.row_widgets[label][1].valueChanged.connect(self.changeCoords)
            if label != self.parent_label:
                self.row_widgets[label][2].setRange(0, 100)
                self.row_widgets[label][2].setSuffix("%")
        self.setLayout(self.layout)

    def setCoords(self, coords):
        success = True
        for label in coords.keys():
            accepted_labels = ["Parent"] + ["USP-%d"%(i+1) for i in range(10)]
            if label in accepted_labels:
                self.row_widgets[label][0].setValue(coords[label][0])
                self.row_widgets[label][1].setValue(coords[label][1])
            else:
                success = False
                print "%s is not an acceptable label. Check the JSON."%label
        return success
    def getCoords(self):
        coords = {}
        for label in self.row_widgets.keys():
            coords[label] = [self.row_widgets[label][0].value(), self.row_widgets[label][1].value()]
        return coords

    def changeCoords(self):
        self.changed_coords = True

    def showPositionMarkers(self):
        return self.show_position_markers.isChecked()

    def getCoordinatesMode(self):
        if self.use_calculated_coordinates.isChecked():
            mode = 0
        elif self.use_enforced_USP_coordinates.isChecked():
            mode = 1
        elif self.use_enforced_coordinates.isChecked():
            mode = 2
        else:
            print "Error getting the mode of the coordinates in PositionWidget, none of the buttons seem to be checked."
            mode = 0
        return mode

    def exportCoordinates(self):
        save_file_name = QtGui.QFileDialog.getSaveFileName(self, "Save Settings To a JSON",
                                                        os.getcwd(), ("JSON files (*.json)")
                                                        )
        if save_file_name:
            coords = self.getCoords()
            with open(save_file_name,"w") as json_file_handler:
                json.dump(coords,json_file_handler,indent=4,sort_keys=True)

    def loadCoordinates(self):
        open_file_name = QtGui.QFileDialog.getOpenFileName(self, "Load Settings from a JSON",
                                                        os.getcwd(), ("JSON files (*.json)")
                                                        )
        if open_file_name:
            if os.path.isfile(open_file_name):
                with open(open_file_name) as json_file_handler:
                    coords = json.load(json_file_handler)
                success = self.setCoords(coords)
                if success:
                    self.alertMessage("Success","Successfully loaded the coordinates from the JSON.")
                    self.use_enforced_coordinates.setChecked(True)
                else:
                    self.alertMessage("Failure","The JSON doesn't seem to be valid. You must have loaded the settings file instead of the coordinates file!")
                    subprocess.call('explorer /select,"%s"'%self.open_file_name, shell=True)

    def setColors(self, colors_list):
        for color in colors_list:
            for label in self.row_widgets.keys():
                if label != self.parent_label:
                    self.row_widgets[label][3].setColors(color)

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            if e.key() == QtCore.Qt.Key_S:
                self.say = QtGui.QMessageBox.question(self,"All Animals are created equal.","But some animals are <b>more</b> equal than others.", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            if e.key() == QtCore.Qt.Key_C: #copy
                selected = self.position_table.selectedRanges()
                columns = [selected[0].leftColumn(), selected[0].rightColumn()]
                rows = [selected[0].topRow(), selected[0].bottomRow()]
                if 3 in columns:
                    colors_list = []
                    for row in rows:
                        if row != 0:
                            colors_list.append(self.row_widgets[row].getColors())
                    s = str(Colors)
                    print s
                    self.clip.setText(s)

    def alertMessage(self, title, message):
        QtGui.QMessageBox.about(self, title, message)