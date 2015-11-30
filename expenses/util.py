# -*- coding: utf-8 -*-
"""Utility functions."""

from base64 import urlsafe_b64encode
import os


def random_string(size):
    """Generate a random base64 string from urandom."""
    if size < 0:
        raise ValueError('Negative lengths are not allowed')
    elif size % 4 != 0:
        raise ValueError('The length must be a multiple of 4')
    n_bytes = size * 3 // 4
    return urlsafe_b64encode(os.urandom(n_bytes)).decode()
