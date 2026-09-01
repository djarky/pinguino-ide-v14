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
    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        color = QtGui.QColor

        self.highlightingRules = []
        self.highlightingRulesMatch = []

        reservadas = QtGui.QTextCharFormat()
        reservadas.setForeground(color("#0000ff"))
        all_reservadas = Autocompleter["reserved"] + Autocompleter["directive"]
        #namespaces = pickle.load(open(os.path.join(os.getenv("PINGUINO_USER_PATH"), "reserved.pickle"), "r"))
        #namespaces = filter(lambda s:not "." in s, namespaces["all"])
        #all_reservadas += namespaces
        self.highlightingRules.append((r"\b("+"|".join(all_reservadas)+r")\b", reservadas))

        dotFuntions = QtGui.QTextCharFormat()
        dotFuntions.setForeground(color("#0000ff"))
        self.highlightingRules.append((r"\b[\D][\w]*\.[\D][\w]*", dotFuntions))

        decimal = QtGui.QTextCharFormat()
        decimal.setForeground(color("#ff0000"))
        self.highlightingRules.append((r"\b[\d]+\b", decimal))

        float_ = QtGui.QTextCharFormat()
        float_.setForeground(color("#ff0000"))
        self.highlightingRules.append((r"\b[\d]+\.[\d]+\b", float_))

        hexa = QtGui.QTextCharFormat()
        hexa.setForeground(color("#ff0000"))
        self.highlightingRules.append((r"\b0[Xx][A-Fa-f\d]+\b", hexa))

        operators = QtGui.QTextCharFormat()
        operators.setFontWeight(QtGui.QFont.Bold)
        self.highlightingRules.append((r"[()\[\]{}<>=\-\+\*\\%#!~&^,]", operators))

        bin_ = QtGui.QTextCharFormat()
        bin_.setForeground(color("#ff0000"))
        self.highlightingRules.append((r"\b0[Bb][01]+\b", bin_))

        doubleQuotation = QtGui.QTextCharFormat()
        doubleQuotation.setForeground(color("#7f0000"))
        self.highlightingRules.append((r'"[^"\\]*(\\.[^"\\]*)*"', doubleQuotation))

        singleQuotation = QtGui.QTextCharFormat()
        singleQuotation.setForeground(color("#cc0000"))
        self.highlightingRules.append((r"'[^'\\]*(\\.[^'\\]*)*'", singleQuotation))

        directives = QtGui.QTextCharFormat()
        directives.setForeground(color("#d36820"))
        self.highlightingRules.append(("#[ ]*[define|include|ifndef|endif|pragma][ ]*.*", directives))

        singleComment = QtGui.QTextCharFormat()
        singleComment.setForeground(color("#007F00"))
        self.highlightingRules.append((r'//[^\n]*', singleComment))

        self.multiComment = QtGui.QTextCharFormat()
        self.multiComment.setForeground(color("#c81818"))

        self.commentStartExpression = QtCore.QRegularExpression(r"/\*")
        self.commentEndExpression = QtCore.QRegularExpression(r"\*/")

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
