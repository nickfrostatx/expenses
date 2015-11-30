# -*- coding: utf-8 -*-
"""Test utility functions."""

from expenses.util import random_string
import pytest


def test_random_string():
    for n in (-2, -1):
        with pytest.raises(ValueError) as exc:
            random_string(n)
        assert 'Negative lengths are not allowed' in str(exc)

    for n in (1, 1.5, 3, 39):
        with pytest.raises(ValueError) as exc:
            random_string(n)
        assert 'The length must be a multiple of 4' in str(exc)

    for n in (0, 4, 8, 40):
        assert isinstance(random_string(n), type(u''))
        assert len(random_string(n)) == n
