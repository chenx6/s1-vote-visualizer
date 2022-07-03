from sqlite3 import connect

from rich.console import Console
from rich.table import Table

conn = connect("./data/data.db")
cursor = conn.cursor()
r = cursor.execute(
    """
    SELECT title, name, count, percentage
    FROM vote_item, vote_post
    WHERE vote_post.id = vote_item.vote_id
        AND title LIKE '%2022%'
    ORDER BY count DESC 
    LIMIT 30;
    """
)

table = Table(title="S1 投票统计（票数排序）")
table.add_column("Vote title")
table.add_column("Name")
table.add_column("Vote count")
table.add_column("Percentage")
for i in r:
    table.add_row(*[str(c) for c in i])
console = Console()
console.print(table)
