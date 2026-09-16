"""Small progress/result window for an Explorer conversion command."""
from i18n import tr
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox, QApplication

class QuickConvert(QWidget):
    def __init__(self, path, fmt, worker_type):
        super().__init__()
        self.setWindowTitle('Simple File Converter')
        self.setWindowIcon(QIcon(str(Path(getattr(sys, '_MEIPASS', Path(__file__).parent)) / 'sfc.ico')))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(460, 190)
        self.state, self.result = '', ''
        self.worker = worker_type([(0, path, fmt, None)], path.parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        self.title = QLabel(tr('파일을 변환하고 있습니다'))
        self.title.setStyleSheet('font-size: 16px; font-weight: 700; color: #3264d9;')
        layout.addWidget(self.title)
        self.message = QLabel(f'{path.name} → {fmt.upper()}')
        self.message.setTextFormat(Qt.PlainText); self.message.setWordWrap(True)
        layout.addWidget(self.message)
        self.progress = QProgressBar(); self.progress.setRange(0, 0)
        layout.addWidget(self.progress)
        row = QHBoxLayout(); row.addStretch()
        self.details = QPushButton(tr('상세 보기')); self.details.hide()
        self.details.clicked.connect(self.show_details); row.addWidget(self.details)
        self.cancel = QPushButton(tr('취소')); self.cancel.clicked.connect(self.stop); row.addWidget(self.cancel)
        layout.addLayout(row)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.close)
        self.worker.result.connect(self.receive)
        self.worker.finished.connect(self.finished)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24, screen.bottom() - self.height() - 48)
        QTimer.singleShot(0, self.worker.start)
    def receive(self, row, state, result):
        self.state, self.result = state, result
    def finished(self):
        self.cancel.setText(tr('닫기')); self.cancel.setEnabled(True)
        self.progress.setRange(0, 100); self.progress.setValue(100)
        if self.state == '완료':
            self.title.setText(tr('변환을 완료했습니다'))
            self.title.setStyleSheet('font-size: 16px; font-weight: 700; color: #168653;')
            self.message.setText(tr('원본 파일과 같은 폴더에 저장했습니다.'))
        elif self.state == '취소됨':
            self.title.setText(tr('변환을 취소했습니다'))
            self.message.setText(tr('원본 파일은 그대로 보관됩니다.'))
        else:
            self.title.setText(tr('파일을 변환하지 못했습니다'))
            self.title.setStyleSheet('font-size: 16px; font-weight: 700; color: #d83d51;')
            self.message.setText(tr('원인과 확인 방법은 상세 보기를 눌러 확인해 주세요.'))
            self.details.show()
            if any(t in self.result.lower() for t in ['80070520', 'logon', 'sign in', 'signin', '로그인', 'authentication', 'activation', '제품 인증']):
                if QMessageBox.question(self, tr('Office 로그인 확인'), tr('Office 연결에 문제가 있습니다. 로그인 페이지를 열까요?\nWindows 세션 오류는 앱 재실행이 필요할 수 있습니다.'), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl('https://www.office.com/login'))
        self.timer.start(2500)
    def show_details(self):
        self.timer.stop()
        QMessageBox.information(self, tr('변환 오류 안내'), self.result)
        self.timer.start(2500)
    def stop(self):
        if self.worker.isRunning():
            self.worker.cancel.set(); self.cancel.setEnabled(False)
            self.title.setText(tr('작업을 정리하고 있습니다'))
        else: self.close()
    def closeEvent(self, event):
        if self.worker.isRunning():
            self.stop(); event.ignore()
        else: event.accept()
