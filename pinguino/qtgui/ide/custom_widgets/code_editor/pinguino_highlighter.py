#! /usr/bin/python
#-*- coding: utf-8 -*-

#import pickle
#import sys
#import re
#import os
#from ConfigParser import RawConfigParser

from PySide6 import QtGui, QtCore, QtWidgets

from .syntax import Autocompleter

########################################################################
class Highlighter(QtGui.QSyntaxHighlighter):

    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    def __init__(self, parent, is_dark=False):
        super(Highlighter, self).__init__(parent)
        self.set_theme(is_dark)

    #----------------------------------------------------------------------
    def set_theme(self, is_dark=False):
        color = QtGui.QColor

        self.highlightingRules = []
        self.highlightingRulesMatch = []

        if is_dark:
            # High-contrast colors for dark background
            kw_color = "#569CD6"       # Light blue
            dot_color = "#4EC9B0"      # Teal / Cyan
            num_color = "#B5CEA8"      # Light green
            op_color = "#D4D4D4"       # Light gray
            str_color = "#CE9178"      # Warm orange/peach
            str_single = "#CE9178"
            dir_color = "#C586C0"      # Soft magenta
            comment_color = "#6A9955"  # Light green
            multi_comment_color = "#6A9955"
        else:
            # Classic colors for light background
            kw_color = "#0000FF"       # Blue
            dot_color = "#0000FF"
            num_color = "#FF0000"      # Red
            op_color = "#000000"
            str_color = "#7F0000"      # Dark red
            str_single = "#CC0000"
            dir_color = "#D36820"      # Orange
            comment_color = "#007F00"  # Green
            multi_comment_color = "#C81818"

        reservadas = QtGui.QTextCharFormat()
        reservadas.setForeground(color(kw_color))
        all_reservadas = Autocompleter["reserved"] + Autocompleter["directive"]
        self.highlightingRules.append((r"\b("+"|".join(all_reservadas)+r")\b", reservadas))

        dotFuntions = QtGui.QTextCharFormat()
        dotFuntions.setForeground(color(dot_color))
        self.highlightingRules.append((r"\b[\D][\w]*\.[\D][\w]*", dotFuntions))

        decimal = QtGui.QTextCharFormat()
        decimal.setForeground(color(num_color))
        self.highlightingRules.append((r"\b[\d]+\b", decimal))

        float_ = QtGui.QTextCharFormat()
        float_.setForeground(color(num_color))
        self.highlightingRules.append((r"\b[\d]+\.[\d]+\b", float_))

        hexa = QtGui.QTextCharFormat()
        hexa.setForeground(color(num_color))
        self.highlightingRules.append((r"\b0[Xx][A-Fa-f\d]+\b", hexa))

        operators = QtGui.QTextCharFormat()
        operators.setForeground(color(op_color))
        operators.setFontWeight(QtGui.QFont.Bold)
        self.highlightingRules.append((r"[()\[\]{}<>=\-\+\*\\%#!~&^,]", operators))

        bin_ = QtGui.QTextCharFormat()
        bin_.setForeground(color(num_color))
        self.highlightingRules.append((r"\b0[Bb][01]+\b", bin_))

        doubleQuotation = QtGui.QTextCharFormat()
        doubleQuotation.setForeground(color(str_color))
        self.highlightingRules.append((r'"[^"\\]*(\\.[^"\\]*)*"', doubleQuotation))

        singleQuotation = QtGui.QTextCharFormat()
        singleQuotation.setForeground(color(str_single))
        self.highlightingRules.append((r"'[^'\\]*(\\.[^'\\]*)*'", singleQuotation))

        directives = QtGui.QTextCharFormat()
        directives.setForeground(color(dir_color))
        self.highlightingRules.append(("#[ ]*[define|include|ifndef|endif|pragma][ ]*.*", directives))

        singleComment = QtGui.QTextCharFormat()
        singleComment.setForeground(color(comment_color))
        self.highlightingRules.append((r'//[^\n]*', singleComment))

        self.multiComment = QtGui.QTextCharFormat()
        self.multiComment.setForeground(color(multi_comment_color))

        self.commentStartExpression = QtCore.QRegularExpression(r"/\*")
        self.commentEndExpression = QtCore.QRegularExpression(r"\*/")
        self.rehighlight()

    #----------------------------------------------------------------------
    def highlightBlock(self, text):
        for pattern, format_ in self.highlightingRules:
            if isinstance(pattern, QtCore.QRegularExpression):
                expression = pattern
            else:
                expression = QtCore.QRegularExpression(pattern)
            iterator = expression.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_)

        #for pattern, format in self.highlightingRulesMatch:
            #expression = QtCore.QRegExp(pattern)
            ##index  =  expression.indexIn(text)
            #print expression.capturedTexts()

            #while index >= 0:
                #length = expression.matchedLength()
                #self.setFormat(index, length, format)
                #index = expression.indexIn(text, index + length)

        self.buildComment(self.commentStartExpression,
                          self.commentEndExpression,
                          self.multiComment,
                          text)

    #----------------------------------------------------------------------
    def buildComment(self, start, end, format_, text):
        self.setCurrentBlockState(0)
        startIndex = -1
        if self.previousBlockState() != 1:
            match_start = start.match(text)
            if match_start.hasMatch():
                startIndex = match_start.capturedStart()
        else:
            startIndex = 0

        while startIndex >= 0 and startIndex < len(text):
            match_end = end.match(text, startIndex)
            if not match_end.hasMatch():
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
                self.setFormat(startIndex, commentLength, format_)
                break
            else:
                endIndex = match_end.capturedStart()
                commentLength = endIndex - startIndex + match_end.capturedLength()
                self.setFormat(startIndex, commentLength, format_)
                # Find next comment start after the end of this comment block
                match_start = start.match(text, startIndex + commentLength)
                if match_start.hasMatch():
                    startIndex = match_start.capturedStart()
                else:
                    startIndex = -1

    #----------------------------------------------------------------------
    def addWord(self, word, tipo):
        color = QtGui.QColor
        newWord = QtGui.QTextCharFormat()
        newWord.setForeground(color(*self.fontsTypes(tipo)[0][:3]))
        if self.fontsTypes(tipo)[1]: newWord.setFontWeight(QtGui.QFont.Bold)
        newWord.setFontItalic(self.fontsTypes(tipo)[2])
        self.highlightingRules.insert(0, (QtCore.QRegularExpression(word), newWord))

    #----------------------------------------------------------------------
    def removeWord(self, word):
        self.highlightingRules.append((QtCore.QRegularExpression(word), QtGui.QTextCharFormat()))
