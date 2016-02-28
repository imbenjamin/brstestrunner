import unittest
import brstestrunner


class TestMain(unittest.TestCase):
    def test_no_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            brstestrunner.main([])
        self.assertEqual(cm.exception.code, 2)

    def test_no_ip(self):
        with self.assertRaises(SystemExit) as cm:
            brstestrunner.main(['-v'])
        self.assertEqual(cm.exception.code, 2)

    def test_help(self):
        self.assertRaises(SystemExit, brstestrunner.main, ['-h'])

    def test_help_with_other_arguments(self):
        self.assertRaises(SystemExit, brstestrunner.main, ['-h', '-v', '--ip', '192.168.1.78'])

if __name__ == '__main__':
    unittest.main(buffer=False)
