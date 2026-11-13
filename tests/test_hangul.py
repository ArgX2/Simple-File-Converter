import _support
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
import pymupdf
import hangul
from engine import convert, imperfect_for_extension, inspect, Cancelled


class HangulTests(unittest.TestCase):
    def test_formats_and_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            for extension, expected in [('hwp', ['hwpx', 'pdf']), ('hwpx', ['hwp', 'pdf'])]:
                source = Path(temp) / ('sample.' + extension)
                source.write_bytes(b'placeholder')
                self.assertEqual(inspect(source)['formats'], expected)
                for target in expected:
                    self.assertTrue(imperfect_for_extension(extension, target))
            self.assertTrue(imperfect_for_extension('pdf', 'hwp'))
            self.assertTrue(imperfect_for_extension('pdf', 'hwpx'))

    def test_missing_engine_and_cancellation(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / 'missing.exe'
            with patch.object(hangul, 'executable', return_value=missing):
                with self.assertRaises(ValueError):
                    hangul.convert_hangul('in.hwp', 'out.pdf', threading.Event(), lambda _: None)
            cancel = threading.Event()
            cancel.set()
            with patch.object(hangul, 'executable', return_value=Path(__file__)):
                with self.assertRaises(Cancelled):
                    hangul.convert_hangul('in.hwp', 'out.pdf', cancel, lambda _: None)

    @unittest.skipUnless(hangul.executable().is_file(), 'rhwp is not prepared')
    def test_real_round_trips(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'sample.pdf'
            with pymupdf.open() as pdf:
                pdf.new_page().insert_text((72, 72), 'Sample content')
                pdf.save(source)
            for ext, other in [('hwp', 'hwpx'), ('hwpx', 'hwp')]:
                with self.subTest(ext=ext):
                    result = convert(source, ext, root)
                    self.assertTrue(convert(result, other, root).is_file())
                    with pymupdf.open(convert(result, 'pdf', root)) as pdf:
                        self.assertEqual(len(pdf), 1)


if __name__ == '__main__':
    unittest.main()
