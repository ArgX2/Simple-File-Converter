import _support
import hashlib
import tempfile
import threading
import unittest
from docx_fixture import make_docx
from pathlib import Path
from PIL import Image
import pymupdf
from pptx import Presentation
from engine import convert, inspect, Cancelled, imperfect_for_extension


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / '한글 & source.png'
        Image.new('RGBA', (41, 29), (20, 80, 180, 100)).save(self.image)

    def test_image_conversion_preserves_source(self):
        before = hashlib.sha256(self.image.read_bytes()).digest()
        result = convert(self.image, 'jpg', self.root)
        with Image.open(result) as image:
            self.assertEqual(image.size, (41, 29))
            self.assertEqual(image.mode, 'RGB')
        self.assertEqual(before, hashlib.sha256(self.image.read_bytes()).digest())

    def test_existing_output_is_not_overwritten(self):
        existing = self.image.with_suffix('.jpg')
        existing.write_bytes(b'keep this file')
        result = convert(self.image, 'jpg', self.root)
        self.assertNotEqual(result, existing)
        self.assertEqual(existing.read_bytes(), b'keep this file')

    def test_pdf_all_pages_and_slide_count(self):
        pdf = self.root / 'input.pdf'
        with pymupdf.open() as doc:
            for i in range(2):
                page = doc.new_page(width=160, height=120)
                page.insert_text((20, 50), f'Page {i + 1}')
            doc.save(pdf)
        pages = convert(pdf, 'png', self.root)
        self.assertEqual(len(list(pages.glob('*.png'))), 2)
        slides = convert(pdf, 'pptx', self.root)
        deck = Presentation(slides)
        self.assertEqual(len(deck.slides), 2)
        self.assertEqual(len(deck.slides[0].shapes), 1)
        self.assertNotIn('txt', inspect(pdf)['formats'])

    def test_cancel_leaves_no_partial_output(self):
        cancelled = threading.Event()
        cancelled.set()
        with self.assertRaises(Cancelled):
            convert(self.image, 'jpg', self.root, cancel=cancelled)
        self.assertFalse(self.image.with_suffix('.jpg').exists())
        self.assertFalse(list(self.root.glob('.converter-*')))

    def test_unsupported_output_and_corrupt_input(self):
        with self.assertRaises(ValueError):
            convert(self.image, 'mp3', self.root)
        corrupt = self.root / 'broken.png'
        corrupt.write_bytes(b'not an image')
        with self.assertRaises(Exception):
            inspect(corrupt)

    def test_docx_is_recognized_and_marked_as_imperfect(self):
        docx = self.root / 'document.docx'
        make_docx(docx)
        meta = inspect(docx)
        self.assertEqual(meta['kind'], 'document')
        self.assertEqual(meta['formats'], ['pdf'])
        self.assertTrue(imperfect_for_extension('docx', 'pdf'))
        self.assertTrue(imperfect_for_extension('pdf', 'docx'))

    def test_invalid_docx_is_rejected_before_conversion(self):
        docx = self.root / 'broken.docx'
        docx.write_bytes(b'not a Word package')
        with self.assertRaises(ValueError):
            inspect(docx)


if __name__ == '__main__':
    unittest.main()
