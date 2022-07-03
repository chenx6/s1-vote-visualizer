from typing import NamedTuple
from datetime import datetime


class VotePost(NamedTuple):
    """投票帖子"""

    url: str
    title: str
    total_vote: int  # 总投票数
    time: datetime  # 投票创建时间


class VoteItem(NamedTuple):
    """投票项"""

    name: str
    count: int  # 投票数
    percentage: float  # 投票占总投票的百分比
