from Artha.data_process import *
# import Artha
import pytest


@pytest.mark.parametrize("initial_text, trimmed_text", [
    ("@test I love pie", "I love pie"),
    ("@test1 @test2 I love pie", "I love pie"),
    ("@test1", ""),
    ("@test1 @test2", ""),
    ("@test1 @test2 @test3", ""),
])
def test_remove_tags(initial_text, trimmed_text):
    assert remove_tags(initial_text) == trimmed_text
