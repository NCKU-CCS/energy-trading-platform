# -*- coding: utf-8 -*-

import pytest

@pytest.fixture()
def hello_world():
    return "hello_world"


def test_h_in_hello_world(hello_world):
    assert "h" in hello_world


def test_w_in_hello_world(hello_world):
    assert "w" in hello_world
