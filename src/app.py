import os
import sys
import threading
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QThread, QUrl, QTimer, QEvent, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QDesktopServices, QIcon, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QLineEdit, QProgressBar, QMessageBox, QHeaderView, QAbstractItemView, QCheckBox
from engine import inspect, convert, Cancelled, IMAGES, MEDIA
from effects import AnimatedButton, DragGlow, ToastManager
QPushButton = AnimatedButton

class DropZone(QLabel):
    files = Signal(list)
    def __init__(self):
        super().__init__('여기에 파일 드래그 혹은 파일 선택')
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(104)
        self.setObjectName('drop')
        self.setAcceptDrops(True)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
    def dropEvent(self, event):
        self.files.emit([u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()])
        event.acceptProposedAction()

class Worker(QThread):
    status = Signal(int, str)
    result = Signal(int, str, str)
    def __init__(self, jobs, folder):
        super().__init__()
        self.jobs, self.folder = jobs, folder
        self.cancel = threading.Event()
    def run(self):
        for row, path, fmt, meta in self.jobs:
            if self.cancel.is_set():
                self.result.emit(row, '취소됨', '')
                continue
            self.status.emit(row, '변환 중…')
            try:
                out = convert(path, fmt, self.folder if self.folder is not None else Path(path).parent, meta, self.cancel, lambda text: self.status.emit(row, text))
                self.result.emit(row, '완료', str(out))
            except Cancelled:
                self.result.emit(row, '취소됨', '')
            except Exception as e:
                self.result.emit(row, '실패', str(e))

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simple File Converter')
        self.setWindowIcon(QIcon(str(Path(getattr(sys, '_MEIPASS', Path(__file__).parent)) / 'sfc.ico')))
        self.resize(960, 640)
        self.setMinimumSize(820, 560)
        self.setAcceptDrops(True)
        self.entries = []
        self.worker = None
        self.last_folder = None
        self.login_prompted = False
        self.presentation_consent = False
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(30, 26, 30, 24)
        layout.setSpacing(14)
        self.drop = DropZone()
        self.drop.files.connect(self.add_files)
        layout.addWidget(self.drop)
        bar = QHBoxLayout()
        self.pick = QPushButton('＋ 파일 선택')
        self.pick.clicked.connect(self.choose_files)
        self.remove = QPushButton('선택 삭제')
        self.remove.clicked.connect(self.remove_selected)
        self.clear = QPushButton('목록 비우기')
        self.clear.clicked.connect(self.clear_files)
        for button in [self.pick, self.remove, self.clear]: bar.addWidget(button)
        bar.addStretch()
        layout.addLayout(bar)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['파일', '파일 정보', '변환 형식', '상태 / 결과'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 120)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.show_result)
        layout.addWidget(self.table, 1)
        dest = QHBoxLayout()
        dest.addWidget(QLabel('저장 위치'))
        self.folder = QLineEdit(str(Path.home() / 'Downloads' / 'Simple File Converter'))
        dest.addWidget(self.folder, 1)
        self.browse = QPushButton('폴더 선택')
        self.browse.clicked.connect(self.choose_folder)
        dest.addWidget(self.browse)
        self.same_folder = QCheckBox('원본 폴더에 저장')
        self.same_folder.setToolTip('각 파일이 있는 폴더에 변환 결과를 저장합니다.')
        self.same_folder.toggled.connect(self.update_save_controls)
        dest.addWidget(self.same_folder)
        layout.addLayout(dest)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        bottom = QHBoxLayout()
        self.status = QLabel('파일 대기')
        bottom.addWidget(self.status, 1)
        self.open = QPushButton('저장 폴더 열기')
        self.open.clicked.connect(self.open_folder)
        bottom.addWidget(self.open)
        self.cancel = QPushButton('취소')
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(self.stop)
        bottom.addWidget(self.cancel)
        self.start = QPushButton('변환 시작')
        self.start.setObjectName('primary')
        self.start.clicked.connect(self.begin)
        self.start.setEnabled(False)
        bottom.addWidget(self.start)
        layout.addLayout(bottom)
        from shell_menu import is_enabled
        self.context_menu = QCheckBox('우클릭 변환 메뉴 사용')
        self.context_menu.setToolTip('Windows 11: 더 많은 옵션 표시 → Simple File Converter\n등록 후 실행 파일을 옮기면 체크를 껐다 켜 주세요.')
        self.context_menu.setChecked(is_enabled())
        self.context_menu.toggled.connect(self.toggle_context_menu)
        layout.addWidget(self.context_menu)
        self.toasts = ToastManager(root)
        self.glow = DragGlow(root)
        self.drag_reset = QTimer(self)
        self.drag_reset.setSingleShot(True)
        self.drag_reset.timeout.connect(self.reset_drag)
        self.progress_motion = QPropertyAnimation(self.progress, b'value', self)
        self.progress_motion.setDuration(450)
        self.progress_motion.setEasingCurve(QEasingCurve.OutCubic)
        # Route drag events from every child, including the table and text field.
        for widget in [self, *self.findChildren(QWidget)]:
            widget.setAcceptDrops(True)
        QApplication.instance().installEventFilter(self)

    def notify(self, title, message, kind='info', details=''):
        self.toasts.show(title, message, kind, details)
    def toggle_context_menu(self, checked):
        from shell_menu import enable, disable, is_enabled
        try:
            if checked: enable()
            else: disable()
        except Exception as exc:
            self.context_menu.blockSignals(True)
            self.context_menu.setChecked(is_enabled())
            self.context_menu.blockSignals(False)
            self.notify('우클릭 메뉴를 변경하지 못했습니다', '상세 내용을 확인한 뒤 다시 시도해 주세요.', 'error', str(exc))
            return
        if checked:
            self.notify('우클릭 변환 메뉴를 켰습니다', '파일을 우클릭하고 변환 형식을 선택해 주세요.')
        else:
            self.notify('우클릭 변환 메뉴를 껐습니다', '필요할 때 다시 켤 수 있습니다.')
    def update_save_controls(self):
        enabled = not self.same_folder.isChecked() and not self.busy()
        self.folder.setEnabled(enabled)
        self.browse.setEnabled(enabled)
    def reset_drag(self):
        self.drag_reset.stop()
        self.glow.deactivate()
        self.drop.setText('여기에 파일 드래그 혹은 파일 선택')
        self.drop.setProperty('dragActive', False)
        self.drop.style().unpolish(self.drop); self.drop.style().polish(self.drop)
    def eventFilter(self, obj, event):
        if not isinstance(obj, QWidget) or obj.window() is not self:
            return super().eventFilter(obj, event)
        kind = event.type()
        if kind in (QEvent.DragEnter, QEvent.DragMove):
            urls = event.mimeData().urls()
            if not any(u.isLocalFile() for u in urls):
                self.reset_drag(); event.ignore(); return True
            self.drag_reset.stop()
            blocked = self.busy()
            self.glow.activate(blocked)
            self.drop.setText('변환 중 · 추가 불가' if blocked else f'{sum(u.isLocalFile() for u in urls)}개 파일 감지 · 놓아서 추가')
            self.drop.setProperty('dragActive', True)
            self.drop.style().unpolish(self.drop); self.drop.style().polish(self.drop)
            event.setDropAction(Qt.CopyAction); event.accept(); return True
        if kind == QEvent.DragLeave:
            # A short delay avoids flicker when crossing between child widgets.
            self.drag_reset.start(45)
            event.accept(); return True
        if kind == QEvent.Drop:
            paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
            self.reset_drag()
            if self.busy(): self.notify('변환 중입니다', '완료 후 파일을 추가해 주세요.')
            elif paths: self.add_files(paths)
            event.setDropAction(Qt.CopyAction); event.accept(); return True
        return super().eventFilter(obj, event)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'toasts'):
            self.glow.setGeometry(self.centralWidget().rect())
            self.toasts.layout()

    def busy(self): return self.worker is not None and self.worker.isRunning()
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and not self.busy(): event.acceptProposedAction()
    def dropEvent(self, event):
        self.add_files([u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()])
        event.acceptProposedAction()
    def choose_files(self):
        patterns = ' '.join('*.' + e for e in sorted(IMAGES | MEDIA | {'pdf', 'ppt', 'pptx'}))
        paths, _ = QFileDialog.getOpenFileNames(self, '변환할 파일 선택', '', f'지원 파일 ({patterns});;모든 파일 (*)')
        self.add_files(paths)
    def add_files(self, paths):
        if self.busy(): return
        errors = []
        added, duplicates = 0, 0
        known = {str(e['path']).lower() for e in self.entries}
        slides = [p for p in paths if Path(p).suffix.lower() in {'.ppt', '.pptx'} and str(Path(p).resolve()).lower() not in known]
        if slides:
            from office import backend
            name, _ = backend()
            if name and self.presentation_consent:
                allowed = True
            elif name:
                answer = QMessageBox.question(self, 'PPT 변환 확인', f'{name}가 설치되어 있습니다. 파일을 PDF 변환 목록에 추가할까요?\n\nPDF를 PPT로 바꾸면 이미지 슬라이드로 저장되어 텍스트를 개별 편집할 수 없습니다.\n예를 누르면 목록을 비울 때까지 다시 묻지 않습니다.', QMessageBox.Yes | QMessageBox.No)
                allowed = answer == QMessageBox.Yes
                if allowed: self.presentation_consent = True
            else:
                QMessageBox.warning(self, '변환 프로그램이 필요합니다', 'PowerPoint 또는 LibreOffice를 설치한 뒤 다시 시도해 주세요.')
                allowed = False
            if not allowed: paths = [p for p in paths if p not in slides]
        for value in paths:
            path = Path(value).resolve()
            if str(path).lower() in known:
                duplicates += 1
                continue
            if not path.is_file():
                errors.append(f'{path.name}: 파일을 선택해 주세요.')
                continue
            try:
                meta = inspect(path)
            except Exception as e:
                errors.append(f'{path.name}: {e}')
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            item = QTableWidgetItem(path.name)
            item.setToolTip(str(path))
            self.table.setItem(row, 0, item)
            self.table.setItem(row, 1, QTableWidgetItem(meta['detail']))
            combo = QComboBox()
            combo.addItems([f.upper() for f in meta['formats']])
            ext = path.suffix.lower()[1:]
            if combo.currentText().lower() == ext and combo.count() > 1: combo.setCurrentIndex(1)
            self.table.setCellWidget(row, 2, combo)
            self.table.setItem(row, 3, QTableWidgetItem('대기'))
            self.entries.append({'path': path, 'meta': meta, 'result': '', 'state': '대기'})
            added += 1
            combo.setAcceptDrops(True)
            known.add(str(path).lower())
        self.status.setText(f'{len(self.entries)}개 파일')
        self.start.setEnabled(bool(self.entries))
        if not self.entries: self.presentation_consent = False
        if added: self.notify('파일을 추가했습니다', f'{added}개 파일의 변환 형식을 선택해 주세요.')
        if duplicates: self.notify('이미 추가된 파일입니다', f'중복된 {duplicates}개 파일은 건너뛰었습니다.')
        if errors: self.notify('일부 파일을 추가하지 못했습니다', f'{len(errors)}개 파일의 원인을 상세 보기에서 확인해 주세요.', 'error', '\n'.join(errors))
    def remove_selected(self):
        count = len({i.row() for i in self.table.selectedIndexes()})
        for row in sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True):
            self.entries.pop(row)
            self.table.removeRow(row)
        self.start.setEnabled(bool(self.entries))
        self.status.setText(f'{len(self.entries)}개 파일')
        if not self.entries: self.presentation_consent = False
        if count: self.notify('목록에서 제거했습니다', f'{count}개 항목을 제거했습니다. 원본 파일은 그대로입니다.')
    def clear_files(self):
        self.entries.clear()
        self.presentation_consent = False
        self.table.setRowCount(0)
        self.start.setEnabled(False)
        self.status.setText('파일 대기')
        self.progress.setValue(0)
        self.notify('목록을 비웠습니다', '새 파일을 추가해 주세요.')
    def choose_folder(self):
        value = QFileDialog.getExistingDirectory(self, '저장 폴더 선택', self.folder.text())
        if value:
            self.folder.setText(value)
            self.notify('저장 위치를 변경했습니다', '선택한 폴더에 결과를 저장합니다.')
    def open_folder(self):
        if self.same_folder.isChecked() and self.entries:
            row = max(0, self.table.currentRow())
            path = self.entries[row]['path'].parent
        else:
            path = self.last_folder or Path(self.folder.text())
        if Path(path).is_dir(): QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else: self.notify('저장 폴더가 아직 없습니다', '변환을 시작하면 자동으로 생성됩니다.')
    def set_busy(self, busy):
        for widget in [self.pick, self.remove, self.clear, self.drop, self.same_folder, self.start]: widget.setEnabled(not busy)
        self.folder.setEnabled(not busy and not self.same_folder.isChecked())
        self.browse.setEnabled(not busy and not self.same_folder.isChecked())
        for row in range(self.table.rowCount()): self.table.cellWidget(row, 2).setEnabled(not busy)
        self.cancel.setEnabled(busy)
    def begin(self):
        if self.busy() or not self.entries: return
        reverse = [i for i,e in enumerate(self.entries) if e['meta']['kind'] == 'pdf' and self.table.cellWidget(i, 2).currentText().lower() in {'ppt', 'pptx'}]
        if reverse:
            from office import backend
            if any(self.table.cellWidget(i, 2).currentText() == 'PPT' for i in reverse) and not backend()[0]:
                QMessageBox.warning(self, 'PPT 변환 프로그램이 필요합니다', 'PowerPoint 또는 LibreOffice를 설치해 주세요.\nPPTX를 선택하면 별도 설치 없이 변환할 수 있습니다.')
                return
            if not self.presentation_consent:
                if QMessageBox.question(self, 'PPT 변환 확인', 'PDF의 각 페이지를 이미지 슬라이드로 변환할까요?\n텍스트를 개별 편집할 수는 없습니다.\n\n예를 누르면 목록을 비울 때까지 다시 묻지 않습니다.', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                    return
                self.presentation_consent = True
        self.progress_motion.stop()
        value = self.folder.text().strip()
        if not value and not self.same_folder.isChecked():
            self.notify('저장 위치를 선택해 주세요', '변환 결과를 저장할 폴더가 필요합니다.', 'error')
            return
        folder = None if self.same_folder.isChecked() else Path(value).expanduser().resolve()
        try:
            if folder is not None: folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.notify('이 폴더에 저장할 수 없습니다', '다른 폴더를 선택하거나 접근 권한을 확인해 주세요.', 'error', str(e))
            return
        self.last_folder = folder
        jobs = [(i, e['path'], self.table.cellWidget(i, 2).currentText().lower(), e['meta']) for i, e in enumerate(self.entries)]
        self.done_count = 0
        self.login_prompted = False
        for i, e in enumerate(self.entries):
            e.update(result='', state='대기')
            self.update_status(i, '대기')
        self.set_busy(True)
        self.progress.setRange(0, 0)
        self.status.setText(f'변환 중 · 0/{len(jobs)}개 처리')
        self.worker = Worker(jobs, folder)
        self.worker.status.connect(self.update_status)
        self.worker.result.connect(self.receive)
        self.worker.finished.connect(self.finished)
        self.worker.start()
        self.notify('변환을 시작했습니다', f'{len(jobs)}개 파일을 처리하고 있습니다.')
    def update_status(self, row, text):
        self.table.item(row, 3).setText(text)
        self.table.item(row, 3).setForeground(QColor('#3264d9' if text != '대기' else '#67748d'))
    def receive(self, row, state, result):
        self.entries[row].update(state=state, result=result)
        self.table.item(row, 3).setText(state + (' · 두 번 클릭' if result else ''))
        self.table.item(row, 3).setToolTip(result)
        self.table.item(row, 3).setForeground(QColor({'완료': '#168653', '실패': '#d83d51'}.get(state, '#3264d9')))
        if state == '실패': self.notify('파일을 변환하지 못했습니다', self.entries[row]['path'].name, 'error', result)
        self.done_count += 1
        self.status.setText(f'변환 중 · {self.done_count}/{len(self.entries)}개 처리')
        if state == '실패' and not self.login_prompted:
            message = result.lower()
            if any(token in message for token in ['80070520', 'logon', 'sign in', 'signin', '로그인', 'authentication', 'activation', '제품 인증']):
                self.login_prompted = True
                QTimer.singleShot(0, self.office_login)
    def office_login(self):
        if QMessageBox.question(self, 'Office 로그인 확인', 'Office 연결에 문제가 있습니다. 로그인 확인을 위해 브라우저를 열까요?\n\nWindows 세션 오류라면 Office 앱을 다시 실행해야 할 수 있습니다.', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if QDesktopServices.openUrl(QUrl('https://www.office.com/login')):
                self.notify('로그인 페이지를 열었습니다', '로그인을 마친 뒤 변환을 다시 시도해 주세요.')
            else:
                self.notify('브라우저를 열지 못했습니다', '브라우저에서 office.com/login에 접속해 주세요.', 'error')
    def finished(self):
        self.set_busy(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress_motion.setStartValue(0); self.progress_motion.setEndValue(100); self.progress_motion.start()
        counts = {state: sum(e['state'] == state for e in self.entries) for state in ['완료', '실패', '취소됨']}
        self.status.setText(' · '.join(f'{state} {count}개' for state, count in counts.items()))
        if counts['실패']:
            self.notify('일부 파일을 변환하지 못했습니다', self.status.text() + '\n실패 항목을 두 번 클릭해 원인을 확인해 주세요.', 'error')
        elif counts['취소됨']:
            self.notify('변환을 취소했습니다', self.status.text())
        else:
            self.notify('변환을 완료했습니다', f"{counts['완료']}개 파일을 저장했습니다. 저장 폴더에서 확인해 주세요.", 'success')
    def stop(self):
        if self.busy():
            self.worker.cancel.set()
            self.cancel.setEnabled(False)
            self.status.setText('취소 중…')
            self.notify('취소하고 있습니다', '작업을 정리하고 있습니다. 잠시만 기다려 주세요.')
    def show_result(self, row, col):
        entry = self.entries[row]
        if entry['state'] == '완료': QDesktopServices.openUrl(QUrl.fromLocalFile(entry['result']))
        elif entry['state'] == '실패': QMessageBox.warning(self, '변환 오류 안내', entry['result'])
    def closeEvent(self, event):
        if self.busy():
            self.stop()
            self.status.setText('취소 중 · 완료 후 종료')
            event.ignore()
        else:
            QApplication.instance().removeEventFilter(self)
            event.accept()

STYLE = '''
QWidget { background: #f5f7fb; color: #20283b; font-family: "Malgun Gothic"; font-size: 13px; }
QLabel#title { font-size: 30px; font-weight: 700; }
QLabel#drop { background: #edf2ff; border: 2px dashed #9cafe9; border-radius: 14px; color: #425c9e; font-size: 16px; }
QLabel#drop[dragActive="true"] { background: #dce8ff; border: 2px solid #416ef0; color: #2349b0; font-weight: 700; }
QLabel#note { color: #67748d; font-size: 12px; }
QPushButton { background: white; border: 1px solid #d7deeb; border-radius: 8px; padding: 10px 16px; }
QPushButton:hover { background: #e8eeff; border-color: #9aace0; }
QPushButton#primary { background: #365fd5; color: white; border: none; font-weight: 700; padding: 12px 25px; }
QPushButton:disabled { color: #a0a6b3; background: #e8ebf1; }
QTableWidget { background: white; border: 1px solid #dce2ed; border-radius: 9px; gridline-color: #edf0f6; selection-background-color: #e2eaff; selection-color: #20283b; }
QHeaderView::section { background: #edf1f8; border: none; padding: 11px; font-weight: 700; }
QLineEdit, QComboBox { background: white; border: 1px solid #d7deeb; border-radius: 6px; padding: 8px; }
QLineEdit:focus, QComboBox:focus { border: 2px solid #7392ef; }
QProgressBar { border: none; background: #e2e7f2; border-radius: 5px; text-align: center; height: 14px; }
QProgressBar::chunk { background: #7392ef; border-radius: 5px; }
'''

if __name__ == '__main__':
    if '--self-test' in sys.argv:
        from diagnostics import run
        sys.exit(run(sys.argv[sys.argv.index('--self-test') + 1]))
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    app.setApplicationName('Simple File Converter')
    if '--context-convert' in sys.argv:
        from quick_convert import QuickConvert
        index = sys.argv.index('--context-convert')
        if len(sys.argv) != index + 3:
            QMessageBox.warning(None, 'Simple File Converter', '변환할 파일과 형식을 확인해 주세요.')
            sys.exit(1)
        window = QuickConvert(Path(sys.argv[index + 2]).resolve(), sys.argv[index + 1].lower(), Worker)
    else:
        window = Window()
    window.show()
    if '--smoke-test' in sys.argv:
        QTimer.singleShot(1500, app.quit)
    sys.exit(app.exec())
