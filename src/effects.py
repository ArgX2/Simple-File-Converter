"""Small, non-blocking interaction effects for Simple File Converter."""
from i18n import tr
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF, QVariantAnimation, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QMessageBox

class AnimatedButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(54, 95, 213, 80))
        self.shadow.setBlurRadius(0)
        self.setGraphicsEffect(self.shadow)
        self.motion = QPropertyAnimation(self.shadow, b'blurRadius', self)
        self.motion.setDuration(160)
        self.motion.setEasingCurve(QEasingCurve.OutCubic)
        self.pressed.connect(lambda: self.animate(3))
        self.released.connect(lambda: self.animate(16 if self.underMouse() else 0))
    def animate(self, target):
        self.motion.stop()
        self.motion.setStartValue(self.shadow.blurRadius())
        self.motion.setEndValue(target)
        self.motion.start()
    def enterEvent(self, event):
        if self.isEnabled(): self.animate(16)
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.animate(0)
        super().leaveEvent(event)
    def focusInEvent(self, event):
        self.animate(16)
        super().focusInEvent(event)
    def focusOutEvent(self, event):
        self.animate(0)
        super().focusOutEvent(event)

class DragGlow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.phase = 0.0
        self.blocked = False
        self.pulse = QVariantAnimation(self)
        self.pulse.setDuration(1100)
        self.pulse.setStartValue(0.0)
        self.pulse.setKeyValueAt(.5, 1.0)
        self.pulse.setEndValue(0.0)
        self.pulse.setLoopCount(-1)
        self.pulse.valueChanged.connect(self.frame)
        self.hide()
    def frame(self, value):
        self.phase = value
        self.update()
    def activate(self, blocked=False):
        self.blocked = blocked
        self.setGeometry(self.parentWidget().rect())
        self.show()
        self.raise_()
        if self.pulse.state() != QVariantAnimation.Running: self.pulse.start()
    def deactivate(self):
        self.pulse.stop()
        self.hide()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor('#dc4455' if self.blocked else '#416ef0')
        wash = QColor(color); wash.setAlpha(12 + int(self.phase * 10))
        painter.setBrush(wash)
        color.setAlpha(150 + int(self.phase * 100))
        painter.setPen(QPen(color, 3 + self.phase * 2))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(5, 5, -5, -5), 16, 16)

COLORS = {
    'info': ('#3264d9', '#eef4ff', 'i'),
    'success': ('#168653', '#edf9f2', '✓'),
    'error': ('#d83d51', '#fff0f2', '!'),
}

class Toast(QWidget):
    def __init__(self, manager, title, message, kind, details=''):
        super().__init__(manager.host)
        self.manager = manager
        self.kind = kind
        self.closing = False
        accent, bg, symbol = COLORS[kind]
        self.setObjectName('toastCard')
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet(f'QWidget#toastCard {{ background: {bg}; border: 1px solid {accent}; border-left: 5px solid {accent}; border-radius: 12px; }} QLabel {{ background: transparent; border: none; color: #26344c; }} QPushButton {{ background: transparent; color: {accent}; border: none; padding: 3px 6px; }}')
        self.setFixedWidth(min(370, manager.host.width() - 40))
        box = QVBoxLayout(self); box.setContentsMargins(16, 12, 12, 12); box.setSpacing(5)
        top = QHBoxLayout()
        label = QLabel(f'{symbol}  {title}')
        label.setTextFormat(Qt.PlainText)
        label.setWordWrap(True)
        label.setStyleSheet(f'font-weight: 700; color: {accent}; font-size: 14px;')
        top.addWidget(label, 1)
        close = QPushButton('×'); close.setAccessibleName(tr('알림 닫기')); close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(self.dismiss)
        top.addWidget(close); box.addLayout(top)
        if message:
            body = QLabel(message); body.setTextFormat(Qt.PlainText); body.setWordWrap(True)
            box.addWidget(body)
        if details:
            more = QPushButton(tr('상세 보기')); more.setCursor(Qt.PointingHandCursor)
            more.clicked.connect(lambda: QMessageBox.information(manager.host, title, details))
            box.addWidget(more, 0, Qt.AlignRight)
        self.adjustSize()
        self.opacity = QGraphicsOpacityEffect(self); self.setGraphicsEffect(self.opacity)
        self.fade = QPropertyAnimation(self.opacity, b'opacity', self)
        self.slide = QPropertyAnimation(self, b'pos', self)
        self.slide.setDuration(240); self.slide.setEasingCurve(QEasingCurve.OutCubic)
        self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.dismiss)
        self.lifetime = 2500
        self.fade.finished.connect(self.after_fade)
    def reveal(self, target):
        self.move(target + QPoint(35, 12)); self.opacity.setOpacity(0)
        self.show(); self.raise_(); self.reposition(target)
        self.fade.setDuration(220); self.fade.setStartValue(0.0); self.fade.setEndValue(1.0); self.fade.start()
        self.timer.start(self.lifetime)
    def reposition(self, target):
        self.slide.stop(); self.slide.setStartValue(self.pos()); self.slide.setEndValue(target); self.slide.start()
    def dismiss(self):
        if self.closing: return
        self.closing = True; self.timer.stop(); self.fade.stop()
        self.fade.setDuration(180); self.fade.setStartValue(self.opacity.opacity()); self.fade.setEndValue(0.0); self.fade.start()
    def after_fade(self):
        if self.closing: self.manager.remove(self)

class ToastManager:
    def __init__(self, host):
        self.host = host
        self.items = []
    def show(self, title, message, kind='info', details=''):
        while len(self.items) >= 3: self.remove(self.items[0])
        toast = Toast(self, title, message, kind, details)
        self.items.append(toast)
        self.layout(new=toast)
    def layout(self, new=None):
        while len(self.items) > 1 and sum(t.height() + 10 for t in self.items) > self.host.height() - 130:
            oldest = self.items.pop(0)
            oldest.timer.stop(); oldest.fade.stop(); oldest.slide.stop(); oldest.hide(); oldest.deleteLater()
        bottom = self.host.height() - 96
        for toast in reversed(self.items):
            bottom -= toast.height()
            target = QPoint(self.host.width() - toast.width() - 24, bottom)
            if toast is new: toast.reveal(target)
            else: toast.reposition(target)
            bottom -= 10
    def remove(self, toast):
        if toast not in self.items: return
        self.items.remove(toast)
        toast.timer.stop(); toast.fade.stop(); toast.slide.stop(); toast.hide(); toast.deleteLater()
        self.layout()
