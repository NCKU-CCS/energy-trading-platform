# -*- coding: utf-8 -*-
import pytest
import requests

def setup_function(function):
    print("setting up", function)

def test_getconn(capsys):

    with pytest.raises(Exception) as e:
        res = requests.get("http://140.116.247.120:5000/", timeout=1)
        print(str(e))

        with capsys.disabled():
            print("HTTP Status: %s" % res.status_code)
            print("HTTP Response: %s" % res.text)
        assert res.ok

'''    try:
        res = requests.get("http://140.116.247.120:5000/", timeout=1)

        with capsys.disabled():
            print(res.status_code)
            print(res.text)
        assert res.ok

    except Exception as e:
        pytest.fail(msg = str(e), pytrace=True)
        return'''

