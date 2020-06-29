# -*- coding: utf-8 -*-
import pytest
import requests


def setup_function(function):
    print("setting up", function)


def test_getconn(capsys):
    with pytest.raises(Exception) as e:
        res = requests.get("http://140.116.247.117:5000/", timeout=1)
        print(str(e))

        with capsys.disabled():
            print("HTTP Status: %s" % res.status_code)
            print("HTTP Response: %s" % res.text)
        assert res.ok
