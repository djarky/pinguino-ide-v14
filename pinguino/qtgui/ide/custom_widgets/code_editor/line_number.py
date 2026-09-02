#! /usr/bin/python
#-*- coding: utf-8 -*-

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter

#from ..methods.backgrounds import BackgroundPallete

class LineNumber(QWidget):

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(LineNumber, self).__init__(*args, **kwargs)

        self.edit = None
        self.highest_line = 0
        self.current = 0
        self.is_dark = False
        self.bg_color = QtGui.QColor("#E0E0E0")
        self.text_color = QtGui.QColor("#555555")
        self.active_text_color = QtGui.QColor("#000000")

        self.setMinimumSize(QtCore.QSize(51, 0))
        self.setMaximumSize(QtCore.QSize(51, 16777215))

        self.setStyleSheet("""
        font-family: mono;
        font-weight: normal;
        font-size: 10pt;
        """)

    #----------------------------------------------------------------------
    def set_theme(self, is_dark=False, bg_color=None, text_color=None):
        self.is_dark = is_dark
        if is_dark:
            self.bg_color = QtGui.QColor("#252526")
            self.text_color = QtGui.QColor("#858585")
            self.active_text_color = QtGui.QColor("#C6C6C6")
        else:
            self.bg_color = QtGui.QColor("#E0E0E0")
            self.text_color = QtGui.QColor("#555555")
            self.active_text_color = QtGui.QColor("#000000")

        palette = QtGui.QPalette(self.palette())
        self.setAutoFillBackground(True)
        palette.setColor(QtGui.QPalette.Window, self.bg_color)
        self.setPalette(palette)
        self.update()

    #----------------------------------------------------------------------
    def setTextEdit(self, edit):
        self.edit = edit

    #----------------------------------------------------------------------
    def update(self, *args):
        QWidget.update(self, *args)

    #----------------------------------------------------------------------
    def paintEvent(self, event):
        if not self.edit:
            return QWidget.paintEvent(self, event)

        contents_y = self.edit.verticalScrollBar().value()
        page_bottom = contents_y + self.edit.viewport().height()
        font_metrics = self.fontMetrics()
        current_block = self.edit.document().findBlock(self.edit.textCursor().position())
        painter = QPainter(self)
        
        # Fill background
        painter.fillRect(event.rect(), self.bg_color)

        line_count = 0
        block = self.edit.document().begin()
        while block.isValid():
            line_count += 1
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
            if position.y() > page_bottom:
                break
            bold = False
            if block == current_block:
                bold = True
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                painter.setPen(self.active_text_color)
                self.current = line_count
            else:
                painter.setPen(self.text_color)

            painter.drawText(self.width() - font_metrics.horizontalAdvance(str(line_count)) - 10,
                             round(position.y()) - contents_y + font_metrics.ascent(),
                             str(line_count))
            if bold:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)
            block = block.next()
        self.highest_line = line_count
        painter.end()

        QWidget.paintEvent(self, event)
