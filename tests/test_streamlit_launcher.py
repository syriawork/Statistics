import os
import tempfile
import unittest

import data_entry_gui


class StreamlitLauncherCommandTests(unittest.TestCase):
    def test_prefers_packaged_launcher_exe_when_available(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_exe = os.path.join(tmpdir, 'launcher.exe')
            with open(launcher_exe, 'w', encoding='utf-8'):
                pass

            cmd = data_entry_gui._build_streamlit_launch_command(
                tmpdir,
                8501,
                frozen=True,
                executable_path=r'C:\app\data_entry_gui.exe',
            )

            self.assertEqual(cmd, [launcher_exe, '--server', '8501'])

    def test_falls_back_to_launcher_py_when_not_frozen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_py = os.path.join(tmpdir, 'launcher.py')
            with open(launcher_py, 'w', encoding='utf-8'):
                pass

            cmd = data_entry_gui._build_streamlit_launch_command(
                tmpdir,
                8502,
                frozen=False,
                executable_path=r'C:\Python\python.exe',
            )

            self.assertEqual(cmd, [r'C:\Python\python.exe', launcher_py, '--server', '8502'])


if __name__ == '__main__':
    unittest.main()
