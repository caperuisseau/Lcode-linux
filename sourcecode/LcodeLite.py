
# This version will not have Update Ever

import sys, os, json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class IDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "fr"
        self.langs = json.load(open("language.json","r",encoding="utf-8"))
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        box = QWidget(); lay = QVBoxLayout(); lay.addWidget(self.tabs); box.setLayout(lay)
        self.setCentralWidget(box)
        self.make_menu()
        self.new_file()

    def t(self,k):
        try: return self.langs[self.lang][k]
        except: return k

    def make_menu(self):
        m = self.menuBar(); m.clear()
        f = m.addMenu(self.t("file") if "file" in self.langs[self.lang] else "File")
        a = lambda x: QAction(self.t(x),self)
        new = a("new"); op = a("open"); sv = a("save"); rn = a("run")
        un = a("undo"); rd = a("redo"); fd = a("find"); rp = a("replace")
        lg = a("change_language")
        new.triggered.connect(self.new_file)
        op.triggered.connect(self.open_file)
        sv.triggered.connect(self.save_file)
        rn.triggered.connect(self.run_code)
        un.triggered.connect(lambda: self.cur().undo())
        rd.triggered.connect(lambda: self.cur().redo())
        fd.triggered.connect(self.find_text)
        rp.triggered.connect(self.replace_text)
        lg.triggered.connect(self.change_language)
        for x in [new,op,sv,rn,un,rd,fd,rp,lg]: f.addAction(x)

    def cur(self):
        w = self.tabs.currentWidget()
        return w.findChild(QTextEdit)

    def new_file(self):
        e = QTextEdit(); w = QWidget(); l = QVBoxLayout(); l.addWidget(e); w.setLayout(l)
        self.tabs.addTab(w, self.t("untitled")); self.tabs.setCurrentWidget(w)

    def close_tab(self,i):
        self.tabs.removeTab(i)
        if self.tabs.count()==0: self.new_file()

    def open_file(self):
        p = QFileDialog.getOpenFileName(self,self.t("open_file"),"","*.py *.txt")[0]
        if not p: return
        e = QTextEdit(); e.setText(open(p,"r",encoding="utf-8").read())
        w = QWidget(); l = QVBoxLayout(); l.addWidget(e); w.setLayout(l); w.path = p
        self.tabs.addTab(w, os.path.basename(p)); self.tabs.setCurrentWidget(w)

    def save_file(self):
        w = self.tabs.currentWidget(); e = self.cur(); p = getattr(w,"path",None)
        if not p:
            p = QFileDialog.getSaveFileName(self,self.t("save_file"),"","*.py")[0]
            if not p: return
            w.path = p
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(p))
        open(p,"w",encoding="utf-8").write(e.toPlainText())

    def run_code(self):
        try: exec(self.cur().toPlainText(),{})
        except Exception as x: QMessageBox.critical(self,"Error",str(x))

    def find_text(self):
        t = QInputDialog.getText(self,self.t("find"),self.t("find"))[0]
        if not t: return
        if not self.cur().find(t):
            QMessageBox.information(self,"", self.t("not_found") if "not_found" in self.langs[self.lang] else "Not found")

    def replace_text(self):
        d = QDialog(self); l = QVBoxLayout(); f = QLineEdit(); r = QLineEdit(); b = QPushButton(self.t("replace"))
        l.addWidget(f); l.addWidget(r); l.addWidget(b); d.setLayout(l)
        def go():
            e = self.cur(); e.setText(e.toPlainText().replace(f.text(), r.text())); d.close()
        b.clicked.connect(go); d.exec_()

    def change_language(self):
        ls = list(self.langs.keys())
        l, ok = QInputDialog.getItem(self,self.t("select_language"),self.t("select_language"),ls,0,False)
        if ok:
            self.lang = l
            self.make_menu()

app = QApplication(sys.argv)
w = IDE()
w.show()
sys.exit(app.exec_())
