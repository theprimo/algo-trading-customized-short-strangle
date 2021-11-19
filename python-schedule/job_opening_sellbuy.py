# schedule - overnight close positions
# opening - fyers mine

import schedule

from practice.opening_samco_sellbuy import OpeningSellBuy


def task():
    # schedule.every(1).minutes.do(job)
    # schedule.every().hour.do(job)
    # schedule.every().day.at("10:30").do(job)
    # schedule.every(5).to(10).minutes.do(job)
    # schedule.every().monday.do(job)
    # schedule.every().wednesday.at("13:15").do(job)
    # schedule.every().minute.at(":17").do(job)
    # schedule.every(10).seconds.do(job)

    # schedule.every().friday.at("23:50:45").do(job)
    # schedule.every().day.at("09:04:05").do(GenerateAccessToken.main_task)

    # schedule.every().day.at("09:04:05").do(OpenPositions.main_task)

    schedule.every().day.at("22:50:10").do(OpeningSellBuy.main_task)

    while True:
        print("schedule opening sell buy job  - run pending ... ")
        schedule.run_pending()
        # time.sleep(1)

if __name__ == '__main__':
    task()
