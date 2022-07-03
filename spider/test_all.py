from .item import VoteItem, VotePost


def test_pipeline():
    from datetime import datetime
    from .pipeline import pipeline

    pipeline([VotePost("", "", 10, datetime.now()), [VoteItem("", 10, 1.0)]])
