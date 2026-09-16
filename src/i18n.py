"""Offline UI translations and a per-user language preference."""
import json
import sys
from pathlib import Path
from PySide6.QtCore import QLocale, QSettings, Qt, QTranslator
from PySide6.QtWidgets import QApplication, QLabel, QAbstractButton, QTableWidget

LANGUAGES = {
    'ko': '한국어', 'en': 'English', 'ja': '日本語',
    'zh_CN': '简体中文', 'zh_TW': '繁體中文', 'de': 'Deutsch',
    'fr': 'Français', 'es': 'Español', 'pt': 'Português',
    'it': 'Italiano', 'ru': 'Русский', 'vi': 'Tiếng Việt',
    'th': 'ไทย', 'id': 'Bahasa Indonesia', 'ar': 'العربية', 'he': 'עברית',
}
_catalog_path = (Path(sys._MEIPASS) / 'source/translations.json') if getattr(sys, 'frozen', False) else Path(__file__).with_name('translations.json')
CATALOGS = json.loads(_catalog_path.read_text(encoding='utf-8'))
_language = 'ko'
_choice = 'auto'
_sources = {text: source for catalog in CATALOGS.values() for source, text in catalog.items()}
_translator = None

class LocalizedText(str):
    """Retain metadata templates independently of the currently displayed text."""
    def __new__(cls, text, source, values):
        obj = super().__new__(cls, text)
        obj.source, obj.values = source, dict(values)
        return obj

def resolve_language(names):
    for name in names:
        parts = name.replace('-', '_').lower().split('_')
        base = parts[0]
        if base == 'zh':
            return 'zh_TW' if any(p in parts for p in ('hant', 'tw', 'hk', 'mo')) else 'zh_CN'
        if base in LANGUAGES:
            return base
    return 'en'

def settings():
    return QSettings(QSettings.IniFormat, QSettings.UserScope, 'SimpleFileConverter', 'preferences')

def selection():
    return _choice

def language():
    return _language

def set_language(choice, persist=False):
    global _choice, _language, _translator
    _choice = choice if choice in LANGUAGES else 'auto'
    _language = resolve_language(QLocale.system().uiLanguages()) if _choice == 'auto' else _choice
    if persist:
        config = settings()
        config.setValue('language', _choice)
        config.sync()
        if config.status() != QSettings.NoError:
            raise OSError('Could not save the language preference.')
    app = QApplication.instance()
    if app:
        app.setLayoutDirection(Qt.RightToLeft if _language in {'ar', 'he'} else Qt.LeftToRight)
        if _translator:
            app.removeTranslator(_translator)
        _translator = ButtonTranslator(app)
        app.installTranslator(_translator)

def initialize():
    set_language(str(settings().value('language', 'auto')))

def tr(source, **values):
    if isinstance(source, LocalizedText) and not values:
        source, values = source.source, source.values
    elif source not in CATALOGS['en']:
        source = _sources.get(source, source)
    english = CATALOGS['en'].get(source, source)
    text = source if _language == 'ko' else CATALOGS.get(_language, {}).get(source, english)
    text = text.format(**values) if values else text
    return LocalizedText(text, source, values)

def retranslate(root):
    for widget in [root, *root.findChildren(QLabel), *root.findChildren(QAbstractButton)]:
        if hasattr(widget, 'text'):
            widget.setText(tr(widget.text()))
        if widget.toolTip():
            widget.setToolTip(tr(widget.toolTip()))
        if widget.accessibleName():
            widget.setAccessibleName(tr(widget.accessibleName()))
    for table in root.findChildren(QTableWidget):
        for col in range(table.columnCount()):
            item = table.horizontalHeaderItem(col)
            if item: item.setText(tr(item.text()))
        for row in range(table.rowCount()):
            # Filename and output paths must never be translated.
            for col in (1, 3):
                item = table.item(row, col)
                if item: item.setText(tr(item.text()))

class ButtonTranslator(QTranslator):
    def translate(self, context, sourceText, disambiguation=None, n=-1):
        keys = {'&Yes': '예', 'Yes': '예', '&No': '아니요', 'No': '아니요',
                'OK': '확인', '&OK': '확인', 'Cancel': '취소', '&Cancel': '취소',
                'Close': '닫기', '&Close': '닫기'}
        return tr(keys[sourceText]) if context in {'QPlatformTheme', 'QDialogButtonBox', 'QMessageBox'} and sourceText in keys else ''
