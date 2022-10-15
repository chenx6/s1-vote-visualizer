from asyncio import run
from traceback import print_exc

from spider.exchange import get_exchange
from spider.spider import spider
from spider.pipeline import pipeline


async def main():
    pipeline_exc = get_exchange("pipeline")
    pipeline_exc.attach(pipeline)
    try:
        # await spider(212958, "三话定命！")
        await spider(191547, "不补可惜")
        await spider(191547, "免补避雷")
    except Exception as e:
        print(e)
        print_exc()


run(main())
