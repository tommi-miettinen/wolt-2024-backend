import os
import sys

current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
os.chdir(root_dir)
sys.path.append(root_dir)


def test_dummy():
    assert True is True
