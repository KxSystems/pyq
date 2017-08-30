# These tests can only be run from the package source directory
import pytest
import os
import sys
import subprocess
import re

pytestmark = pytest.mark.skipif("not os.path.exists('setup.py')")

python = sys.executable

version_re = re.compile(r'^\d\.\d.*$')  # TODO: Come up with a more restrictive RE.

def test_version():
    v = subprocess.check_output([python, 'setup.py', '--version']).decode()
    assert version_re.match(v)

# For now, just test that the build succeeds.
# TODO: test under different scenarios w.r.t. QHOME, etc.
def test_build():
    rc = subprocess.call([python, 'setup.py', 'build'])
    assert rc == 0

def test_config(tmpdir):
    dest = tmpdir.join('setup.cfg')
    rc = subprocess.call([python, 'setup.py', 'config',
                          '--python-dll', 'faked',
                          '--dest', dest.strpath,
                          '--write'])
    assert rc == 0
    assert dest.read().startswith('[config]')
