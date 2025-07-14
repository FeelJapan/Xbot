import pytest

def test_simple():
    """シンプルなテスト"""
    assert 1 + 1 == 2

def test_string():
    """文字列テスト"""
    assert "hello" + " world" == "hello world"

def test_list():
    """リストテスト"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1 