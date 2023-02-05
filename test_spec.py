from unittest.mock import Mock, patch

import pytest


class SomeClass:
    def __init__(self, title):
        self.title = title

    def method_1(self):
        return "SomeClass.method_1"

    def method_2(self, arg1, arg2):
        return arg1 + arg2

    def method_3(self):
        return self.title


def test_mock_spec_list():
    """
    モック初期化時に引数specに任意の属性名のリスト、クラス、またはオブジェクト
    を指定すると、属性名のリストまたはクラス/オブジェクトのメソッドのみを
    モック化するようになる。

    指定したもの以外の属性をメソッドとして呼び出そうとすると、
    AttributeErrorが発生する。
    尚、属性に直接値を入れてもエラーとはならない。
    """
    mock = Mock(spec=["attr_1", "attr_2"])
    assert isinstance(mock.attr_1(), Mock)
    assert isinstance(mock.attr_2(), Mock)
    with pytest.raises(AttributeError):
        mock.attr_3()

    mock.attr_4 = "hoge"
    assert mock.attr_4 == "hoge"


def test_mock_spec_class():
    mock = Mock(spec=SomeClass)
    assert mock.__class__ == SomeClass
    assert isinstance(mock, SomeClass)
    assert mock.method_1() != "SomeClass.method_1"
    assert isinstance(mock.method_1(), Mock)
    assert mock.method_2(1, 2) != 3
    assert isinstance(mock.method_2(), Mock)
    assert isinstance(mock.method_3(), Mock)
    with pytest.raises(AttributeError):
        mock.method_4()


def test_mock_spec_object():
    mock = Mock(spec=SomeClass("John Wick"))
    assert mock.__class__ == SomeClass
    assert isinstance(mock, SomeClass)
    assert mock.title != "John Wick"
    assert isinstance(mock.title, Mock)
    assert mock.method_1() != "SomeClass.method_1"
    assert isinstance(mock.method_1(), Mock)
    assert mock.method_2(1, 2) != 3
    assert isinstance(mock.method_2(), Mock)
    assert isinstance(mock.method_3(), Mock)
    with pytest.raises(AttributeError):
        mock.method_4()


from sample import Sample


@patch("sample.Sample", autospec=True)
def test_patch(mock):
    """
    patch()でautospec=Trueとすることにより、
    第一引数に指定したモジュールをspecとするモックがこの関数の引数に渡される。
    また、この場合は指定したモジュールのメソッド/関数と同じ引数を指定しないと
    TypeErrorが発生する。
    """
    assert mock.__class__ == Sample
    assert isinstance(mock, Sample)
    assert isinstance(mock.hoge(1, 2), Mock)
    with pytest.raises(TypeError):
        mock.hoge("hoge")
    with pytest.raises(AttributeError):
        mock.some_method()
