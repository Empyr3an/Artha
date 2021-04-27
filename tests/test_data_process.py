from Artha.data_process import *
import pytest


@pytest.mark.parametrize("initial_text, trimmed_text", [
    ("@test I love pie", "I love pie"),
    ("@test1 @test2 I love pie", "I love pie"),
    ("@test1", ""),
    ("@test1 @test2", ""),
    ("@test1 @test2 @test3", ""),
])
def test_remove_first_tag(initial_text, trimmed_text):
    assert remove_first_tags(initial_text) == trimmed_text
