import _support
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QPointF
from PySide6.QtGui import QEnterEvent
from PySide6.QtTest import QTest
from app import Window, Worker

APP = QApplication.instance() or QApplication([])


class UITests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        state = patch('shell_menu.is_enabled', return_value=False)
        state.start()
        self.addCleanup(state.stop)
        self.window = Window()
        self.addCleanup(self.window.close)

    def test_ppt_consent_lasts_until_list_is_empty(self):
        paths = []
        for name in ['one.ppt', 'two.pptx', 'three.ppt']:
            path = self.root / name
            path.write_bytes(b'only testing UI consent, not Office parsing')
            paths.append(str(path))
        with patch('office.backend', return_value=('PowerPoint', '')), patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes) as question:
            self.window.add_files(paths[:1])
            self.window.add_files(paths[1:2])
            self.assertEqual(question.call_count, 1)
            self.window.table.selectRow(0)
            self.window.remove_selected()
            self.window.add_files(paths[2:])
            self.assertEqual(question.call_count, 1)
            while self.window.entries:
                self.window.table.selectRow(0)
                self.window.remove_selected()
            self.window.add_files(paths[:1])
            self.assertEqual(question.call_count, 2)
            self.window.clear_files()
            self.assertFalse(self.window.presentation_consent)

    def test_original_folder_mode_and_custom_folder(self):
        jobs = []
        for i in range(2):
            folder = self.root / str(i)
            folder.mkdir()
            path = folder / 'image.png'
            Image.new('RGB', (30, 20), 'blue').save(path)
            jobs.append((i, path, 'jpg', None))
        for destination in [None, self.root / 'custom']:
            results = []
            worker = Worker(jobs, destination)
            worker.result.connect(lambda row, state, result: results.append((row, state, result)))
            worker.run()
            self.assertEqual(len(results), 2)
            for row, state, result in results:
                self.assertEqual(state, '완료')
                self.assertEqual(Path(result).parent, destination or jobs[row][1].parent)
        self.window.same_folder.setChecked(True)
        self.assertFalse(self.window.folder.isEnabled())
        self.window.same_folder.setChecked(False)
        self.assertTrue(self.window.folder.isEnabled())

    def test_checkbox_enable_and_disable(self):
        with patch('shell_menu.enable') as enable, patch('shell_menu.disable') as disable:
            self.window.context_menu.setChecked(True)
            self.window.context_menu.setChecked(False)
            enable.assert_called_once()
            disable.assert_called_once()

    def test_version_is_small_footer_label(self):
        from version import VERSION
        self.assertEqual(self.window.version.text(), 'v' + VERSION)
        self.assertEqual(self.window.version.objectName(), 'version')

    def test_toast_expires_even_when_hovered(self):
        self.window.show()
        for kind in ['info', 'success', 'error']:
            self.window.notify('테스트', '알림 메시지', kind)
        for toast in self.window.toasts.items:
            QApplication.sendEvent(toast, QEnterEvent(QPointF(), QPointF(), QPointF()))
        QTest.qWait(2000)
        self.assertEqual(len(self.window.toasts.items), 3)
        QTest.qWait(1000)
        self.assertEqual(len(self.window.toasts.items), 0)


if __name__ == '__main__':
    unittest.main()
