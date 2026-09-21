import _support
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch, Mock
import pymupdf
import document
from engine import convert, inspect, Cancelled, imperfect_for_extension
from docx_fixture import make_docx, TYPES, RELS


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docx = make_docx(self.root / '한글 & input.docx')
        self.pdf = self.root / 'sample.pdf'
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((50, 50), 'Source content')
            pdf.save(self.pdf)

    def test_backend_selection_and_no_pdf_libreoffice_fallback(self):
        for word, lo, direction, expected in [
            (True, 'soffice', 'docx-to-pdf', 'Word'),
            (True, None, 'pdf-to-docx', 'Built-in PDF extraction'),
            (False, 'soffice', 'docx-to-pdf', 'LibreOffice'),
            (False, 'soffice', 'pdf-to-docx', 'Built-in PDF extraction'),
            (False, None, 'docx-to-pdf', None)]:
            with self.subTest(word=word, lo=lo, direction=direction), patch.object(document, '_word_installed', return_value=word), patch.object(document, '_libreoffice_path', return_value=lo):
                self.assertEqual(document.backend(direction)[0], expected)

    def test_invalid_direction_rejected(self):
        with self.assertRaises(ValueError):
            document.backend('pdf-to-doc')

    def test_docx_xml_and_relationships_are_validated(self):
        invalids = [('not xml', TYPES, RELS), ('<document/>', TYPES, RELS),
                    ('<document/>', '<Types/>', RELS), ('<document/>', TYPES, '<Relationships/>')]
        for body, types, rels in invalids:
            with zipfile.ZipFile(self.docx, 'w') as package:
                package.writestr('[Content_Types].xml', types)
                package.writestr('_rels/.rels', rels)
                package.writestr('word/document.xml', body)
            with self.assertRaises(ValueError):
                document.validate_docx(self.docx)

    def test_docx_content_and_empty_document(self):
        self.assertEqual(document.validate_docx(self.docx), {'text': True, 'objects': False})
        make_docx(self.docx, text='')
        self.assertEqual(document.validate_docx(self.docx), {'text': False, 'objects': False})
        self.assertEqual(inspect(self.docx)['formats'], ['pdf'])

    def test_pdf_to_docx_dispatch_preserves_original_and_output_collision(self):
        original = self.pdf.read_bytes()
        def output(src, dst, direction, cancel, progress):
            self.assertEqual(direction, 'pdf-to-docx')
            make_docx(dst)
        with patch.object(document, '_convert', side_effect=output):
            first = convert(self.pdf, 'docx', self.root)
            second = convert(self.pdf, 'docx', self.root)
        self.assertEqual(first.name, 'sample.docx')
        self.assertEqual(second.name, 'sample (1).docx')
        self.assertEqual(original, self.pdf.read_bytes())
        self.assertFalse(list(self.root.glob('.converter-*')))

    def test_docx_to_pdf_dispatch_and_readable_output(self):
        def output(src, dst, direction, cancel, progress):
            self.assertEqual(direction, 'docx-to-pdf')
            Path(dst).write_bytes(self.pdf.read_bytes())
        original = self.docx.read_bytes()
        with patch.object(document, '_convert', side_effect=output):
            result = convert(self.docx, 'pdf', self.root)
        with pymupdf.open(result) as pdf:
            self.assertIn('Source content', pdf[0].get_text())
        self.assertEqual(original, self.docx.read_bytes())

    def test_empty_reconstruction_is_not_a_success(self):
        with patch.object(document, '_pdf_to_docx_fallback', side_effect=lambda src, dst, *args: make_docx(dst, text='')):
            with self.assertRaises(ValueError):
                convert(self.pdf, 'docx', self.root)
        self.assertFalse((self.root / 'sample.docx').exists())
        self.assertFalse(list(self.root.glob('.converter-*')))

    def test_output_corruption_is_rejected(self):
        for source, fmt in [(self.docx, 'pdf'), (self.pdf, 'docx')]:
            patch_target = '_convert' if fmt == 'pdf' else '_pdf_to_docx_fallback'
            with self.subTest(fmt=fmt), patch.object(document, patch_target, side_effect=lambda src, dst, *args: Path(dst).write_bytes(b'broken')):
                with self.assertRaises(ValueError):
                    convert(source, fmt, self.root)

    def test_missing_software_has_actionable_error(self):
        with patch.object(document, 'backend', return_value=(None, None)):
            for source, fmt in [(self.docx, 'pdf')]:
                with self.assertRaises(ValueError):
                    convert(source, fmt, self.root)

    def test_no_output_with_successful_exit_is_rejected(self):
        with patch.object(document, 'backend', return_value=('Word', None)), patch.object(document, '_run_word'):
            with self.assertRaises(ValueError):
                convert(self.docx, 'pdf', self.root)

    def test_word_failure_does_not_fallback(self):
        with patch.object(document, 'backend', return_value=('Word', None)), patch.object(document, '_run_word', side_effect=ValueError('failed')), patch.object(document, '_run_libreoffice') as fallback:
            with self.assertRaises(ValueError):
                convert(self.docx, 'pdf', self.root)
            fallback.assert_not_called()

    def test_cancel_after_conversion_never_publishes_output(self):
        cancel = threading.Event()
        def output(src, dst, *args):
            make_docx(dst)
            cancel.set()
        with patch.object(document, '_pdf_to_docx_fallback', side_effect=output):
            with self.assertRaises(Cancelled):
                convert(self.pdf, 'docx', self.root, cancel=cancel)
        self.assertFalse((self.root / 'sample.docx').exists())

    def test_word_cancel_requests_cleanup(self):
        process = Mock()
        process.poll.return_value = None
        cancel = threading.Event()
        cancel.set()
        with patch.object(document.subprocess, 'Popen', return_value=process), patch.object(document, '_stop_owned_word') as cleanup:
            with self.assertRaises(Cancelled):
                document._run_word(self.docx, self.root / 'out.pdf', 'docx-to-pdf', cancel)
            cleanup.assert_called_once()
            process.wait.assert_any_call(timeout=3)

    def test_word_timeout_requests_cleanup(self):
        process = Mock()
        process.poll.return_value = None
        with patch.object(document.subprocess, 'Popen', return_value=process), patch.object(document.time, 'monotonic', side_effect=[0, 121]), patch.object(document, '_stop_owned_word') as cleanup:
            with self.assertRaises(ValueError):
                document._run_word(self.docx, self.root / 'out.pdf', 'docx-to-pdf', threading.Event())
            cleanup.assert_called_once()

    def test_quality_notes_and_normalization(self):
        self.assertTrue(imperfect_for_extension('.DOCX', '.PDF'))
        self.assertTrue(imperfect_for_extension('.PDF', '.DOCX'))
        self.assertIn('OCR', document.quality_note('.PDF', 'DOCX'))
        self.assertFalse(imperfect_for_extension('png', 'pdf'))
        self.assertEqual(document.quality_note('.png', 'pdf'), '')


if __name__ == '__main__':
    unittest.main()
