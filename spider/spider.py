from re import compile as compile_re
from typing import List, Set, Tuple
from json import load
from pathlib import Path

from httpx import AsyncClient
from bs4 import BeautifulSoup
from arrow import get
from tqdm.asyncio import tqdm

from .exchange import get_exchange
from .item import VotePost, VoteItem

HOST = "https://bbs.saraba1st.com/2b"
vote_count = compile_re(r"共有 (\d+) 人参与投票")
split_count_perc = compile_re(r"([\d|.]+)% \((\d+)\)")
remove_no = compile_re(r"\d+. \xa0")
clean_title = compile_re(r"【.+】([^（]+)(（\d）){0,1}")


def process_post_list(text: str, in_title: str) -> List[str]:
    """解析发帖列表"""
    soup = BeautifulSoup(text, features="html.parser")
    # 从 a 标签中获取帖子链接
    return [
        i["href"]
        for i in soup.find_all("a", href=compile_re("thread-.+"))
        if not i.text.isnumeric() and in_title in i.text and "汇总" not in i.text
    ]


def process_vote_post(href: str, text: str) -> Tuple[VotePost, List[VoteItem]]:
    """解析投票数据"""
    soup = BeautifulSoup(text, features="html.parser")
    # 标题
    title_elem = soup.select_one("#thread_subject")
    assert title_elem
    m = clean_title.search(title_elem.text)
    assert m
    tltle = m.group(1)
    # 发帖时间
    post_time_s = soup.find("em", id=compile_re("authorposton.+"))
    assert post_time_s
    post_time = get(post_time_s.text, "发表于 YYYY-M-D HH:mm").datetime

    # 投票相关
    poll = soup.select_one('form[id="poll"]')
    assert poll, href
    # 获取投票人数
    poll_info = poll.select_one('div[class="pinf"]')
    assert poll_info
    vote_count_result = poll_info.text
    vote_count_result = vote_count.findall(vote_count_result)[0]
    # 解析投票表格
    poll_result = poll.select_one('table[summary="poll panel"]')
    assert poll_result
    tds = poll_result.select("td")
    votes: list[VoteItem] = []
    # 寄，投票没结束时候，会多出一个选择框，得调整步进次数
    td_step = 4
    td_start = 0
    td_class = tds[0].attrs.get("class")
    assert td_class
    if "pslt" in td_class:
        td_step = 6
        td_start = 1
    for i in range(0, len(tds) - 1, td_step):
        curr_td = tds[i + td_start]
        # 筛选出真正的投票表格
        curr_attrs = curr_td.attrs.get("class", "")
        if "pvt" not in curr_attrs:
            continue
        # 投票名称
        name = curr_td.text.strip()
        name = remove_no.sub("", name)
        # 投票数量
        vote_count_info_s = split_count_perc.findall(tds[i + td_start * 2 + 3].text)
        if not vote_count_info_s:
            continue
        perc_s, count_s = vote_count_info_s[0]
        votes.append(VoteItem(name, int(count_s), float(perc_s)))
    return VotePost(href, tltle, int(vote_count_result), post_time), votes


async def fetch_post_list(client: AsyncClient, uid: int, page: int):
    """获取发帖列表"""
    resp = await client.get(
        f"{HOST}/home.php?mod=space&uid={uid}&do=thread&view=me&order=dateline&from=space",
        params={"page": page},
    )
    return resp.text


async def fetch_post(client: AsyncClient, href: str):
    """获取帖子内容"""
    # 看下有没有缓存，如果有缓存就先用缓存，减小服务器负担
    cachefile = Path(f"data/{href}")
    if cachefile.exists():
        return cachefile.read_text()
    else:
        resp = await client.get(f"{HOST}/{href}")
        cachefile.write_text(resp.text)
        return resp.text


async def spider(uid: int, title_filter: str):
    """爬虫主函数"""
    exc = get_exchange("pipeline")
    with open("data/cookies.json", "r") as f:
        cookies = load(f)
    async with AsyncClient(cookies=cookies) as client:
        # 获取投票贴链接
        posts: Set[str] = set()
        home_page = 1
        prog = tqdm(desc="processing post list")
        while True:
            text = await fetch_post_list(client, uid, home_page)
            post_list = process_post_list(text, title_filter)
            if len(post_list) == 0:
                break
            posts.update(post_list)
            home_page += 1
            prog.update(1)
        prog.close()
        # 获取和解析投票贴数据
        texts = await tqdm.gather(*[fetch_post(client, href) for href in posts])
        for href, text in tqdm(zip(posts, texts)):
            vote_post, votes = process_vote_post(href, text)
            exc.send((vote_post, votes))
