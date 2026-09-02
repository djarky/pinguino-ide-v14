#! /usr/bin/python
#-*- coding: utf-8 -*-

import os
import re

from PySide6 import QtCore, QtGui, QtWidgets

from .autocompleter import PinguinoAutoCompleter
from .pinguino_highlighter import Highlighter
from .line_number import LineNumber


def is_color_dark(color):
    qcol = QtGui.QColor(color)
    if not qcol.isValid():
        return False
    luminance = (0.299 * qcol.red() + 0.587 * qcol.green() + 0.114 * qcol.blue())
    return luminance < 128


########################################################################
class CustomTextEdit(QtWidgets.QPlainTextEdit):

    #----------------------------------------------------------------------
    def __init__(self, parent=None, line_number=None, highlighter=None):
        super(CustomTextEdit, self).__init__(parent)

        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)

        self.last_saved = ""
        self.path = None
        self.helpers = {}
        self.next_ignore = None

        self.completer = PinguinoAutoCompleter(self)
        if highlighter is False:
            self.highlighter = None
        elif isinstance(highlighter, Highlighter):
            self.highlighter = highlighter
        else:
            self.highlighter = Highlighter(self.document())

        self.line_number = line_number if line_number is not None else LineNumber(self)
        self.line_number.setTextEdit(self)

        self.updateRequest.connect(self.update_line_number)
        self.cursorPositionChanged.connect(self.line_number.update)

        self.apply_theme()

    #----------------------------------------------------------------------
    def apply_theme(self):
        bg_color = None
        text_color = None
        try:
            from pinguino.qtgui.pinguino_core.config import Config
            config = Config()
            if config.has_section("Styles"):
                if config.has_option("Styles", "editor_background_color"):
                    val = config.get("Styles", "editor_background_color")
                    if val and val.lower() != "none":
                        bg_color = val
                if config.has_option("Styles", "editor_text_color"):
                    val = config.get("Styles", "editor_text_color")
                    if val and val.lower() != "none":
                        text_color = val
                if not bg_color and config.has_option("Styles", "background_color"):
                    val = config.get("Styles", "background_color")
                    if val and val.lower() != "none":
                        bg_color = val
        except Exception:
            pass

        if not bg_color:
            bg_color = "#FFFFFF"

        is_dark = is_color_dark(bg_color)
        if not text_color:
            text_color = "#D4D4D4" if is_dark else "#000000"

        sel_bg = "#264F78" if is_dark else "#57AAFF"
        sel_fg = "#FFFFFF"

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                selection-background-color: {sel_bg};
                selection-color: {sel_fg};
            }}
        """)

        if self.highlighter and hasattr(self.highlighter, "set_theme"):
            self.highlighter.set_theme(is_dark)

        if self.line_number and hasattr(self.line_number, "set_theme"):
            self.line_number.set_theme(is_dark, bg_color, text_color)

        parent_editor = self.parent()
        if parent_editor and hasattr(parent_editor, "update_theme"):
            parent_editor.update_theme(is_dark)


    #----------------------------------------------------------------------
    def set_autocompleter(self, autocompleter):
        if callable(autocompleter):
            self.completer = autocompleter(self)
        else:
            self.completer = autocompleter


    #----------------------------------------------------------------------
    def update_line_number(self, rect, dy):
        if dy:
            self.line_number.scroll(0, dy)
        else:
            self.line_number.update(0, rect.y(), self.line_number.width(), rect.height())


    #----------------------------------------------------------------------
    def resizeEvent(self, event):
        super(CustomTextEdit, self).resizeEvent(event)
        cr = self.contentsRect()
        self.line_number.setGeometry(QtCore.QRect(cr.left(), cr.top(), 51, cr.height()))


    #----------------------------------------------------------------------
    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
        else:
            super(CustomTextEdit, self).wheelEvent(event)


    #----------------------------------------------------------------------
    def insert(self, completion):

        tc = self.textCursor()

        Snippet = self.completer.snippet
        Helpers = self.completer.helper

        self.temp_helpers = self.helpers.copy()
        self.temp_helpers.update(Helpers)
        self.temp_helpers.update(self.completer.local_functions)

        pos = tc.position()
        tc.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        at_right = tc.selectedText()
        tc.setPosition(pos, QtGui.QTextCursor.MoveAnchor)

        if completion in self.temp_helpers.keys() and not at_right:
            pos = tc.position()

            # text_position = Snippet[completion].find("[!]")
            text_insert = self.temp_helpers[completion].replace("{{", "").replace("}}", "")
            position_in_line = tc.positionInBlock()

            start_position = self.temp_helpers[completion].find("{{")
            end_position = self.temp_helpers[completion].find("}}")

            tc.insertText(text_insert.replace("\n", "\n"+" "*position_in_line))
            tc.setPosition(pos + start_position)

            select = self.temp_helpers[completion][(start_position + 2):end_position]
            tc.beginEditBlock()
            self.moveCursor(QtGui.QTextCursor.StartOfLine)
            self.find(select)
            tc.endEditBlock()


        elif completion in Snippet.keys():
            pos = tc.position()

            text_insert = Snippet[completion].replace("{{", "").replace("}}", "")
            position_in_line = tc.positionInBlock()

            start_position = Snippet[completion].find("{{")
            end_position = Snippet[completion].find("}}")

            tc.insertText(text_insert.replace("\n", "\n"+" "*position_in_line))
            tc.setPosition(pos + start_position)

            select = Snippet[completion][(start_position + 2):end_position]
            tc.beginEditBlock()
            self.moveCursor(QtGui.QTextCursor.StartOfLine)
            self.find(select)
            tc.endEditBlock()

        else:
            tc.insertText(completion)

        self.smart_under_selection(tc)
        self.setTextCursor(tc)


    #----------------------------------------------------------------------
    def set_autocomplete(self, words):
        self.completer.set_words(words)


    #----------------------------------------------------------------------
    def keyPressEvent(self, event):
        self.__keyPressEvent__(event)


    #----------------------------------------------------------------------
    def __keyPressEvent__(self, event):

        key = event.text()

        if self.completer.popup().isVisible():
            if event.key() in [QtCore.Qt.Key_Enter,
                                QtCore.Qt.Key_Return,
                                QtCore.Qt.Key_Escape,
                                QtCore.Qt.Key_Tab,
                                QtCore.Qt.Key_Backtab]:
                event.ignore()
                return

        if event.key() == QtCore.Qt.Key_Tab:
            tc = self.textCursor()
            if tc.hasSelection():
                text = tc.selectedText()
                lines = text.split("\u2029")
                new_lines = ["    " + line for line in lines]
                tc.insertText("\u2029".join(new_lines))
                return
            else:
                tc.insertText("    ")
                return

        if event.key() == QtCore.Qt.Key_Backtab:
            tc = self.textCursor()
            if tc.hasSelection():
                text = tc.selectedText()
                lines = text.split("\u2029")
                new_lines = []
                for line in lines:
                    if line.startswith("    "):
                        new_lines.append(line[4:])
                    elif line.startswith("\t"):
                        new_lines.append(line[1:])
                    else:
                        new_lines.append(line)
                tc.insertText("\u2029".join(new_lines))
                return

        if key in ["\"", "'", "(", "[", "{"]:
            tc = self.textCursor()

            if self.next_ignore == key:
                self.next_ignore = None
                tc.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor)
                self.setTextCursor(tc)
                return

            def accept(insert):
                selected = tc.selectedText()
                tc.insertText(key + selected + insert)
                tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor)
                tc.setPosition(tc.position()-len(selected), QtGui.QTextCursor.MoveAnchor)
                tc.setPosition(tc.position()+len(selected), QtGui.QTextCursor.KeepAnchor)
                return tc

            if key == "[":
                self.next_ignore = "]"
                return accept("]")

            elif key == "{":
                self.next_ignore = "}"
                return accept("}")

            elif key == "(":
                self.next_ignore = ")"
                return accept(")")

            elif key == "\"":
                if self.get_format() not in ["comment", "quotation"]:
                    self.next_ignore = "\""
                    return accept("\"")

            elif key == "'":
                if self.get_format() not in ["comment", "quotation"]:
                    self.next_ignore = "'"
                    return accept("'")

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Enter-1]:
            tc = self.textCursor()
            pos = tc.position()
            tc.select(QtGui.QTextCursor.LineUnderCursor)
            line = tc.selectedText()
            comment = ""
            if line.isspace() or line == "":
                len_s = len(line)
            else:
                normal = line.replace(" ", "")
                #if normal.startswith("//"):
                    #comment = "//"
                len_s = line.find(normal[0])

            tc.setPosition(pos)
            tc.insertText("\n"+" "*len_s+comment)
            return

        super(CustomTextEdit, self).keyPressEvent(event)

        self.show_autocomplete_if_conditions()



    #----------------------------------------------------------------------

    def smart_under_selection(self, tc):
        #word like: cdc|
        tc.movePosition(QtGui.QTextCursor.WordLeft, QtGui.QTextCursor.KeepAnchor)

        #word like: cdc.|
        if tc.selectedText().startswith("."): tc.movePosition(QtGui.QTextCursor.WordLeft, QtGui.QTextCursor.KeepAnchor)

        #word like: cdc.pri|
        tc.movePosition(QtGui.QTextCursor.WordLeft, QtGui.QTextCursor.KeepAnchor)
        if tc.selectedText().startswith("."): tc.movePosition(QtGui.QTextCursor.WordLeft, QtGui.QTextCursor.KeepAnchor)
        else: tc.movePosition(QtGui.QTextCursor.WordRight, QtGui.QTextCursor.KeepAnchor)


    #----------------------------------------------------------------------
    def show_autocomplete_if_conditions(self):
        """"""

        tc = self.textCursor()

        if self.get_format() in ["comment", "quotation"]:
            return

        pos = tc.positionInBlock()
        block = tc.block()
        text = block.text()[:pos]

        if not text.strip():
            return

        word = re.split(r"[\s\(\)\[\]{},;]", text)[-1]

        if len(word) >= 2:
            rect = self.cursorRect()
            pos = self.mapToGlobal(rect.bottomLeft())
            self.completer.popup(pos, word)
        else:
            self.completer.hide()


    #----------------------------------------------------------------------
    def get_format(self):

        contex_color = {"#7f0000": "quotation",
                        "#cc0000": "quotation",
                        "#ce9178": "quotation",
                        "#007f00": "comment",
                        "#c81818": "comment",
                        "#6a9955": "comment"}

        tc = self.textCursor()
        pos = tc.positionInBlock()

        block = tc.block()
        layout = block.layout()
        formats = layout.formats()

        for format_ in formats:
            if pos >= format_.start and pos <= format_.start + format_.length:
                return contex_color.get(format_.format.foreground().color().name().lower(), None)


    #----------------------------------------------------------------------
    def brace_match(self):
        pass

    #----------------------------------------------------------------------
    def setAcceptRichText(self, accept=False):
        pass
