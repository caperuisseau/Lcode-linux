import sys, os, json, subprocess
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QRegularExpression, QRect, QThread, pyqtSignal
from PyQt6.QtGui import (
    QColor, QFont, QTextCharFormat, QSyntaxHighlighter,
    QKeySequence, QPainter, QAction, QShortcut, QFileSystemModel
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QStatusBar, QLabel, QPlainTextEdit,
    QWidget, QMessageBox, QLineEdit, QSplitter, QTreeView,
    QStyleFactory, QFrame, QPushButton, QDialog
)


GLOBAL_QSS = """

* {
    font-family: "Inter", "SF Pro Display", "Segoe UI", "Helvetica Neue", sans-serif;
}

QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1b26, stop:1 #16161e);
}

QMenuBar {
    background: transparent;
    color: #a9b1d6;
    border: none;
    padding: 4px 8px;
    font-size: 13px;
    font-weight: 500;
    spacing: 2px;
}
QMenuBar::item {
    padding: 6px 14px;
    border-radius: 6px;
    background: transparent;
}
QMenuBar::item:selected {
    background: rgba(122, 162, 247, 0.15);
    color: #7aa2f7;
}
QMenu {
    background: #1f2029;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 6px;
    color: #a9b1d6;
}
QMenu::item {
    padding: 8px 28px 8px 16px;
    border-radius: 6px;
    font-size: 13px;
}
QMenu::item:selected {
    background: rgba(122, 162, 247, 0.18);
    color: #c0caf5;
}
QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.05);
    margin: 4px 12px;
}

QSplitter {
    background: #1a1b26;
}
QSplitter::handle {
    background: #12121a;
    width: 1px;
}

QTreeView {
    background: #16161e;
    border: none;
    color: #787c99;
    font-size: 12px;
    font-family: "Inter", "SF Pro Text", sans-serif;
    outline: 0;
    padding-top: 6px;
    show-decoration-selected: 1;
}
QTreeView::item {
    padding: 5px 8px;
    border-radius: 5px;
    margin: 0px 6px;
}
QTreeView::item:hover {
    background: rgba(122, 162, 247, 0.06);
    color: #9aa5ce;
}
QTreeView::item:selected {
    background: rgba(122, 162, 247, 0.14);
    color: #c0caf5;
}
QTreeView::branch {
    background: transparent;
}
QTreeView::branch:has-siblings:!adjoins-item {
    border-image: none;
}
QTreeView::branch:has-siblings:adjoins-item {
    border-image: none;
}
QTreeView::branch:!has-children:!has-siblings:adjoins-item {
    border-image: none;
}
QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {
    image: none;
    border-image: none;
}
QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings {
    image: none;
    border-image: none;
}

QTabWidget {
    background: transparent;
}
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabWidget::tab-bar {
    alignment: left;
}
QTabBar {
    background: #16161e;
    qproperty-drawBase: 0;
}
QTabBar::tab {
    background: transparent;
    color: #565f89;
    padding: 10px 24px;
    margin: 0;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
    font-weight: 500;
    min-width: 100px;
}
QTabBar::tab:selected {
    color: #c0caf5;
    border-bottom: 2px solid #7aa2f7;
    background: rgba(122, 162, 247, 0.05);
}
QTabBar::tab:hover:!selected {
    color: #9aa5ce;
    background: rgba(255, 255, 255, 0.02);
}
QTabBar::close-button {
    image: none;
    subcontrol-position: right;
    padding: 4px;
}

QPlainTextEdit {
    background: #1a1b26;
    color: #a9b1d6;
    border: none;
    font-family: "JetBrains Mono", "Fira Code", "SF Mono", "Cascadia Code", "Consolas", monospace;
    font-size: 13px;
    selection-background-color: rgba(122, 162, 247, 0.2);
    selection-color: #c0caf5;
    padding: 8px 4px;
}

QStatusBar {
    background: #16161e;
    color: #565f89;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    font-size: 11px;
    padding: 2px 12px;
    min-height: 28px;
}
QStatusBar QLabel {
    color: #565f89;
    font-size: 11px;
    padding: 0 8px;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}
QScrollBar::handle:vertical {
    background: rgba(122, 162, 247, 0.15);
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(122, 162, 247, 0.3);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 2px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(122, 162, 247, 0.15);
    min-width: 30px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: rgba(122, 162, 247, 0.3);
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

QDialog {
    background: #1a1b26;
    color: #a9b1d6;
    border-radius: 12px;
}

QLineEdit {
    background: #16161e;
    color: #a9b1d6;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: rgba(122, 162, 247, 0.25);
}
QLineEdit:focus {
    border: 1px solid rgba(122, 162, 247, 0.5);
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7aa2f7, stop:1 #5d7de0);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #89b0ff, stop:1 #6b8df0);
}
QPushButton:pressed {
    background: #4c6abf;
}

QTextEdit {
    background: #16161e;
    color: #9ece6a;
    border: none;
    border-radius: 8px;
    padding: 10px;
    font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 12px;
    selection-background-color: rgba(158, 206, 106, 0.2);
}

QToolTip {
    background: #1f2029;
    color: #a9b1d6;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

QMessageBox {
    background: #1a1b26;
}
QMessageBox QLabel {
    color: #a9b1d6;
    font-size: 13px;
}
"""


class _RunWorker(QThread):
    output = pyqtSignal(str, str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            r = subprocess.run(self.cmd, capture_output=True, text=True, timeout=15)
            if r.stdout:
                self.output.emit(r.stdout.rstrip(), "#a9b1d6")
            if r.stderr:
                self.output.emit(r.stderr.rstrip(), "#f7768e")
            self.output.emit(f"Exit code: {r.returncode}", "#565f89")
        except subprocess.TimeoutExpired:
            self.output.emit("Timed out (15s)", "#e0af68")
        except Exception as ex:
            self.output.emit(str(ex), "#f7768e")


class Highlighter(QSyntaxHighlighter):

    def __init__(self, doc, lang='c'):
        super().__init__(doc)
        self.lang = lang
        self.rules = []
        self._ml_start = None
        self._ml_end = None
        self._ml_fmt = None
        self._build_formats()
        self._build_rules()

    def _make(self, color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Weight.Bold)
        f.setFontItalic(italic)
        return f

    def _build_formats(self):
        self.kw   = self._make('#bb9af7', bold=True)
        self.typ  = self._make('#2ac3de', bold=True)
        self.num  = self._make('#ff9e64')
        self.str  = self._make('#9ece6a')
        self.cmt  = self._make('#565f89', italic=True)
        self.pre  = self._make('#e0af68')
        self.func = self._make('#7aa2f7')
        self.cls  = self._make('#2ac3de', italic=True)
        self.self_fmt = self._make('#f7768e', italic=True)

    def _build_rules(self):
        self.rules = []

        self.rules.append((QRegularExpression(r'\b[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?\b'), self.num))
        self.rules.append((QRegularExpression(r'\b0[xX][0-9a-fA-F]+\b'), self.num))
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.str))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.str))

        if self.lang == 'python':
            for w in ['and','as','assert','async','await','break','class','continue',
                       'def','del','elif','else','except','finally','for','from',
                       'global','if','import','in','is','lambda','nonlocal','not',
                       'or','pass','raise','return','try','while','with','yield']:
                self.rules.append((QRegularExpression(rf'\b{w}\b'), self.kw))

            for b in ['True','False','None']:
                self.rules.append((QRegularExpression(rf'\b{b}\b'), self.typ))

            self.rules.append((QRegularExpression(r'\bself\b'), self.self_fmt))
            self.rules.append((QRegularExpression(r'#[^\n]*'), self.cmt))
            self.rules.append((QRegularExpression(r'\bdef\s+([A-Za-z_]\w*)'), self.func))
            self.rules.append((QRegularExpression(r'\bclass\s+([A-Za-z_]\w*)'), self.cls))
            self.rules.append((QRegularExpression(r'@[A-Za-z_][\w.]*'), self.pre))
            self.rules.append((QRegularExpression(r'\b[A-Za-z_]\w*(?=\s*\()'), self.func))

            self._ml_start = QRegularExpression(r'"""|\'\'\'')
            self._ml_end = QRegularExpression(r'"""|\'\'\'')
            self._ml_fmt = self.str

        else:
            for w in ['if','else','for','while','do','switch','case','break',
                       'continue','return','goto','sizeof','struct','union','enum',
                       'typedef','static','const','volatile','extern','register',
                       'inline','default','NULL','true','false','new','delete',
                       'class','public','private','protected','template','typename',
                       'namespace','using','virtual','override','final','noexcept',
                       'constexpr','auto','nullptr','static_cast','dynamic_cast',
                       'reinterpret_cast','const_cast','throw','catch','try']:
                self.rules.append((QRegularExpression(rf'\b{w}\b'), self.kw))

            for t in ['int','long','short','char','float','double','void','bool',
                       'size_t','uint8_t','uint16_t','uint32_t','uint64_t',
                       'int8_t','int16_t','int32_t','int64_t','unsigned','signed',
                       'wchar_t','char16_t','char32_t','ptrdiff_t','FILE']:
                self.rules.append((QRegularExpression(rf'\b{t}\b'), self.typ))

            self.rules.append((QRegularExpression(r'^\s*#\s*\w+'), self.pre))
            self.rules.append((QRegularExpression(r'//[^\n]*'), self.cmt))
            self.rules.append((QRegularExpression(r'\b[A-Za-z_]\w*(?=\s*\()'), self.func))

            self._ml_start = QRegularExpression(r'/\*')
            self._ml_end = QRegularExpression(r'\*/')
            self._ml_fmt = self.cmt

    def highlightBlock(self, text):
        for pat, fmt in self.rules:
            it = pat.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        if not self._ml_start:
            return

        self.setCurrentBlockState(0)
        offset = 2 if self.lang != 'python' else 3

        start = 0
        if self.previousBlockState() != 1:
            m = self._ml_start.match(text)
            start = m.capturedStart() if m.hasMatch() else -1

        while start >= 0:
            me = self._ml_end.match(text, start + offset)
            end = me.capturedStart() if me.hasMatch() else -1
            if end == -1:
                self.setCurrentBlockState(1)
                length = len(text) - start
            else:
                length = end - start + me.capturedLength()
            self.setFormat(start, length, self._ml_fmt)
            ms = self._ml_start.match(text, start + length)
            start = ms.capturedStart() if ms.hasMatch() else -1


class LineNumberArea(QWidget):

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.paintLineNumbers(event)


class CodeEditor(QPlainTextEdit):

    def __init__(self, path=None, parent=None):
        super().__init__(parent)
        self.file_path = path
        self._modified = False

        font = QFont("JetBrains Mono", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        lang = 'python' if path and str(path).endswith('.py') else 'c'
        self.highlighter = Highlighter(self.document(), lang)

        self.gutter = LineNumberArea(self)
        self.blockCountChanged.connect(self._updateGutterWidth)
        self.updateRequest.connect(self._updateGutter)
        self.cursorPositionChanged.connect(self._highlightLine)
        self._updateGutterWidth(0)
        self._highlightLine()

        self.document().modificationChanged.connect(self._onModified)

    def _onModified(self, m):
        self._modified = m
        w = self.window()
        if hasattr(w, '_syncTabTitle'):
            w._syncTabTitle(self)

    def lineNumberAreaWidth(self):
        digits = max(3, len(str(self.blockCount())))
        return 16 + self.fontMetrics().horizontalAdvance('9') * digits

    def _updateGutterWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def _updateGutter(self, rect, dy):
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._updateGutterWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.gutter.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def paintLineNumbers(self, event):
        painter = QPainter(self.gutter)
        painter.fillRect(event.rect(), QColor('#16161e'))

        block = self.firstVisibleBlock()
        num = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        current = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                if num == current:
                    painter.setPen(QColor('#c0caf5'))
                    f = QFont(self.font())
                    f.setBold(True)
                    painter.setFont(f)
                else:
                    painter.setPen(QColor('#3b3f58'))
                    painter.setFont(self.font())

                painter.drawText(
                    0, int(top),
                    self.gutter.width() - 12,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(num + 1)
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            num += 1

    def _highlightLine(self):
        if self.isReadOnly():
            return
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(QColor('#1e2030'))
        sel.format.setProperty(1, True)
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        self.setExtraSelections([sel])

    def keyPressEvent(self, event):
        pairs = {
            Qt.Key.Key_ParenLeft: ('(', ')'),
            Qt.Key.Key_BracketLeft: ('[', ']'),
            Qt.Key.Key_BraceLeft: ('{', '}'),
        }
        quotes = {Qt.Key.Key_QuoteDbl: '"', Qt.Key.Key_Apostrophe: "'"}

        if event.key() in pairs and not event.modifiers():
            o, c = pairs[event.key()]
            cur = self.textCursor()
            cur.insertText(o + c)
            cur.movePosition(cur.MoveOperation.Left)
            self.setTextCursor(cur)
            return

        if event.key() in quotes and not event.modifiers():
            q = quotes[event.key()]
            cur = self.textCursor()
            pos = cur.positionInBlock()
            txt = cur.block().text()
            if pos < len(txt) and txt[pos] == q:
                cur.movePosition(cur.MoveOperation.Right)
                self.setTextCursor(cur)
                return
            cur.insertText(q + q)
            cur.movePosition(cur.MoveOperation.Left)
            self.setTextCursor(cur)
            return

        closers = {')', ']', '}'}
        if event.text() in closers:
            cur = self.textCursor()
            pos = cur.positionInBlock()
            txt = cur.block().text()
            if pos < len(txt) and txt[pos] == event.text():
                cur.movePosition(cur.MoveOperation.Right)
                self.setTextCursor(cur)
                return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cur = self.textCursor()
            line = cur.block().text()
            indent = ''
            for ch in line:
                if ch in (' ', '\t'):
                    indent += ch
                else:
                    break
            stripped = line.rstrip()
            if stripped.endswith('{') or stripped.endswith(':'):
                indent += '    '
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        super().keyPressEvent(event)


class SearchBar(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.main = parent
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QWidget {
                background: #16161e;
                border-top: 1px solid rgba(255,255,255,0.04);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(8)

        self.field = QLineEdit()
        self.field.setPlaceholderText("Search...")
        self.field.setMinimumWidth(280)
        self.field.returnPressed.connect(self.findNext)
        layout.addWidget(self.field)

        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(32, 32)
        prev_btn.setStyleSheet("""
            QPushButton {
                background: rgba(122,162,247,0.1);
                border-radius: 6px;
                font-size: 11px;
                padding: 0;
            }
            QPushButton:hover { background: rgba(122,162,247,0.2); }
        """)
        prev_btn.clicked.connect(self.findPrev)
        layout.addWidget(prev_btn)

        next_btn = QPushButton("▶")
        next_btn.setFixedSize(32, 32)
        next_btn.setStyleSheet(prev_btn.styleSheet())
        next_btn.clicked.connect(self.findNext)
        layout.addWidget(next_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(247,118,142,0.1);
                border-radius: 6px;
                font-size: 12px;
                padding: 0;
                color: #f7768e;
            }
            QPushButton:hover { background: rgba(247,118,142,0.2); }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

        layout.addStretch()
        self.hide()

    def open(self):
        self.show()
        self.field.setFocus()
        self.field.selectAll()

    def findNext(self):
        editor = self.main.currentEditor()
        if not editor or not self.field.text():
            return
        if not editor.find(self.field.text()):
            c = editor.textCursor()
            c.movePosition(c.MoveOperation.Start)
            editor.setTextCursor(c)
            editor.find(self.field.text())

    def findPrev(self):
        from PyQt6.QtGui import QTextDocument
        editor = self.main.currentEditor()
        if not editor or not self.field.text():
            return
        if not editor.find(self.field.text(), QTextDocument.FindFlag.FindBackward):
            c = editor.textCursor()
            c.movePosition(c.MoveOperation.End)
            editor.setTextCursor(c)
            editor.find(self.field.text(), QTextDocument.FindFlag.FindBackward)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Lcode')
        self.resize(1400, 900)
        self._worker = None
        self._applyTheme()
        self._buildUI()
        self._buildMenus()

    def _applyTheme(self):
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        app.setStyleSheet(GLOBAL_QSS)

    def _buildUI(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        self.fsmodel = QFileSystemModel()
        root = str(Path(__file__).parent)
        self.fsmodel.setRootPath(root)

        self.tree = QTreeView()
        self.tree.setModel(self.fsmodel)
        self.tree.setRootIndex(self.fsmodel.index(root))
        for col in (1, 2, 3):
            self.tree.setColumnHidden(col, True)
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.doubleClicked.connect(self._openFromTree)
        self.splitter.addWidget(self.tree)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self._closeTab)
        self.tabs.currentChanged.connect(self._onTabChanged)
        right_layout.addWidget(self.tabs, stretch=3)

        self.searchBar = SearchBar(self)
        right_layout.addWidget(self.searchBar)

        console_wrap = QWidget()
        console_wrap.setStyleSheet("background: #16161e;")
        cl = QVBoxLayout(console_wrap)
        cl.setContentsMargins(12, 6, 12, 10)
        cl.setSpacing(4)

        header = QLabel("Console")
        header.setStyleSheet("""
            color: #565f89;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 4px 0;
        """)
        cl.addWidget(header)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(160)
        cl.addWidget(self.console)
        right_layout.addWidget(console_wrap)

        self.splitter.addWidget(right)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([240, 1160])

        self.statusBar().setStyleSheet(GLOBAL_QSS)
        self.cursorLabel = QLabel("Ln 1  Col 1")
        self.cursorLabel.setStyleSheet("color: #7aa2f7; font-weight: 600;")
        self.statusBar().addPermanentWidget(self.cursorLabel)

        self.encodingLabel = QLabel("UTF-8")
        self.statusBar().addPermanentWidget(self.encodingLabel)

    def _buildMenus(self):
        mb = self.menuBar()

        file_m = mb.addMenu("File")
        self._act(file_m, "New File", "Ctrl+N", self.newFile)
        self._act(file_m, "Open File…", "Ctrl+O", self._openFileDialog)
        self._act(file_m, "Open Folder…", "Ctrl+Shift+O", self._openFolder)
        file_m.addSeparator()
        self._act(file_m, "Save", "Ctrl+S", self.saveFile)
        self._act(file_m, "Save As…", "Ctrl+Shift+S", self._saveAs)
        file_m.addSeparator()
        self._act(file_m, "Quit", "Ctrl+Q", self.close)

        edit_m = mb.addMenu("Edit")
        self._act(edit_m, "Undo", "Ctrl+Z", lambda: self.currentEditor() and self.currentEditor().undo())
        self._act(edit_m, "Redo", "Ctrl+Y", lambda: self.currentEditor() and self.currentEditor().redo())
        edit_m.addSeparator()
        self._act(edit_m, "Find", "Ctrl+F", self.searchBar.open)
        self._act(edit_m, "Replace…", "Ctrl+H", self._openReplace)

        view_m = mb.addMenu("View")
        self._act(view_m, "Toggle Sidebar", "Ctrl+B", self._toggleSidebar)

        build_m = mb.addMenu("Build")
        self._act(build_m, "Build & Run", "Ctrl+Shift+B", self._buildRun)

    def _act(self, menu, name, shortcut, handler):
        a = QAction(name, self)
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(handler)
        menu.addAction(a)

    def currentEditor(self):
        w = self.tabs.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def _toggleSidebar(self):
        self.tree.setVisible(not self.tree.isVisible())

    def _openFromTree(self, index):
        path = self.fsmodel.filePath(index)
        if not self.fsmodel.isDir(index):
            self.openFile(path)

    def _openFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self.fsmodel.setRootPath(folder)
            self.tree.setRootIndex(self.fsmodel.index(folder))
            self.setWindowTitle(f"Lcode — {Path(folder).name}")

    def _openFileDialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "C/C++ (*.c *.h *.cpp *.hpp);;Python (*.py);;All Files (*)"
        )
        if path:
            self.openFile(path)

    def newFile(self):
        e = CodeEditor()
        e.cursorPositionChanged.connect(self._updateCursor)
        self.tabs.addTab(e, "untitled")
        self.tabs.setCurrentWidget(e)
        e.setFocus()
        self._log("New file created", "#7aa2f7")

    def openFile(self, path):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, CodeEditor) and w.file_path == path:
                self.tabs.setCurrentIndex(i)
                return

        e = CodeEditor(path=path)
        e.cursorPositionChanged.connect(self._updateCursor)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                e.setPlainText(f.read())
        except UnicodeDecodeError:
            with open(path, 'r', encoding='latin-1') as f:
                e.setPlainText(f.read())
        except Exception as ex:
            QMessageBox.warning(self, "Error", str(ex))
            return

        e.document().setModified(False)
        self.tabs.addTab(e, Path(path).name)
        self.tabs.setCurrentWidget(e)
        e.setFocus()
        self._log(f"Opened {Path(path).name}", "#9ece6a")

    def saveFile(self):
        e = self.currentEditor()
        if not e:
            return
        if not e.file_path:
            self._saveAs()
            return
        try:
            with open(e.file_path, 'w', encoding='utf-8') as f:
                f.write(e.toPlainText())
            e.document().setModified(False)
            self._syncTabTitle(e)
            self._log(f"Saved {Path(e.file_path).name}", "#9ece6a")
        except Exception as ex:
            self._log(f"Save error: {ex}", "#f7768e")

    def _saveAs(self):
        e = self.currentEditor()
        if not e:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "C/C++ (*.c *.h *.cpp *.hpp);;Python (*.py);;All Files (*)"
        )
        if path:
            e.file_path = path
            self.saveFile()

    def _closeTab(self, index):
        w = self.tabs.widget(index)
        if isinstance(w, CodeEditor) and w._modified:
            name = self.tabs.tabText(index).rstrip(' ●')
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f'"{name}" has unsaved changes.\nSave before closing?',
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            if reply == QMessageBox.StandardButton.Save:
                self.tabs.setCurrentIndex(index)
                self.saveFile()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.newFile()

    def _syncTabTitle(self, editor):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) is editor:
                name = Path(editor.file_path).name if editor.file_path else "untitled"
                if editor._modified:
                    name += " ●"
                self.tabs.setTabText(i, name)
                break

    def _onTabChanged(self, idx):
        self._updateCursor()
        e = self.currentEditor()
        if e and e.file_path:
            self.setWindowTitle(f"Lcode — {Path(e.file_path).name}")
        else:
            self.setWindowTitle("Lcode")

    def _updateCursor(self):
        e = self.currentEditor()
        if e:
            c = e.textCursor()
            self.cursorLabel.setText(f"Ln {c.blockNumber()+1}  Col {c.columnNumber()+1}")

    def _buildRun(self):
        e = self.currentEditor()
        if not e or not e.file_path:
            self._log("Save file first", "#e0af68")
            return

        self.saveFile()
        p = e.file_path

        if p.endswith('.py'):
            self._log(f"Running {Path(p).name}...", "#e0af68")
            self._runAsync([sys.executable, p])
        elif p.endswith(('.c', '.cpp')):
            out = p.rsplit('.', 1)[0]
            compiler = 'g++' if p.endswith('.cpp') else 'gcc'
            self._log(f"Compiling {Path(p).name}...", "#e0af68")
            try:
                r = subprocess.run([compiler, p, '-o', out, '-lm'], capture_output=True, text=True, timeout=30)
                if r.returncode != 0:
                    self._log(r.stderr, "#f7768e")
                    return
                self._log("Compilation OK", "#9ece6a")
            except Exception as ex:
                self._log(str(ex), "#f7768e")
                return
            self._log(f"Running...", "#e0af68")
            self._runAsync([out])
        else:
            self._log("Unsupported file type", "#f7768e")

    def _runAsync(self, cmd):
        self._worker = _RunWorker(cmd)
        self._worker.output.connect(lambda msg, col: self._log(msg, col))
        self._worker.start()

    def _openReplace(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Replace")
        dlg.setMinimumWidth(420)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        find_label = QLabel("Find")
        find_label.setStyleSheet("color: #a9b1d6; font-size: 12px; font-weight: 500;")
        layout.addWidget(find_label)
        find_field = QLineEdit()
        layout.addWidget(find_field)

        replace_label = QLabel("Replace with")
        replace_label.setStyleSheet("color: #a9b1d6; font-size: 12px; font-weight: 500;")
        layout.addWidget(replace_label)
        replace_field = QLineEdit()
        layout.addWidget(replace_field)

        btn_row = QHBoxLayout()
        replace_btn = QPushButton("Replace All")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(247,118,142,0.15);
                color: #f7768e;
            }
            QPushButton:hover { background: rgba(247,118,142,0.25); }
        """)

        def do_replace():
            e = self.currentEditor()
            if e and find_field.text():
                old = e.toPlainText()
                count = old.count(find_field.text())
                e.setPlainText(old.replace(find_field.text(), replace_field.text()))
                self._log(f"Replaced {count} occurrence(s)", "#9ece6a")
                dlg.close()

        replace_btn.clicked.connect(do_replace)
        cancel_btn.clicked.connect(dlg.close)
        btn_row.addWidget(replace_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)
        dlg.exec()

    def _log(self, msg, color="#a9b1d6"):
        self.console.append(f'<span style="color:{color};">{msg}</span>')


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

