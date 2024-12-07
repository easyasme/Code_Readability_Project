# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designerwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget

class ActivityCheckBox():
    def __init__(self, ckb_name, wgt_parent, report_cb):
        self.obj_name = ckb_name
        self.report_cb = report_cb
        self.parent = wgt_parent
        self.checkBox = QtWidgets.QCheckBox(self.parent)
        self.checkBox.setObjectName(ckb_name)
        self.checkBox.stateChanged.connect(self.StateChanged)       
        self.checkBox.setStyleSheet("color: red")
        
    def AddWidget(self, layout_reference):
        self.refence = layout_reference
        self.refence.addWidget(self.checkBox)
        
    def RemoveWidget(self):
        self.refence.removeWidget(self.checkBox)
        self.checkBox.deleteLater()
        self.checkBox = None
        
    def SetText(self, text):
        self.text = text
        
    def UpdateLabel(self, translate):
        self.checkBox.setText(translate("MainWindow", self.text))
        
    def SetCheckState(self, state):
        assert(state == QtCore.Qt.Checked or state == QtCore.Qt.Unchecked)
        self.state = state
        self.checkBox.setCheckState(state)
        
    # stateChanged Qt Signal connected from QCheckBox
    # CheckState:
    #     Qt.Unchecked        0
    #     Qt.PartiallyChecked	1
    #     Qt.Checked          2
    #
    def StateChanged(self, state):
        assert(state == QtCore.Qt.Checked or state == QtCore.Qt.Unchecked)
        self.state = state
        self.report_cb(self.obj_name, self.state)
        
class SliderFeatureController():
    def __init__(self, obj_name, wgt_parent, lyt_parent, report_cb):
        self.obj_name = obj_name
        self.parent = wgt_parent
        self.parent_layout = lyt_parent
        self.report_cb = report_cb
        
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.setObjectName("vertical_layout_" + obj_name)
        
        self.ftr_label = QtWidgets.QLabel(self.parent)
        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftr_label.sizePolicy().hasHeightForWidth())
        
        self.ftr_label.setSizePolicy(sizePolicy)
        self.ftr_label.setObjectName("ftr_label_" + obj_name)
        
        # add label into vertical layout
        self.vertical_layout.addWidget(self.ftr_label)
        
        self.slr_h_feature = QtWidgets.QSlider(self.parent)
        self.slr_h_feature.setOrientation(QtCore.Qt.Horizontal)
        self.slr_h_feature.setObjectName(obj_name)
        self.slr_h_feature.valueChanged.connect(self.ValueChanged)
        self.slr_h_feature.setRange(0, 100)
        
        self.vertical_layout.addWidget(self.slr_h_feature)
        self.parent_layout.addLayout(self.vertical_layout)
    
    def SetValue(self, curr_value):
        self.value = curr_value * 100
        self.slr_h_feature.setValue(self.value)
    
    def SetText(self, text):
        self.text = text
        
    def UpdateLabel(self, translate):
        self.ftr_label.setText(translate("MainWindow", self.text))
        
    # valueChanged Qt Signal connected from QSlider
    def ValueChanged(self, value):
        self.value = value
        self.report_cb(self.obj_name, self.value * 0.01)