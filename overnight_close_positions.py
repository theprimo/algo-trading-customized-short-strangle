# customized short strangle - overnight

# Close overnight positions on markets opening which were opened on previous trading day
# NIFTY BANK OTM Weekly expiry options - Automation using Fyers API
# Fyers API is for live order placement

import sys
import json
import requests
import os
import os.path
import overnight_props as props
from os import path
from fyers_api import fyersModel
from datetime import datetime


class ClosePositions:
    # perform the task
    @staticmethod
    def main_task():
        error_flag = "False"
        holiday_flag = "False"

        # start time
        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
        prefix = now.strftime("%b%Y")

        # log file
        f = "C:/MyApps/automate/overnight/" + prefix + "_BNFOTMHedging.txt"
        file = open(f, "a")

        try:

            # check if today is holiday
            today = now.strftime("%d-%b-%Y")
            weekday = now.strftime("%A")
            holiday_msg = ''

            if weekday == "Saturday" or weekday == "Sunday":
                holiday_msg = weekday
                holiday_flag = "True"
            elif today in props.holidays2020:
                holiday_msg = props.holidays2020[today]
                holiday_flag = "True"

            if holiday_flag == "True":
                file.write("Close positions - Trading Holiday : " + holiday_msg + " - " + timestamp + "\n")
                file.close()
                # sys.exit()
                return

            file.write("Close positions - start time: " + timestamp + "\n")

            # read access token
            access_token = ''
            tf = "C:/MyApps/automate/overnight/token.txt"
            if path.exists(tf) and os.path.getsize(tf) > 0:
                with open(tf, 'r') as fp:
                    access_token = fp.readline()

            if access_token == '':
                file.write("Close positions - Error: Unable to read the access token from token.txt " + "\n")
                error_flag = "True"
            else:
                file.write("Close positions - Info: fetched access token from token.txt " + "\n")

                # main task - start

                is_async = False
                fyers = fyersModel.FyersModel(is_async)

                # exit all positions
                res = fyers.exit_positions(
                    token=access_token
                )

                now = datetime.now()
                timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
                if ('code' in res and res['code'] == 200) or (
                        'code' in res and res['code'] == 400 and res[
                    'message'] == 'Looks like you have no open positions.'):
                    file.write(
                        "Close positions - Info: Exit all positions successful - " + timestamp + " - " + str(
                            res) + "\n")
                else:
                    file.write(
                        "Close positions - Error: Exit all positions failed - " + timestamp + " - " + str(res) + "\n")
                    error_flag = "True"

                # main task - end

            # end time
            now = datetime.now()
            timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
            file.write("Close positions - end time: " + timestamp + "\n")

        except Exception as e:
            if file is not None:
                file.write("Close positions - Exception: " + str(e) + "\n")
        finally:
            if file is not None:
                file.close()
            # if error_flag == "True":
            #     sys.exit(1)


# execution starts from here
if __name__ == '__main__':
    ClosePositions.main_task()

# the end
