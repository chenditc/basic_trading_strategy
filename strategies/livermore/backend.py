from .http import HttpClient


class TradeBackend(object):

    def __init__(self, key, secret, test=False):
        self.key = key
        self.http = HttpClient(key, secret, test)

    def get_ipo_list(self):
        path = "/api/info/get-ipo-setting"
        params = {
        }
        return self.http.get(path, params)

    def get_ipo_detail(self, position_str):
        path = "/api/info/get-ipo-detail"
        params = {
            "sp_page": "1",
            "position_str": position_str,
            "get_all": "1",
        }
        return self.http.get(path, params)

    def get_ipo_number(self, stock_code):
        path = "/api/info/get-ipo-number"
        params = {
            "stock_code": stock_code,
            "sp_ipo_financing_v2": "1",
        }
        return self.http.get(path, params)

    def get_withdraw(self):
        path = "/api/info/get-withdraw"
        params = {
        }
        return self.http.get(path, params)

    def get_stock_info(self, ignore_clean_stock, exchange_type):
        path = "/api/info/get-stock-info"
        params = {
            "ignore_clean_stock": ignore_clean_stock,
            "get_all": "1",
            "exchange_type": exchange_type,
        }
        return self.http.get(path, params)

    def get_user_fund(self):
        path = "/api/info/fund-info"
        params = {
        }
        return self.http.get(path, params)

    def is_connnect(self):
        path = "/api/info/is-connect"
        params = {
        }
        return self.http.get(path, params)

    def entrust_stock(self, stock_code, entrust_amount, entrust_price, entrust_bs, entrust_type, entrust_prop, auto_exchange, session_type):
        path = "/api/trade/entrust-enter"
        data = {
            "stock_code": stock_code,
            "entrust_amount": entrust_amount,
            "entrust_price": entrust_price,
            "entrust_bs": entrust_bs,
            "entrust_type": entrust_type,
            "entrust_prop": entrust_prop,
            "auto_exchange": auto_exchange if auto_exchange else "",
            "session_type": session_type,
        }
        return self.http.post(path, data)

    def set_ipo_detail(self, stock_code, quantity_apply, apply_amount, deposit_rate, deposit_amount, type_, action_in):
        path = "/api/trade/set-ipo-detail"
        data = {
            "stock_code": stock_code,
            "quantity_apply": quantity_apply,
            "apply_amount": apply_amount,
            "deposit_rate": deposit_rate,
            "deposit_amount": deposit_amount,
            "type_": type_,
            "action_in": action_in,
        }
        return self.http.post(path, data)

    def entrust_withdraw(self, batch_flag, entrust_amount, entrust_price, entrust_no_first, stock_code, entrust_type, exchange_type, session_type):
        path = "/api/trade/entrust-withdraw"
        data = {
            "batch_flag": batch_flag,
            "entrust_amount": entrust_amount,
            "entrust_price": entrust_price,
            "entrust_no_first": entrust_no_first,
            "stock_code": stock_code,
            "entrust_type": entrust_type,
            "exchange_type": exchange_type,
            "session_type": session_type,
        }
        return self.http.post(path, data)
