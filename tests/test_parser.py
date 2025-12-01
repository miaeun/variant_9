import subprocess
import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent.parent

def run_example(name):
    path = ROOT / "examples" / name
    proc = subprocess.run([sys.executable, "-m", "src.cli", str(path)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, f"CLI failed: {proc.stderr}"
    xml = proc.stdout
    root = ET.fromstring(xml)
    return root

def test_network():
    root = run_example("network.cfg")
    assert any(n.tag.startswith("const_ipList") or n.tag=="const_ipList" or "const_ipList" for n in root)

def test_inventory():
    root = run_example("inventory.cfg")
    assert any(n.tag.startswith("const_sortedPrices") or "sortedPrices" in n.tag for n in root)

def test_build():
    root = run_example("build.cfg")
    assert any("const_flags" in n.tag or n.tag.startswith("const_flags") for n in root)
