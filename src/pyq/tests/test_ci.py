import os

from pyq import q

import pytest


def test_inside_ci():
    # Test designed for Gitlab CI
    if 'GITLAB_CI' not in os.environ:
        pytest.skip("This test designed for Gitlab CI only.")

    qmin = int(os.environ.get('QMIN', '0'))
    qver = int(os.environ.get('QVER', '0'))

    assert q(".z.K") == qver + 0.1 * qmin
