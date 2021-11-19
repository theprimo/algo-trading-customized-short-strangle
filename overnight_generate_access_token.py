# customized short strangle - overnight

# Open & Close overnight positions - Automation using Fyers API
# NIFTY BANK OTM Weekly expiry options
# generate fyers access token

import sys
import json
import requests
import overnight_props as props
from datetime import datetime


# from fyers_api import fyersModel

class GenerateAccessToken:
    # perform the task
    @staticmethod
    def main_task():
        error_flag = "False"

        # start time
        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
        prefix = now.strftime("%b%Y")

        # log file
        f = "C:/MyApps/automate/overnight/" + prefix + "_BNFOTMHedging.txt"
        file = open(f, "a")

        try:
            holiday_flag = "False"

            # check if is a holiday
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
                file.write("Generate access token - Trading Holiday : " + holiday_msg + " - " + timestamp + "\n")
                file.close()
                # sys.exit()
                return

            file.write("Generate access token - start time: " + timestamp + "\n")

            # generate access token
            url = props.FYERS_TOKEN_URL
            requestParams = {
                "fyers_id": props.FYERS_ID,
                "password": props.FYERS_PWD,
                "pan_dob": props.FYERS_PAN_DOB,
                "appId": props.FYERS_APPID,
                "create_cookie": False
            }
            res = requests.post(url, json=requestParams)
            resd = json.loads(res.text)

            if 'Url' not in resd:
                file.write("Generate access token - Error: Authorization failed - " + str(resd) + "\n")
                error_flag = "True"
            else:
                urlstr = resd['Url']
                temp = (urlstr.split('?')[1]).split('&')[0]
                access_token = temp[13:]

                f = "C:/MyApps/automate/overnight/token.txt"
                tf = open(f, "w")

                # store token in a file
                tf.write(access_token)

                # log token time in a shared log file
                now = datetime.now()
                timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
                file.write("Generate access token - Info: access token " + access_token + " - " + timestamp + "\n")

                if tf is not None:
                    tf.close()

            # end time
            now = datetime.now()
            timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
            file.write("Generate access token - end time: " + timestamp + "\n")

        except Exception as e:
            if file is not None:
                file.write("Generate access token - Exception: " + str(e) + "\n")
        finally:
            if file is not None:
                file.close()
            # if error_flag == "True":
            #     sys.exit(1)


# execution starts from here
if __name__ == '__main__':
    GenerateAccessToken.main_task()

# the end
