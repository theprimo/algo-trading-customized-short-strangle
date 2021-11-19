# customized short strangle - overnight

# Take trades - Open positions Automation using Fyers API & Samco API
# NIFTY BANK OTM Weekly options - Overnight positions
# Samco API is for live market data
# Fyers API is for live order placement

# Friday - buy options
# Tuesday, Wednesday, Thursday - sell options

import sys
import json
import requests
import os
import os.path
import overnight_props as props
from os import path
from time import sleep
from datetime import datetime, timedelta
from fyers_api import fyersModel
from truedata_ws.websocket.TD import TD
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge


class OpenPositions:

    # check if given date is a trading holiday
    @staticmethod
    def check_is_trading_holiday(date):
        global holiday_msg
        holiday_flag = "False"
        today = date.strftime("%d-%b-%Y")
        weekday = date.strftime("%A")

        if weekday == "Saturday" or weekday == "Sunday":
            holiday_flag = "True"
            holiday_msg = weekday
        elif today in props.holidays2020:
            holiday_flag = "True"
            holiday_msg = props.holidays2020[today]
        return holiday_flag

    # find next trading day
    @staticmethod
    def next_trading_day(date):
        i = 1
        while True:
            fut = date + timedelta(i)
            if OpenPositions.check_is_trading_holiday(fut) == "False":
                break
            i += 1

        return fut

    # perform task
    @staticmethod
    def main_task():
        global access_token, data_token
        global holiday_msg
        error_flag = "False"

        # start time
        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
        prefix = now.strftime("%b%Y")

        # log file
        f = "C:/MyApps/automate/overnight/" + prefix + "_BNFOTMHedging.txt"
        file = open(f, "a")

        try:

            # check if today is a trading holiday
            holiday_flg = OpenPositions.check_is_trading_holiday(now)
            if holiday_flg == "True":
                file.write("Open positions - Trading Holiday : " + holiday_msg + " - " + timestamp + "\n")
                file.close()
                # sys.exit()
                return

            # take positions on selective days
            weekday = now.strftime("%A")
            ntd = (OpenPositions.next_trading_day(now)).strftime("%A")

            if ntd == 'Monday':  # ntd == 'Monday' or ntd == 'Tuesday' or ntd == 'Friday':
                file.write(
                    "Open positions - Next trading day is " + ntd + " : not taking positions" + " - " + timestamp + "\n")
                file.close()
                # sys.exit()
                return

            file.write("Open positions - start time: " + timestamp + "\n")

            # main task - start

            is_async = False
            fyers = fyersModel.FyersModel(is_async)

            # read access token
            access_token = ''
            tf = "C:/MyApps/automate/overnight/token.txt"
            if path.exists(tf) and os.path.getsize(tf) > 0:
                with open(tf, 'r') as fp:
                    access_token = fp.readline()

            if access_token == '':
                file.write("Open positions - Error: Unable to read the access token from token.txt " + "\n")
                error_flag = "True"
            else:
                file.write("Open positions - Info: fetched access token from token.txt " + "\n")

                # flg = generate_data_token(fyers=fyers, file=file)     # old - market data from truedata
                # if flg == "True":

                # market data - fetch BNF Index spot price from samco
                ltp = OpenPositions.fetch_bnf_spot_price(file=file)
                if ltp != 0:
                    # find ce, pe strike price symbols
                    cesymbol, pesymbol = OpenPositions.find_otm_hedge_symbols(ltp=ltp)
                    file.write(
                        "Open positions - Info: ltp " + str(
                            ltp) + ", symbols " + str(cesymbol) + ", " + str(pesymbol) + "\n")

                    if ntd == 'Friday':
                        # place ATM hedge position buy orders
                        OpenPositions.place_buy_orders(fyers=fyers, token=access_token, ceatmsymbol=cesymbol,
                                                        peatmsymbol=pesymbol,
                                                        file=file)
                    else:
                        # place OTM hedge position sell orders
                        OpenPositions.place_sell_orders(fyers=fyers, token=access_token, ceotmsymbol=cesymbol,
                                                   peotmsymbol=pesymbol,
                                                   file=file)

            # main task - end

            # end time
            now = datetime.now()
            timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
            file.write("Open positions - end time: " + timestamp + "\n")

        except Exception as e:
            if file is not None:
                file.write("Open positions - Exception: " + str(e) + "\n")
        finally:
            if file is not None:
                file.close()
            # if error_flag == "True":
            #     sys.exit(1)

    # fetch bnf index spot price using samco api
    @staticmethod
    def fetch_bnf_spot_price(file):
        error_flag = "False"
        ltp = 0
        samco = StocknoteAPIPythonBridge()
        st = ''

        # do login & get token
        res = samco.login(
            body={'userId': props.SAMCO_ID, 'password': props.SAMCO_PWD, 'yob': props.SAMCO_YOB})
        resd = json.loads(res)
        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]

        if resd['status'] == 'Success':
            st = resd['sessionToken']
            file.write("Open positions - Info: samco login successful - " + timestamp + "\n")
        else:
            error_flag = "True"
            file.write("Open positions - Error: samco login failed - " + timestamp + " - " + str(res) + "\n")

        if error_flag == "False":
            # set session token
            samco.set_session_token(sessionToken=st)

            # res = samco.get_quote(symbol_name=props.SAMCO_BNFFUT_TRADINGSYMBOL, exchange=samco.EXCHANGE_NFO)
            # resd = json.loads(res)
            # if 'status' in resd and resd['status'] == 'Success' and 'statusMessage' in resd and resd[
            #     'statusMessage'] == 'Quote details retrieved successfully':
            #     ltp = resd['lastTradedPrice']  # ltt = resd['lastTradedTime']

            # get bnf index quote
            headers = {
                'Accept': 'application/json',
                'x-session-token': st
            }
            res = requests.get('https://api.stocknote.com/quote/indexQuote', params={
                'indexName': props.SAMCO_BNF_INDEXNAME
            }, headers=headers)

            resd = res.json()

            if 'status' in resd and resd['status'] == 'Success' and 'statusMessage' in resd and resd[
                'statusMessage'] == 'Index Quote details retrieved successfully':
                ltp = resd['spotPrice']

            now = datetime.now()
            timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]

            if ltp == 0:
                file.write(
                    "Open positions - Error: fetching BNF Index spot price from samco is failed - " + timestamp + " - " + str(
                        res) + "\n")
            else:
                ltp = int(ltp.split(".")[0])
                file.write(
                    "Open positions - Info: fetching BNF Index spot price from samco is success - " + timestamp + "\n")

            # logout
            res = samco.logout()
            resd = json.loads(res)
            now = datetime.now()
            timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]

            if resd['status'] == 'Success':
                file.write("Open positions - Info: samco logout successful - " + timestamp + "\n")
            else:
                error_flag = "True"
                file.write("Open positions - Error: samco logout failed - " + timestamp + " - " + str(res) + "\n")

        return ltp

    # fetch NIFTY BANK Index LTP from TrueData
    @staticmethod
    def fetch_bnf_ltp(file):
        global data_token
        ltp = 0
        error_flag = "True"

        td_obj = ''
        resd = ''
        # symbols = ['NIFTY 50', 'NIFTY BANK', 'BANKNIFTY-I', 'BANKNIFTY-II']
        symbols = [props.TD_BNF_SYMBOL]

        try:
            td_obj = TD(props.TD_APP_USER, props.TD_APP_PWD, broker_token=data_token)

            req_ids = td_obj.start_live_data(symbols)
            sleep(1)  # let the data populate
            for req_id in req_ids:
                res = td_obj.live_data[req_id]
                resd = res.__dict__
                if 'symbol' in resd and 'ltp' in resd and resd['symbol'] == 'NIFTY BANK':
                    ltp = resd['ltp']
                    error_flag = "False"
                    now = datetime.now()
                    timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
                    file.write(
                        "Open positions - Info: fetch NIFTY BANK Index LTP response - " + timestamp + " - " + str(
                            resd) + "\n")
                # sleep(1)

        except Exception as e:
            file.write("Open positions - Exception: " + str(e) + "\n")
        finally:
            if td_obj is not None:
                td_obj.stop_live_data(symbols)
                td_obj.disconnect()

        if error_flag == "True":
            file.write("Open positions - Info: " + str(resd) + "\n")
            file.write("Open positions - Error: Unable to fetch NIFTY BANK Index LTP, please check immediately" + "\n")
        return ltp

    # find OTM hedge strike price symbols
    @staticmethod
    def find_otm_hedge_symbols(ltp):
        x = ltp % 100
        if x > 75:
            ltp += 100
        y = ltp // 100
        atmr = y * 100

        atmf = (ltp // 100) * 100

        now = datetime.now()
        ntd = (OpenPositions.next_trading_day(now)).strftime("%A")
        symbol_format = OpenPositions.find_symbol_format()

        if ntd == 'Friday':
            # find weekly expiry atm option symbols
            cesymbol = props.FYERS_BNF_SYMBOL_PREFIX + symbol_format + str(int(atmr)) + 'CE'
            pesymbol = props.FYERS_BNF_SYMBOL_PREFIX + symbol_format + str(int(atmr)) + 'PE'
        else:
            if ntd == 'Wednesday' or ntd == 'Thursday':
                delta = props.BNFOTM_DELTA_POINTS
            else:
                delta = props.BNFOTM_DELTA_DEFAULT_POINTS

            if (ntd == 'Wednesday' or ntd == 'Thursday') and atmr % 500 == 0:   # ntd == 'Tuesday' or
                ceotm = atmr
                peotm = atmr
            elif (ntd == 'Wednesday' or ntd == 'Thursday') and atmf % 500 == 0:
                ceotm = atmf
                peotm = atmf
            else:
                ceotm = atmr + delta
                peotm = atmr - delta

                # find otm prices divisible by 500
                while ceotm % 500 != 0:
                    ceotm += 100
                while peotm % 500 != 0:
                    peotm -= 100

            # find weekly expiry otm option symbols
            # ex: NSE:BANKNIFTY20O1524000CE, NSE:BANKNIFTY20OCT24000CE
            cesymbol = props.FYERS_BNF_SYMBOL_PREFIX + symbol_format + str(int(ceotm)) + 'CE'
            pesymbol = props.FYERS_BNF_SYMBOL_PREFIX + symbol_format + str(int(peotm)) + 'PE'

        return cesymbol, pesymbol

    # find expiry symbol format
    @staticmethod
    def find_symbol_format():
        now = datetime.now()
        curexp = OpenPositions.get_expiry_date(now)
        nextexp = OpenPositions.get_expiry_date(curexp)
        curexpmon = (curexp.strftime("%b")).upper()
        nextexpmon = (nextexp.strftime("%b")).upper()

        part1 = curexp.strftime("%y")  # yy

        # weekly option strikes - yyMdd
        if curexpmon == nextexpmon:
            M = curexpmon[0]
            dd = curexp.strftime("%d")
            part2 = M + dd
        # monthly option strikes - yyMON
        else:
            part2 = curexpmon

        symbol_format = part1 + part2
        return symbol_format

    # find expiry date for given date
    @staticmethod
    def get_expiry_date(date):
        exp = ''
        weekday = date.strftime("%A")
        # get coming thursday
        if weekday == 'Thursday':
            exp = date + timedelta(7)
        elif weekday == 'Friday':
            exp = date + timedelta(6)
        elif weekday == 'Saturday':
            exp = date + timedelta(5)
        elif weekday == 'Sunday':
            exp = date + timedelta(4)
        elif weekday == 'Monday':
            exp = date + timedelta(3)
        elif weekday == 'Tuesday':
            exp = date + timedelta(2)
        elif weekday == 'Wednesday':
            exp = date + timedelta(1)

        if OpenPositions.check_is_trading_holiday(exp) == "True":
            exp = exp - timedelta(1)
        return exp

    # place bnf atm hedging position buy orders
    @staticmethod
    def place_buy_orders(fyers, token, ceatmsymbol, peatmsymbol, file):
        # ce atm buy order
        res = fyers.place_orders(
            token=token,
            data={
                "symbol": ceatmsymbol,
                "qty": props.ORDER_BNF_OTM_QTY,
                "type": props.ORDER_TYPE_MARKET_ORDER,
                "side": props.ORDER_SIDE_BUY,
                "productType": props.ORDER_PRODUCTTYPE_MARGIN,
                "limitPrice": 0,
                "stopPrice": 0,
                "disclosedQty": 0,
                "validity": props.ORDER_VALIDITY_DAY,
                "offlineOrder": props.ORDER_OFFLINEORDER,  # True for AMO orders
                "stopLoss": 0,
                "takeProfit": 0
            }
        )

        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
        if 'code' in res and res['code'] == 200:
            file.write(
                "Open positions - Info: Placing CE Long Order successful - " + timestamp + " - " + str(res) + "\n")
        else:
            file.write("Open positions - Error: Placing CE Long Order failed - " + timestamp + " - " + str(res) + "\n")
            return

        # pe atm buy order
        res = fyers.place_orders(
            token=token,
            data={
                "symbol": peatmsymbol,
                "qty": props.ORDER_BNF_OTM_QTY,
                "type": props.ORDER_TYPE_MARKET_ORDER,
                "side": props.ORDER_SIDE_BUY,
                "productType": props.ORDER_PRODUCTTYPE_MARGIN,
                "limitPrice": 0,
                "stopPrice": 0,
                "disclosedQty": 0,
                "validity": props.ORDER_VALIDITY_DAY,
                "offlineOrder": props.ORDER_OFFLINEORDER,  # True for AMO orders
                "stopLoss": 0,
                "takeProfit": 0
            }
        )

        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
        if 'code' in res and res['code'] == 200:
            file.write(
                "Open positions - Info: Placing PE Long Order successful - " + timestamp + " - " + str(res) + "\n")
        else:
            file.write("Open positions - Error: Placing PE Long Order failed - " + timestamp + " - " + str(res) + "\n")
            # exit open positions
            OpenPositions.exit_positions(fyers=fyers, token=token, file=file)
            return

    # place bnf otm hedging position sell orders
    @staticmethod
    def place_sell_orders(fyers, token, ceotmsymbol, peotmsymbol, file):
        # ce otm sell order
        res = fyers.place_orders(
            token=token,
            data={
                "symbol": ceotmsymbol,
                "qty": props.ORDER_BNF_OTM_QTY,
                "type": props.ORDER_TYPE_MARKET_ORDER,
                "side": props.ORDER_SIDE_SELL,
                "productType": props.ORDER_PRODUCTTYPE_MARGIN,
                "limitPrice": 0,
                "stopPrice": 0,
                "disclosedQty": 0,
                "validity": props.ORDER_VALIDITY_DAY,
                "offlineOrder": props.ORDER_OFFLINEORDER,  # True for AMO orders
                "stopLoss": 0,
                "takeProfit": 0
            }
        )

        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
        if 'code' in res and res['code'] == 200:
            file.write(
                "Open positions - Info: Placing CE Short Order successful - " + timestamp + " - " + str(res) + "\n")
        else:
            file.write(
                "Open positions - Error: Placing CE Short Order failed - " + timestamp + " - " + str(res) + "\n")
            return

        # pe otm sell order
        res = fyers.place_orders(
            token=token,
            data={
                "symbol": peotmsymbol,
                "qty": props.ORDER_BNF_OTM_QTY,
                "type": props.ORDER_TYPE_MARKET_ORDER,
                "side": props.ORDER_SIDE_SELL,
                "productType": props.ORDER_PRODUCTTYPE_MARGIN,
                "limitPrice": 0,
                "stopPrice": 0,
                "disclosedQty": 0,
                "validity": props.ORDER_VALIDITY_DAY,
                "offlineOrder": props.ORDER_OFFLINEORDER,  # True for AMO orders
                "stopLoss": 0,
                "takeProfit": 0
            }
        )

        now = datetime.now()
        timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
        if 'code' in res and res['code'] == 200:
            file.write(
                "Open positions - Info: Placing PE Short Order successful - " + timestamp + " - " + str(res) + "\n")
        else:
            file.write(
                "Open positions - Error: Placing PE Short Order failed - " + timestamp + " - " + str(res) + "\n")
            # exit open positions
            OpenPositions.exit_positions(fyers=fyers, token=token, file=file)
            return

    # generate data token
    @staticmethod
    def generate_data_token(fyers, file):
        global access_token, data_token
        token_flag = "True"

        try:
            # generate data token aka broker token
            res = fyers.generate_data_token(
                token=access_token,
                data={
                    "vendorApp": props.FYERS_VENDORAPP
                }
            )
            if 'code' in res and res['code'] == 200:
                data_token = res['data']['token_id']
                # log token time
                now = datetime.now()
                timestamp = now.strftime("%a %d %b %Y %H:%M:%S.%f")[:-3]
                file.write("Open positions - Info: data token " + str(data_token) + " - " + timestamp + "\n")
            else:
                file.write("Open positions - Error: Generating data token failed - " + str(res) + "\n")
                token_flag = "False"

        except Exception as e:
            file.write("Open positions - Exception: " + str(e) + "\n")
        finally:
            pass

        return token_flag

    # validate & generate tokens
    @staticmethod
    def validate_and_generate_tokens(fyers, file):
        global access_token, data_token
        token_valid_flag = "False"
        token_failed_flag = "False"

        # 1st line - access token; 2nd line - data token
        tf = 'C:/MyApps/automate/overnight/token.txt'

        # test access token is valid
        if path.exists(tf) and os.path.getsize(tf) > 0:
            with open(tf, 'r') as fp:
                access_token = fp.readline()
                res = fyers.get_profile(token=access_token)
                if 'code' in res or res['code'] == 200:
                    token_valid_flag = "True"
                    data_token = fp.readline()

        # generate new tokens
        if token_valid_flag == "False":
            # generate access token
            url = props.FYERS_TOKEN_URL
            request_params = {
                "fyers_id": props.FYERS_ID,
                "password": props.FYERS_PWD,
                "pan_dob": props.FYERS_PAN_DOB,
                "appId": props.FYERS_APPID,
                "create_cookie": False
            }
            res = requests.post(url, json=request_params)
            resd = json.loads(res.text)

            if 'Url' not in resd:
                file.write("Open positions - Info: " + str(resd) + "\n")
                file.write("Open positions - Error: Authorization failed, please check immediately" + "\n")
                token_failed_flag = "True"
            else:
                url_str = resd['Url']
                temp = (url_str.split('?')[1]).split('&')[0]
                access_token = temp[13:]
                # print("access_token: " + access_token)

            # generate data token aka broker token
            res = fyers.generate_data_token(
                token=access_token,
                data={
                    "vendorApp": props.FYERS_VENDORAPP
                }
            )

            if 'code' not in res or res['code'] != 200:
                file.write("Open positions - Info: " + str(res) + "\n")
                file.write("Open positions - Error: Generating data token failed, please check immediately" + "\n")
                token_failed_flag = "True"
            else:
                data_token = res['data']['token_id']
                # print("data_token: " + data_token)

            if token_failed_flag == "False":
                tfile = open(tf, 'w')
                tfile.write(access_token + "\n")
                tfile.write(data_token + "\n")
                tfile.close()
            else:
                tfile = open(tf, 'w')  # create emtpy file
                tfile.write('')
                tfile.close()
                file.close()
                # sys.exit(1)

    # exit all positions
    @staticmethod
    def exit_positions(fyers, token, file):
        try:
            res = fyers.exit_positions(
                token=token
            )
            if ('code' in res and res['code'] == 200) or (
                    'code' in res and res['code'] == 400 and res[
                'message'] == 'Looks like you have no open positions.'):
                file.write("Open positions - Info: Exit all positions successful - " + str(res) + "\n")
            else:
                file.write("Open positions - Error: Exit all positions failed - " + str(res) + "\n")
        except Exception as e:
            file.write("Open positions - Exception: " + str(e) + "\n")
        finally:
            pass


# execution starts from here
if __name__ == '__main__':
    OpenPositions.main_task()

# the end
