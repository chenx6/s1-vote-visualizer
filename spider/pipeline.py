from sqlite3 import connect

from .item import VoteItem, VotePost

conn = connect("./data/data.db")


def init_db():
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vote_post (
            id INTEGER PRIMARY KEY,
            url VARCHAR UNIQUE,
            title VARCHAR UNIQUE,
            total_vote INTEGER,
            time DATETIME
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vote_item (
            id INTEGER PRIMARY KEY,
            vote_id INTEGER,
            name VARCHAR,
            count INTEGER,
            percentage REAL,
            FOREIGN KEY(vote_id) REFERENCES vote_post(id)
        );
        """
    )
    conn.commit()


init_db()


def vote_post_pipeline(item: VotePost):
    """处理投票帖子的管道"""
    cursor = conn.cursor()
    # 存在一季度多个投票贴的情况，则返回已存在的帖子 id
    r = cursor.execute("SELECT id FROM vote_post WHERE title = ?", (item.title,))
    r = list(r)
    if len(r):
        return r[0][0]
    # 如果不存在则插入
    cursor.execute(
        "INSERT INTO vote_post (url, title, total_vote, time) VALUES (?, ?, ?, ?)", item
    )
    conn.commit()
    return cursor.lastrowid


def vote_item_pipeline(item: VoteItem, vote_id: int):
    """处理投票项的管道"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vote_item (name, count, percentage, vote_id) VALUES (?, ?, ?, ?)",
        (*item, vote_id),
    )
    conn.commit()


def pipeline(*item):
    """数据处理管道"""
    try:
        row_id = vote_post_pipeline(item[0])
    except Exception as e:
        print(e)
        return
    if not row_id:
        print("missing row_id?")
        row_id = 1
    [vote_item_pipeline(i, row_id) for i in item[1]]
