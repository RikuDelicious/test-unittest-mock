import re
import unittest.mock
from unittest.mock import Mock

import pytest

"""
Mockクラスはモックオブジェクトの基底クラスである。
非情に柔軟性が高く、
幅広いユースケースでMockクラス及びその派生クラスのオブジェクトが使われる。
"""


def test_instantiating_mock():
    mock = Mock()
    assert isinstance(mock, Mock)


def test_mock_attributes_creation():
    """
    モックオブジェクトは置き換え元の属性やメソッドの振る舞いを模倣するために、
    任意の属性にアクセスした時にその場でその属性を生成する。
    この時、生成された属性、及びメソッドの戻り値もまたモックオブジェクトである。
    """
    mock = Mock()

    assert isinstance(mock.attr_1, Mock)
    assert isinstance(mock.method_1(), Mock)


def test_patching_library():
    """
    例えばライブラリ自体をモックオブジェクトに置き換えることができる。
    モックオブジェクトで元のライブラリと同じメソッドを呼び出すと、
    その場でメソッドを生成する。
    モックが作成したメソッドは元のメソッドと違い、いかなる引数でも受け取る。
    また、メソッドの戻り値はモックオブジェクトである。
    """
    json = Mock()

    assert isinstance(json.dumps(), Mock)
    assert isinstance(json.dumps("hogehoge"), Mock)
    assert isinstance(json.dumps(1, 2, 3, 4, 5, 6), Mock)


def test_mock_method_recursion():
    """
    モックオブジェクトが生成したメソッドの戻り値はモックオブジェクトなので、
    その呼び出し結果もまたモックオブジェクトである。
    この性質を利用して何らかのメソッドチェーンも模倣することができる。
    """
    json = Mock()

    assert isinstance(json.loads('{"K": "V"}').get("k"), Mock)


def test_mock_assert_called():
    """
    モックオブジェクトにはそれをどのように使用したかという情報が記録される。
    例えばあるモックオブジェクトを呼び出した場合、
    そのオブジェクトのMock.assert_called()メソッド等を使って
    呼び出したかどうかについて検証することができる。

    Mock.assert_called():
    モックが少なくとも一度は呼び出されたことを検証する。
    """
    json = Mock()
    json.loads('{"key": "value"}')

    json.loads.assert_called()
    with pytest.raises(AssertionError, match="Expected 'dumps' to have been called."):
        json.dumps.assert_called()


def test_mock_assert_called_once():
    """
    Mock.assert_called_once()
    モックが一度のみ呼び出されたことを検証する
    """
    json = Mock()
    json.loads('{"key": "value"}')
    json.loads.assert_called_once()

    json.loads('{"hoge": "huga"}')
    with pytest.raises(
        AssertionError,
        match="Expected 'loads' to have been called once. Called 2 times.",
    ):
        json.loads.assert_called_once()


def test_mock_assert_called_with():
    """
    Mock.assert_called_with(*args, **kwargs)
    直前のモックの呼び出しが↑の引数で呼び出されたかどうかを検証する
    """
    json = Mock()
    json.loads('{"key": "value"}', hoge="fuga")
    json.loads.assert_called_with('{"key": "value"}', hoge="fuga")
    with pytest.raises(AssertionError, match="expected call not found."):
        json.loads.assert_called_with('{"key": "value"}')


def test_mock_assert_called_once_with():
    """
    Mock.assert_called_once_with(*args, **kwargs)
    モックが一度だけ呼び出されており、かつ↑の引数で呼び出されたかどうかを検証する
    """
    json = Mock()
    json.loads('{"key": "value"}', hoge="fuga")
    json.loads.assert_called_once_with('{"key": "value"}', hoge="fuga")

    json.loads('{"key": "value"}', hoge="fuga")
    with pytest.raises(
        AssertionError, match="Expected 'loads' to be called once. Called 2 times."
    ):
        json.loads.assert_called_once_with('{"key": "value"}', hoge="fuga")


def test_mock_assert_not_called():
    """
    Mock.assert_not_called()
    モックが一度も呼び出されなかったことを確認する
    """
    json = Mock()
    json.loads.assert_not_called()

    json.loads('{"key": "value"}', hoge="fuga")
    with pytest.raises(
        AssertionError,
        match="Expected 'loads' to not have been called. Called 1 times.",
    ):
        json.loads.assert_not_called()


def test_mock_call_count():
    """
    Mock.call_count
    モックを呼び出した回数を保持する属性
    """
    json = Mock()
    json.loads('{"key": "value"}', hoge="fuga")
    json.loads('{"key": "value"}')
    json.loads(hoge="fuga")

    assert json.loads.call_count == 3


def test_mock_call_args():
    """
    Mock.call_args
    直前のモック呼び出し時の引数を保持する属性
    モック呼び出しに関する情報はunittest.mock.callオブジェクトで保持される
    -> 一度も呼び出していなければNoneとなる
    """
    json = Mock()
    json.loads('{"key": "value"}', hoge="fuga")
    assert json.loads.call_args == unittest.mock.call('{"key": "value"}', hoge="fuga")
    assert json.dumps.call_args is None


def test_mock_call_args_list():
    """
    Mock.call_args_list
    モックの呼び出し情報をリストで保持する属性
    モックを呼び出した順にリストにcallオブジェクトが追加される
    一度も呼び出していない場合は空のリストが返される
    """
    json = Mock()
    json.loads('{"key": "value"}', hoge="fuga")
    json.loads('{"key": "value"}')
    json.loads(hoge="fuga")

    assert json.loads.call_args_list == [
        unittest.mock.call('{"key": "value"}', hoge="fuga"),
        unittest.mock.call('{"key": "value"}'),
        unittest.mock.call(hoge="fuga"),
    ]
    assert json.dumps.call_args_list == []


def test_mock_method_calls():
    """
    Mock.method_calls
    モックオブジェクトの属性やメソッドの呼び出し情報をリストで保持する属性
    モックオブジェクトの属性が持つメソッドの呼び出しも再帰的に記録する。
    あるメソッドの戻り値から派生したメソッド呼び出しや、
    モックオブジェクト自身の呼び出しに関する情報は保持されない。
    """
    json = Mock()
    json.loads("call json.loads() 1")
    json.loads("call json.loads() 2")
    json.some_attr.some_method("call json.some_attr.some_method")
    json.other_attr.other_attr_attr.some_method(
        "call json.other_attr.other_attr_attr.some_method"
    )

    json.loads("call json.loads() 3").get("this call isn't tracked.")
    json("this call isn't tracked.")

    assert json.method_calls == [
        unittest.mock.call.loads("call json.loads() 1"),
        unittest.mock.call.loads("call json.loads() 2"),
        unittest.mock.call.some_attr.some_method("call json.some_attr.some_method"),
        unittest.mock.call.other_attr.other_attr_attr.some_method(
            "call json.other_attr.other_attr_attr.some_method"
        ),
        unittest.mock.call.loads("call json.loads() 3"),
    ]


def test_mock_return_value():
    """
    Mock.return_value
    この属性に任意の値を代入することで、
    モックオブジェクトを呼び出したときの戻り値を設定する
    テストで一部のメソッドの呼び出し結果を制御したい場合にこの仕組みを利用する
    """
    json = Mock()
    json.loads.return_value = {"key1": "value1", "key2": "value2"}
    assert json.loads("hoge") == {"key1": "value1", "key2": "value2"}


def test_mock_side_effect():
    """
    Mock.side_effect
    この属性に任意の例外クラスまたは関数を代入することで、
    モックオブジェクトを呼び出したときに例外が発生または関数が実行される
    関数を設定した場合、モックオブジェクト呼び出し時の引数がside_effectにも渡される
    モックのメソッド実行時の副作用を作りたい場合にこの仕組みを利用する
    尚、side_effectにNoneを設定すると副作用がクリアされる。
    """
    json = Mock()

    # 例外クラスを設定
    json.loads.side_effect = TypeError
    # assertion
    with pytest.raises(TypeError):
        json.loads("fuga")

    # 関数を設定
    side_effect_result = None

    def side_effect(arg):
        nonlocal side_effect_result
        side_effect_result = arg

    json.dumps.side_effect = side_effect
    json.dumps("hoge")
    # assertion
    assert side_effect_result == "hoge"

    # Noneを設定
    json.loads.side_effect = None
    try:
        json.loads("foo")
    except TypeError:
        pytest.fail(
            "TypeError occured when the mock was called although the side_effect was set None."
        )


def test_mock_side_effect_return():
    """
    side_effectの関数の戻り値がunittest.mock.DEFAULTの場合、
    モックオブジェクト呼び出しの結果は新しいモックもしくはMock.return_valueとなる
    上記以外の何らかの値を返す場合（もしくはreturn文が無い->None値の場合）、
    モックオブジェクトの呼び出し結果もその値となる。
    この仕組みを利用してモックオブジェクトの呼び出し結果をより動的に制御できる。
    """

    def side_effect_1():
        return unittest.mock.DEFAULT

    def side_effect_2():
        return "hoge"

    def side_effect_3():
        pass

    mock = Mock()

    mock.method_1.side_effect = side_effect_1
    assert isinstance(mock.method_1(), Mock)

    mock.method_2.return_value = "fuga"
    mock.method_2.side_effect = side_effect_1
    assert mock.method_2() == "fuga"

    mock.method_3.side_effect = side_effect_2
    assert mock.method_3() == "hoge"

    mock.method_4.return_value = "foo"
    mock.method_4.side_effect = side_effect_2
    assert mock.method_4() == "hoge"

    mock.method_5.side_effect = side_effect_3
    assert mock.method_5() == None


def test_mock_side_effect_iterable():
    """
    Mock.side_effect属性にはイテラブルオブジェクトを設定することができる
    この場合、モックオブジェクトを呼び出すたびにイテラブルの次の要素を返すようになる
    モック呼び出し時、イテラブルの要素が例外クラスの場合は例外が発生、
    unittest.mock.DEFAULTの場合は新しいモックオブジェクトまたはMock.return_valueが返され、
    それ以外の場合は要素の値がそのままモック呼び出しの戻り値として返される
    """
    mock = Mock()
    mock.method_1.side_effect = [
        TypeError,
        unittest.mock.DEFAULT,
        {"key1": "value1", "key2": "value2"},
    ]

    with pytest.raises(TypeError):
        mock.method_1()

    assert isinstance(mock.method_1(), Mock)
    assert mock.method_1() == {"key1": "value1", "key2": "value2"}


def test_mock_configuring():
    """
    モック初期化時にside_effect、return_value、name等の属性の設定を行える
    nameはrepr()メソッド実行時に表示されるモックの名前であり、
    初期化時にしか設定することが出来ない。
    """
    mock = Mock(side_effect=Exception)
    with pytest.raises(Exception):
        mock()

    mock = Mock(return_value="hoge", name="fuga")
    assert mock() == "hoge"
    assert re.match("<Mock name='fuga'", repr(mock)) is not None

    # 補足
    # mock.name属性にアクセスするとモックオブジェクトが新規作成される
    assert isinstance(mock.name, Mock)
    # mock.name属性に直接モック名を設定しても、
    # 属性の値は設定されるが、モックの名前としては設定されない
    mock.name = "John"
    assert mock.name == "John"
    assert re.match("<Mock name='fuga'", repr(mock)) is not None


def test_mock_configure_mock():
    """
    Mock.configure_mock(**kwargs)
    モック初期化後、このメソッドで
    キーワード引数によりモックの各属性を設定できる
    尚、このメソッドではnameの設定は出来ない
    """
    mock = Mock()
    mock.configure_mock(side_effect=Exception)
    with pytest.raises(Exception):
        mock()

    mock.configure_mock(side_effect=None, return_value="hoge")
    assert mock() == "hoge"


def test_mock_configuring_from_dict():
    """
    モックのコンストラクタ及びMock.configure_mock()メソッドの引数に
    辞書を展開して渡すことでモックオブジェクトの属性の設定ができる。
    その際、モックオブジェクトが持つメソッドの属性もドットで繋ぐことで設定できる。
    """
    config = {
        "return_value": 12345,
        "method_1.side_effect": TypeError,
        "method_2.return_value": "hoge",
    }

    mock_1 = Mock(**config)
    assert mock_1() == 12345
    with pytest.raises(TypeError):
        mock_1.method_1()
    assert mock_1.method_2() == "hoge"

    mock_2 = Mock()
    mock_2.configure_mock(**config)
    assert mock_2() == 12345
    with pytest.raises(TypeError):
        mock_2.method_1()
    assert mock_2.method_2() == "hoge"
