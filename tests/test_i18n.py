import _support
import ast
import tempfile
import unittest
from pathlib import Path
from string import Formatter
from unittest.mock import patch
from PIL import Image
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QMessageBox
import i18n
from app import Window, Worker
from fake_registry import Registry

APP = QApplication.instance() or QApplication([])

class LanguageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        config = QSettings(str(self.root / 'preferences.ini'), QSettings.IniFormat)
        patcher = patch('i18n.settings', return_value=config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(lambda: i18n.set_language('ko'))

    def test_system_locale_resolution(self):
        for names, expected in [(['ko-KR'], 'ko'), (['pt-BR'], 'pt'),
                                (['zh-Hant-HK'], 'zh_TW'), (['zh-TW'], 'zh_TW'),
                                (['zh-Hans-CN'], 'zh_CN'), (['de-DE'], 'de'),
                                (['xx', 'ja-JP'], 'ja'), (['xx'], 'en')]:
            self.assertEqual(i18n.resolve_language(names), expected)

    def test_catalogs_are_complete_and_placeholders_match(self):
        fields = lambda text: {name for _, name, _, _ in Formatter().parse(text) if name is not None}
        for code in i18n.LANGUAGES:
            if code == 'ko': continue
            catalog = i18n.CATALOGS[code]
            self.assertEqual(set(catalog), set(i18n.CATALOGS['en']), code)
            for key, text in catalog.items():
                self.assertTrue(text.strip(), (code, key))
                self.assertEqual(fields(key), fields(text), (code, key))
                self.assertFalse(any('\uac00' <= c <= '\ud7a3' for c in text), (code, key))

    def test_all_literal_translation_keys_exist(self):
        for source in (Path(__file__).resolve().parents[1] / 'src').glob('*.py'):
            for node in ast.walk(ast.parse(source.read_text(encoding='utf-8'))):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'tr' and node.args and isinstance(node.args[0], ast.Constant):
                    self.assertIn(node.args[0].value, i18n.CATALOGS['en'], source.name)

    def test_explorer_menu_labels_use_selected_language(self):
        import shell_menu
        registry = Registry()
        with patch.object(shell_menu, 'winreg', registry), patch.object(shell_menu, 'refresh'), patch.object(shell_menu, 'launch_command', return_value=['converter.exe']):
            for code in ('ko', 'en', 'ja', 'ar'):
                i18n.set_language(code)
                shell_menu.enable()
                labels = [values['MUIVerb'][0] for values in registry.data.values() if 'MUIVerb' in values]
                self.assertIn(i18n.tr('{v0}로 변환', v0='PDF'), labels)

    def test_quick_conversion_window_is_localized(self):
        from quick_convert import QuickConvert
        source = self.root / 'original.png'
        Image.new('RGB', (20, 30), 'blue').save(source)
        i18n.set_language('ja')
        # Prevent the startup timer; this test checks the result UI independently.
        with patch('quick_convert.QTimer.singleShot'):
            window = QuickConvert([source], 'jpg', Worker)
        self.addCleanup(window.close)
        window.receive(0, '완료', str(self.root / 'original.jpg'))
        window.finished()
        self.assertEqual(window.title.text(), i18n.tr('변환을 완료했습니다'))
        self.assertEqual(window.timer.interval(), 2500)

    def test_saved_choice_and_system_default(self):
        with patch('i18n.QLocale') as locale:
            locale.system.return_value.uiLanguages.return_value = ['ja-JP']
            i18n.initialize()
            self.assertEqual(i18n.language(), 'ja')
            i18n.set_language('fr', persist=True)
            i18n.set_language('ko')
            i18n.initialize()
            self.assertEqual(i18n.language(), 'fr')
            i18n.set_language('auto', persist=True)
            i18n.initialize()
            self.assertEqual(i18n.language(), 'ja')

    def test_live_switch_preserves_files_formats_and_results(self):
        source = self.root / '완료_日本語_العربية.png'
        Image.new('RGB', (20, 30), 'blue').save(source)
        with patch('shell_menu.is_enabled', return_value=False):
            i18n.set_language('ko')
            window = Window()
        self.addCleanup(window.close)
        window.add_files([str(source)])
        window.table.cellWidget(0, 2).setCurrentIndex(window.table.cellWidget(0, 2).findData('pdf'))
        window.entries[0].update(state='완료', result=str(self.root / 'result.pdf'))
        window.table.item(0, 3).setText(i18n.tr('완료'))
        for code in i18n.LANGUAGES:
            window.language_picker.setCurrentIndex(window.language_picker.findData(code))
            self.assertEqual(window.pick.text(), i18n.tr('＋ 파일 선택'))
            self.assertEqual(window.table.item(0, 0).text(), source.name)
            self.assertEqual(window.table.cellWidget(0, 2).currentData(), 'pdf')
            self.assertEqual(window.entries[0]['state'], '완료')
            self.assertTrue(window.table.item(0, 3).text().startswith(i18n.tr('완료')))
            self.assertEqual(APP.layoutDirection(), Qt.RightToLeft if code in {'ar', 'he'} else Qt.LeftToRight)
        window.set_busy(True)
        self.assertFalse(window.language_picker.isEnabled())
        window.set_busy(False)
        self.assertTrue(window.language_picker.isEnabled())

    def test_localized_dialog_buttons(self):
        for code in i18n.LANGUAGES:
            i18n.set_language(code)
            box = QMessageBox(QMessageBox.Question, 'Office', 'PDF?', QMessageBox.Yes | QMessageBox.No)
            self.assertEqual(box.button(QMessageBox.Yes).text().replace('&', ''), i18n.tr('예'))
            self.assertEqual(box.button(QMessageBox.No).text().replace('&', ''), i18n.tr('아니요'))

    def test_conversion_state_is_independent_of_display_language(self):
        i18n.set_language('ar')
        source = self.root / '日本語_한국어.png'
        Image.new('RGB', (20, 30), 'blue').save(source)
        worker = Worker([(0, source, 'jpg', None)], self.root)
        results = []
        worker.result.connect(lambda row, state, result: results.append((state, result)))
        worker.run()
        self.assertEqual(results[0][0], '완료')
        self.assertTrue(Path(results[0][1]).is_file())

if __name__ == '__main__':
    unittest.main()
