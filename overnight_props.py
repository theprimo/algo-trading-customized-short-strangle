# customized short strangle - overnight

# global properties file

# fyers account for order placement
# samco account for live market data

FYERS_TOKEN_URL = 'https://api.fyers.in/api/v1/token'

FYERS_ID = '******'
FYERS_PWD = '*******'
FYERS_PAN_DOB = '*******'
FYERS_APPID = '********'
FYERS_VENDORAPP = '0KMS0EZVXI'
FYERS_BNF_SYMBOL_PREFIX = 'NSE:BANKNIFTY'

TD_APP_USER = '*******'
TD_APP_PWD = '********'
TD_BNF_SYMBOL = 'NIFTY BANK'

BNFOTM_DELTA_POINTS = 400
BNFOTM_DELTA_DEFAULT_POINTS = 700
BNFOTM_DELTA_MIN_POINTS = 300
BNFOTM_DELTA_MAX_POINTS = 1000

ORDER_BNF_OTM_QTY = 25
ORDER_SIDE_BUY = 1
ORDER_SIDE_SELL = -1
ORDER_TYPE_LIMIT_ORDER = 1
ORDER_TYPE_MARKET_ORDER = 2

ORDER_PRODUCTTYPE_MARGIN = 'MARGIN'
ORDER_PRODUCTTYPE_INTRADAY = 'INTRADAY'
ORDER_PRODUCTTYPE_CNC = 'CNC'
ORDER_PRODUCTTYPE_CO = 'CO'
ORDER_PRODUCTTYPE_BO = 'BO'

ORDER_OFFLINEORDER = 'False'
ORDER_VALIDITY_IOC = 'IOC'
ORDER_VALIDITY_DAY = 'DAY'

holidays2020 = {
    '02-Oct-2020': 'Mahatma Gandhi Jayanti',
    '16-Nov-2020': 'Diwali-Balipratipada',
    '30-Nov-2020': 'Gurunanak Jayanti',
    '25-Dec-2020': 'Christmas',
}

holidays2021 = {
    '26-Jan-2021': 'Republic day',
    '11-Mar-2021': 'Mahashivratri Day',
    '29-Mar-2021': 'Holi',
    '02-Apr-2021': 'Good Friday',
    '14-Apr-2021': 'Dr. Baba Saheb Ambedkar Jayanti',
    '21-Apr-2021': 'Ram Navami',
    '13-May-2021': 'Id-ul-Fltr (Ramzan Eid)',
    '20-Jul-2021': 'Id-al-Adha',
    '19-Aug-2021': 'Ashura',
    '10-Sep-2021': 'Ganesh Chaturthi',
    '15-Oct-2021': 'Dussehra',
    '04-Nov-2021': 'Diwali',
    '19-Nov-2021': 'Guru Nanak Jayanti',
}

SAMCO_ID = '********'
SAMCO_PWD = '********'
SAMCO_YOB = '****'

SAMCO_BNF_SYMBOLNAME = 'BANKNIFTY'
SAMCO_BNF_INDEXNAME = 'Nifty Bank'
# SAMCO_BNFFUT_TRADINGSYMBOL = 'BANKNIFTY20OCTFUT'
# SAMCO_BNFFUT_SYMBOLCODE = '50836_NFO'

