import unittest
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent / "interpreter"
sys.path.insert(0, str(src_path))

loader = unittest.TestLoader()
suite = loader.discover("tests", pattern="test_*.py")

runner = unittest.TextTestRunner()
runner.run(suite)
