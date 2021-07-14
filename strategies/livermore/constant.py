
TEST_TRADE_HOST = "https://test-trade-info-api.jesselivermore.com"
TRADE_HOST = "https://trade-info-api.jesselivermore.com"


class ExchangeType(object):
    A = "t,v"
    HK = "K"
    ALL = "ALL"


class SessionType(object):
    NORMAL = "0"
    ANPAN = "2"


class EntrustProp(object):
    C_Limit_Order = "0"                         # AB股限价单,美股
    Ao_At_Auction = "d"                         # 竞价单
    ELO = 'e'                                   # 增强限价盘
    Al_Auction = 'g'                            # 竞价限价单
    Limit = 'h'                                 # 限价单
    Quote_Order = 'I'                           # 报价单(交易所有，我们系统没有支持)
    SLO = 'j'                                   # 特别限价盘
    Average_Price_Order = 'k'                   # 平均价订单(没有这个业务)
    Cancel_Cross_Broker = 'l'                   # 交叉盘撤单
    Special_Odd_Lot = 'm'                       # 碎股挂单 碎股界面下的单
    WEITUOTIANDAN = 'n'                         # 委托填单
    Manual_Trade = 'o'                          # 手动交易
    Bulk_Cancel = 'p'                           # 批量撤单
    Pre_Opening = 'r'                           # 开市前交易(人手交易的一种)
    Odd_Lot = 's'                               # 特殊功能界面下的碎股
    Bulk_Cancel_Cross_Broker = 't'              # 交叉盘批量撤单
    Odd_Lot_Input = 'u'                         # 普通下单界面下的碎股


class EntrustType(object):
    """
    委托类别
    """
    BuySell = '0'
    Query = '1'
    CancelOrder = '2'
    Supplement = '3'
    ChangeOrder = 'B'


class EntrustBs(object):
    BUY = "1"
    SELL = "2"


class ActionIn(object):
    NEW = "0"
    MODIFY = "1"
    DELETE = "2"


class IPOType(object):
    CASH = "0"
    FINANCING = "1"
