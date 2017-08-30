from __future__ import absolute_import
import os

import pytest

from pyq import q


def test_inside_ci():
    # Test designed for Gitlab CI
    if 'GITLAB_CI' not in os.environ:
        pytest.skip("This test designed for Gitlab CI only.")

    qver, qmin = os.environ.get('KDB_VER', '0.0').split('.')
    assert q(".z.K") == int(qver) + 0.1 * int(qmin)
