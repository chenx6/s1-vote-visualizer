from time import sleep

from schedule import every, run_pending


def update_db():
    """TODO 完成每季度定时抓取"""
    pass


every().day.at("08:88").do(update_db)

while True:
    run_pending()
    sleep(1)
