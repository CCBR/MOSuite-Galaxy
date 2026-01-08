# tests/test_cli.py
import subprocess
import sys
import shutil

from galaxysynth.util import get_version


def _cli_cmd(*args):
    exe = shutil.which("galaxysynth")
    if exe:
        return [exe, *args]
    return [sys.executable, "-m", "galaxysynth.galaxy_xml_synthesizer", *args]


def run_cmd(*args):
    return subprocess.run(_cli_cmd(*args), capture_output=True, text=True)


def test_help_works():
    res = run_cmd("--help")
    assert res.returncode == 0
    assert "usage:" in res.stdout.lower()
    assert "--version" in res.stdout


def test_version_matches_package():
    res = run_cmd("--version")
    expected = get_version()
    # argparse's version action prints to stdout
    output = (res.stdout or res.stderr).strip()
    assert res.returncode == 0
    assert expected in output
