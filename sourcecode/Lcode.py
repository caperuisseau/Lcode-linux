#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, json
from pathlib import Path
from PyQt5.QtCore import Qt, QSize, QRegExp
from PyQt5.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QTabWidget, QTextEdit,
    QToolBar, QStatusBar, QLabel, QPlainTextEdit, QWidget, QAction,
    QDialog, QListWidget, QVBoxLayout
)

LANG = "fr"
TR = {}

class CHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        self.rules = []
        self.init_formats()
        self.init_rules()

    def fmt(self, color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold: f.setFontWeight(QFont.Bold)
        f.setFontItalic(italic)
        return f

    def init_formats(self):
        self.keywordFmt = self.fmt('#d19a66', bold=True)
        self.typeFmt = self.fmt('#61afef')
        self.numFmt = self.fmt('#d19a66')
        self.strFmt = self.fmt('#98c379')
        self.commentFmt = self.fmt('#7f8c8d', italic=True)
        self.preFmt = self.fmt('#c678dd')

    def init_rules(self):
        kws = ['if','else','for','while','do','switch','case','break','continue','return','goto','sizeof','struct','union','enum','typedef','static','const','volatile','extern','register','inline','restrict']
        types = ['int','long','short','char','float','double','void','signed','unsigned','bool']
        for w in kws:
            self.rules.append((QRegExp(f'\\b{w}\\b'), self.keywordFmt))
        for t in types:
            self.rules.append((QRegExp(f'\\b{t}\\b'), self.typeFmt))
        self.rules.append((QRegExp(r'\\b[0-9]+(\\.[0-9]+)?\\b'), self.numFmt))
        self.rules.append((QRegExp(r'".*"'), self.strFmt))
        self.rules.append((QRegExp(r"'.*'"), self.strFmt))
        self.rules.append((QRegExp(r'^\\s*#.*'), self.preFmt))
        self.rules.append((QRegExp(r'//.*'), self.commentFmt))

    def highlightBlock(self, text):
        for pat, fmt in self.rules:
            i = pat.indexIn(text)
            while i >= 0:
                l = pat.matchedLength()
                self.setFormat(i, l, fmt)
                i = pat.indexIn(text, i + l)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.setFont(QFont('Menlo',12))
        self.setTabStopDistance(self.fontMetrics().width(' ')*4)
        self.setStyleSheet('background:#1e1e1e;color:#d4d4d4;border:none;')
        self.highlighter = CHighlighter(self.document())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Xcode 0.3')
        self.resize(1200,800)
        self.setupUI()

    def setupUI(self):
        self.setStyleSheet('''
            QMainWindow{background:#1e1e1e;}
            QTabWidget::pane{border:1px solid #3c3c3c;}
            QTabBar::tab{background:#2d2d2d;color:#d4d4d4;padding:5px;}
            QTabBar::tab:selected{background:#3c3c3c;}
            QToolBar{background:#2d2d2d;border:none;}
            QStatusBar{background:#2d2d2d;color:#d4d4d4;}
            QTextEdit{background:#1e1e1e;color:#d4d4d4;}
        ''')

        c = QWidget()
        l = QVBoxLayout(c)
        self.setCentralWidget(c)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        l.addWidget(self.tabs)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(220)
        l.addWidget(self.console)

        tb = QToolBar('Main')
        tb.setIconSize(QSize(18,18))
        self.addToolBar(tb)

        sb = QStatusBar()
        self.setStatusBar(sb)
        self.cursorLabel = QLabel('Ln 1, Col 1')
        sb.addPermanentWidget(self.cursorLabel)

        self.newAct = QAction('',self); self.newAct.triggered.connect(self.newFile); tb.addAction(self.newAct)
        self.openAct = QAction('',self); self.openAct.triggered.connect(self.openFile); tb.addAction(self.openAct)
        self.saveAct = QAction('',self); self.saveAct.triggered.connect(self.saveFile); tb.addAction(self.saveAct)
        self.runAct = QAction('',self); self.runAct.triggered.connect(self.buildRun); tb.addAction(self.runAct)

        self.changeLangAct = QAction('', self)
        self.changeLangAct.triggered.connect(self.openLanguageDialog)
        tb.addAction(self.changeLangAct)

        self.applyLanguage()
        self.newFile()

    def applyLanguage(self):
        tr = TR.get(LANG, {})
        en = TR.get('en', {})

        self.newAct.setText(tr.get('new', en.get('new', 'New')))
        self.openAct.setText(tr.get('open', en.get('open', 'Open')))
        self.saveAct.setText(tr.get('save', en.get('save', 'Save')))
        self.runAct.setText(tr.get('run', en.get('run', 'Build & Run')))
        self.changeLangAct.setText(tr.get('change_language', en.get('change_language', 'Change Language')))

        for i in range(self.tabs.count()):
            name = self.tabs.tabText(i)
            untitled_candidates = {v.get('untitled') for v in TR.values() if isinstance(v, dict)}
            if name in untitled_candidates:
                self.tabs.setTabText(i, tr.get('untitled', en.get('untitled', 'untitled')))

    def openLanguageDialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(TR.get(LANG, {}).get('select_language', TR.get('en', {}).get('select_language', 'Select Language')))

        lst = QListWidget(dlg)
        for key, val in TR.items():
            display = key
            if isinstance(val, dict) and 'name' in val:
                display = f"{key} — {val['name']}"
            lst.addItem(display)

        def on_double(item):
            code = item.text().split(' — ')[0]
            self.setLanguage(code, dlg)

        lst.itemDoubleClicked.connect(on_double)

        layout = QVBoxLayout(dlg)
        layout.addWidget(lst)
        dlg.setLayout(layout)

        dlg.exec_()
        #pooping is my favorite time on my day

    def setLanguage(self, lang, dlg):
        global LANG
        if lang in TR:
            LANG = lang
        else:
            LANG = 'en'
        dlg.close()
        self.applyLanguage()

    def currentEditor(self):
        return self.tabs.currentWidget()

    def newFile(self):
        e = CodeEditor()
        self.tabs.addTab(e, TR.get(LANG, {}).get('untitled', TR.get('en', {}).get('untitled', 'untitled')))
        self.tabs.setCurrentWidget(e)

    def openFile(self):
        path, _ = QFileDialog.getOpenFileName(self, TR.get(LANG, {}).get('open_file', TR.get('en', {}).get('open_file', 'Open File')), '', 'C Files (*.c);;All Files (*)')
        if path:
            e = CodeEditor()
            with open(path,'r',encoding='utf-8') as f:
                e.setPlainText(f.read())
            e.file_path = path
            self.tabs.addTab(e, Path(path).name)
            self.tabs.setCurrentWidget(e)

    def saveFile(self):
        e = self.currentEditor()
        if not e:
            return
        if not getattr(e, 'file_path', None):
            path, _ = QFileDialog.getSaveFileName(self, TR.get(LANG, {}).get('save_file', TR.get('en', {}).get('save_file', 'Save File')), '', 'C Files (*.c);;All Files (*)')
            if not path:
                return
            e.file_path = path
            self.tabs.setTabText(self.tabs.currentIndex(), Path(path).name)
        with open(e.file_path, 'w', encoding='utf-8') as f:
            f.write(e.toPlainText())

    def buildRun(self):
        e = self.currentEditor()
        if not e:
            return
        if not getattr(e, 'file_path', None):
            self.saveFile()
        src = getattr(e, 'file_path', None)
        if not src:
            return
        exe = str(Path(src).with_suffix(''))
        os.system(f"gcc '{src}' -o '{exe}'")
        if os.path.exists(exe):
            self.console.append(f"Running: {exe}\n")
            # try common terminal emulators in order
            for term in ("x-terminal-emulator", "gnome-terminal", "konsole", "xterm"):
                if os.system(f"which {term} > /dev/null 2>&1") == 0:
                    os.system(f"{term} -e '{exe}' &")
                    break

    def closeTab(self, index):
        self.tabs.removeTab(index)


def main():
    global TR
    try:
        with open('language.json','r',encoding='utf-8') as f:
            TR = json.load(f)
    except Exception:
        TR = {
            'en': {
                'new': 'New', 'open': 'Open', 'save': 'Save', 'run': 'Build & Run',
                'untitled': 'untitled', 'open_file': 'Open File', 'save_file': 'Save File',
                'change_language': 'Change Language', 'select_language': 'Select Language'
            }
        }

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
