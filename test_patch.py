from unittest.mock import MagicMock, Mock, patch

import pytest
from requests.exceptions import Timeout

from sample import get_weather_reports, requests

"""
unittest.mock.patch()
オブジェクトを簡単にモック化する関数
モジュールを指定し、そのモジュール内のオブジェクトをモックに置き換える
通常、デコレータやコンテキストマネージャーとして使う。
"""


@patch("sample.requests")
def test_get_weather_reports_200(mock_requests):
    """
    patch(target, new=DEFAULT, ...)
    patch()デコレータを適用し、targetにモジュールパスの形式でオブジェクトを指定することで、
    この関数内ではそのオブジェクトをモックオブジェクトに置き換える。
    newオプションを省略すると、置き換えたモックオブジェクトはこの関数の追加の引数として渡される
    """
    mock_response = Mock(
        **{
            "json.return_value": {
                "Tuesday": "rainy",
                "Wednesday": "snowy",
                "Thursday": "rainy",
            },
            "status_code": 200,
        }
    )
    mock_requests.get.return_value = mock_response

    assert get_weather_reports() == {
        "Tuesday": "rainy",
        "Wednesday": "snowy",
        "Thursday": "rainy",
    }
    mock_requests.get.assert_called_once()
    mock_response.json.assert_called_once()


@patch("sample.requests")
def test_get_weather_reports_timeout(mock_requests):
    mock_requests.get.side_effect = Timeout
    with pytest.raises(Timeout):
        get_weather_reports()
        mock_requests.get.assert_called_once()


@patch("sample.requests")
def test_patch_magic_mock(mock_requests):
    """
    patch()はMockのサブクラスであるMagicMockのインスタンスを返す。
    MagicMockは__len__(), __str__(), __iter__() 等のマジックメソッドを
    デフォルトで実装してくれるという利便性がある。
    """
    assert isinstance(mock_requests, MagicMock)


def test_patch_as_context_manager():
    """
    patch()はコンテキストマネージャーとしても使える
    この場合、with文を抜けるとオブジェクトの置き換えは元に戻る
    一部のスコープでのみモックを使いたい場合にこの仕組みを利用する
    """
    with patch("sample.requests") as mock_requests:
        mock_requests.get.side_effect = Timeout
        with pytest.raises(Timeout):
            get_weather_reports()
            mock_requests.get.assert_called_once()


@patch.object(requests, "get", side_effect=Timeout)
def test_patch_object(mock_requests):
    """
    patch.object()でオブジェクトの一部の属性のみをモックに置き換えることができる。
    第一引数にはターゲットとするオブジェクト、第二引数にはモックに置き換える属性を指定する。
    また、モック生成のための任意のキーワード引数を渡すことができる。
    newキーワード引数を省略すると、生成されたモックが関数の追加の引数として渡される。
    この例では、sampleモジュールのrequestsのgetメソッドをモックに置き換えて、
    side_effectに例外Timeoutを設定。生成したモックはmock_requestsで渡されている。
    """
    with pytest.raises(Timeout):
        get_weather_reports()


def test_patch_object_context_manager():
    with patch.object(requests, "get", side_effect=Timeout):
        with pytest.raises(Timeout):
            get_weather_reports()
