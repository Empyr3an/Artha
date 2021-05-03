from Artha.data_process import *
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


def test_follow_edges():
    selected_people = ["BTC_JackSparrow", "razoreth", "Nostranomist", "CryptoKaleo", "nebraskangooner", "Rager", "SavageBTC"]
    selected_follows = follow_edges(selected_people, .5)
    s = 0
    for i in selected_follows:
        if i[0] == "BTC_JackSparrow":
            s += i[4]
    assert round(s, 1) == .5
