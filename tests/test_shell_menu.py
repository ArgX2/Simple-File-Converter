import _support
import unittest
from unittest.mock import patch
from fake_registry import Registry
import shell_menu


class ShellMenuTests(unittest.TestCase):
    def setUp(self):
        self.registry = Registry()
        for name, value in [('winreg', self.registry), ('refresh', lambda: None),
                            ('launch_command', lambda: [r'C:\Example Folder\Simple File Converter.exe'])]:
            patcher = patch.object(shell_menu, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_submenu_contains_expected_image_formats(self):
        shell_menu.enable()
        self.assertTrue(shell_menu.is_enabled())
        with self.registry.OpenKey(1, shell_menu.menu_key('png')) as key:
            self.assertEqual(self.registry.QueryValueEx(key, 'MUIVerb')[0], 'Simple File Converter')
            group = self.registry.QueryValueEx(key, 'ExtendedSubCommandsKey')[0]
        commands = []
        for path, values in self.registry.data.items():
            if path.startswith(shell_menu.CLASSES + '\\' + group + '\\shell\\') and path.endswith('\\command'):
                commands.append(values[''][0])
        self.assertEqual(len(commands), 6)
        for fmt in ['jpg', 'webp', 'bmp', 'tiff', 'gif', 'pdf']:
            expected = f'"C:\\Example Folder\\Simple File Converter.exe" --context-convert {fmt} "%1"'
            self.assertIn(expected, commands)

    def test_disable_removes_only_owned_keys(self):
        unrelated = r'Software\Classes\UnrelatedApp'
        self.registry.CreateKeyEx(1, unrelated)
        shell_menu.enable()
        shell_menu.enable()
        shell_menu.disable()
        self.assertFalse(shell_menu.is_enabled())
        self.assertIn(unrelated, self.registry.data)
        self.assertFalse(any('SimpleFileConverter' in path for path in self.registry.data))

    def test_registration_failure_rolls_back(self):
        original = shell_menu.put
        count = 0
        def fail_after_two(path, values):
            nonlocal count
            count += 1
            if count == 3:
                raise PermissionError('test permission failure')
            original(path, values)
        with patch.object(shell_menu, 'put', fail_after_two):
            with self.assertRaises(PermissionError):
                shell_menu.enable()
        self.assertFalse(shell_menu.is_enabled())
        self.assertFalse(any('SimpleFileConverter' in path for path in self.registry.data))


if __name__ == '__main__':
    unittest.main()
