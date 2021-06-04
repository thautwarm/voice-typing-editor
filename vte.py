"""
命令词前缀：肥肥
命令词：0. 重做 1. 撤销 2. 删除 3. 删行 4. 下一行
"""
#!/usr/bin/env python

import sys
import itertools
import time
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QTextEdit, QLabel, QShortcut, QFileDialog, QMessageBox
from PyQt5.QtGui import QKeySequence, QTextCursor
from PyQt5 import Qt
from wisepy2 import wise
from pynput.keyboard import Key, Controller
keyboard = Controller()

prefix = "肥肥"

class Window(QWidget):
    def __init__(self, file_path):
        super().__init__()

        self.file_path = file_path
        self.now = time.time()


        self.open_new_file_shortcut = QShortcut(QKeySequence('Ctrl+O'), self)
        self.open_new_file_shortcut.activated.connect(self.open_new_file)

        self.save_current_file_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        self.save_current_file_shortcut.activated.connect(self.save_current_file)

        vbox = QVBoxLayout()
        text = "Untitled File"
        self.title = QLabel(text)
        self.title.setWordWrap(True)
        self.title.setAlignment(Qt.Qt.AlignCenter)
        vbox.addWidget(self.title)
        self.setLayout(vbox)

        self.scrollable_text_area = QTextEdit()
        self.scrollable_text_area.lineWrapColumnOrWidth = 15

        self.scrollable_text_area.setFontPointSize(32)
        vbox.addWidget(self.scrollable_text_area)

        # fileNewAction=QShortcut('Ctrl+K', self).activated.connect(lambda : )

        self.commands = [
            (f"{prefix}撤销",         self.on_undo),
            (f"{prefix}重做",         self.on_redo),
            (f"{prefix}下一行",       self.on_newline),
            (f"{prefix}删行",         self.on_delete_line),
            (f"{prefix}删除",         self.on_delete),
        ]
        self.scrollable_text_area.textChanged.connect(self.ai_process)
        self.open_current_file()

    def on_undo(self, cmd):
        keyboard.press(Key.ctrl)
        keyboard.press('z')
        keyboard.release('z')
        keyboard.press('z')
        keyboard.release('z')
        keyboard.release(Key.ctrl)

    def on_redo(self, cmd):
        keyboard.press(Key.ctrl)
        keyboard.press(Key.shift)
        keyboard.press('z')
        keyboard.release('z')
        keyboard.press('z')
        keyboard.release('z')
        keyboard.release(Key.shift)
        keyboard.release(Key.ctrl)

    def on_newline(self, cmd):
        self.delete_back_n(len(cmd))
        self.scrollable_text_area.insertPlainText("\n")

    def on_delete_line(self, cmd):
        self.delete_back_n(len(cmd))
        cursor = self.scrollable_text_area.textCursor()
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()

    def on_delete(self, cmd):
        self.delete_back_n(len(cmd) + 1)

    def delete_forward_n(self, n: int):
        cursor = self.scrollable_text_area.textCursor()
        for _ in itertools.repeat(None, n):
            cursor.deleteChar()

    def delete_back_n(self, n: int):
        cursor = self.scrollable_text_area.textCursor()
        for _ in range(n):
            cursor.deletePreviousChar()

    def ai_process(self):
        text = self.scrollable_text_area.toPlainText()
        for cmd, f in self.commands:
            if text.endswith(cmd):

                return f(cmd)
        now = time.time()
        if now - self.now > 1:
            self.now = now
            self.save_current_file()

    def open_current_file(self):
        if self.file_path:
            with open(self.file_path, "r", encoding='utf8') as f:
                file_contents = f.read()
                self.title.setText(self.file_path)
                self.scrollable_text_area.setText(file_contents)


    def open_new_file(self):
        self.file_path, filter_type = QFileDialog.getOpenFileName(self, "Open new file",
                "", "All files (*)")
        if self.file_path:
            with open(self.file_path, "r", encoding='utf8') as f:
                file_contents = f.read()
                self.title.setText(self.file_path)
                self.scrollable_text_area.setText(file_contents)
        else:
            self.invalid_path_alert_message()

    def save_current_file(self):
        if not self.file_path:
            new_file_path, filter_type = QFileDialog.getSaveFileName(self, "Save this file as...", "", "All files (*)")
            if new_file_path:
                self.file_path = new_file_path
            else:
                self.invalid_path_alert_message()
                return False
        file_contents = self.scrollable_text_area.toPlainText()
        with open(self.file_path, "w", encoding='utf8') as f:
            f.write(file_contents)
        self.title.setText(self.file_path)

    def closeEvent(self, event):
        messageBox = QMessageBox()
        title = "Quit Application?"
        message = "WARNING !!\n\nIf you quit without saving, any changes made to the file will be lost.\n\nSave file before quitting?"

        reply = messageBox.question(self, title, message, messageBox.Yes | messageBox.No |
                messageBox.Cancel, messageBox.Cancel)
        if reply == messageBox.Yes:
            return_value = self.save_current_file()
            if return_value == False:
                event.ignore()
        elif reply == messageBox.No:
            event.accept()
        else:
            event.ignore()

    def invalid_path_alert_message(self):
        messageBox = QMessageBox()
        messageBox.setWindowTitle("Invalid file")
        messageBox.setText("Selected filename or path is not valid. Please select a valid file.")
        messageBox.exec()

def main(filename):
    app = QApplication([])
    w = Window(filename)
    w.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    wise(main)()
