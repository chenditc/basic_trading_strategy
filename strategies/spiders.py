from typing import List, Dict
from datetime import datetime
        
from vnpy.app.portfolio_strategy import StrategyTemplate, StrategyEngine, BacktestingEngine
from vnpy.trader.object import BarData

from utils.back_testing_wrapper import BackTestingWrapper
from utils.target_pos_strategy_template import TargetPosStrategyTemplate
from market_data.models import FutureHoldingData

class SpiderStrategy(TargetPosStrategyTemplate):
    """"""

    author = "chendi"

    # params
    price_data = None
    holding_data = None
    target_pos_map = None
    target_pos_reason = None
    trade_vol = 1
    threshold = 0

    # vars
    underlying_bars = []
    
    parameters = [
        "price_data",
        "holding_data",
        "target_pos_map",
        "target_pos_reason",
        "trade_vol",
        "threshold",
    ]
    variables = [
    ]

    def __init__(
        self,
        strategy_engine: StrategyEngine,
        strategy_name: str,
        vt_symbols: List[str],
        setting: dict
    ):
        """"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)
        
    def on_bars(self, bars: Dict[str, BarData]):
        """""" 
        self.cancel_all()
        
        current_date = list(bars.values())[0].datetime
        curr_pos = self.get_curr_pos()

        # 当前有数据的合约列表
        price_code_set = set(bars.keys()) & set(self.price_data.get_monthly_symbol_list())
        price_code_list = sorted(list(price_code_set))
        price_code_list_without_exchange = [x.split(".")[0] for x in price_code_list]
        
        if len(price_code_list) == 0:
            return
        
        # 过滤出当天的持仓排名总和，并且计算对应的聪明投资者名单
        holding_data = list(FutureHoldingData.select()
                            .where(FutureHoldingData.trade_date==current_date.date())
                            .where(FutureHoldingData.symbol << price_code_list_without_exchange)
                            .dicts())

        # Merge all code's data
        merged_data_map = {}
        for data in holding_data:
            long_hld = data["long_hld"] or 0
            short_hld = data["short_hld"] or 0

            if (long_hld + short_hld) == 0:
                continue
            vol = data["vol"] or 0
            long_chg = data["long_chg"] or 0
            short_chg = data["short_chg"] or 0
            merged_data = merged_data_map.get(data["broker"], {})
            merged_data["long_hld"] = merged_data.get("long_hld", 0) + long_hld
            merged_data["short_hld"] = merged_data.get("short_hld", 0) + short_hld
            merged_data["vol"] = merged_data.get("vol", 0) + vol
            merged_data["long_chg"] = merged_data.get("long_chg", 0) + long_chg
            merged_data["short_chg"] = merged_data.get("short_chg", 0) + short_chg
            merged_data["broker"] = data["broker"]
            merged_data_map[data["broker"]] = merged_data

        for data in merged_data_map.values():
            smart_score = abs(data["vol"] * (data["long_hld"] - data["short_hld"]) / (data["long_hld"] + data["short_hld"]))
            data["smart_score"] = smart_score

        sorted_holding_data = sorted(merged_data_map.values(), key=lambda x: x["smart_score"], reverse=True)
        long_signal = 0
        short_signal = 0
        for data in sorted_holding_data:
            long_signal += data["long_chg"]
            short_signal += data["short_chg"]
            #print(data["broker"], data["smart_score"], data["long_chg"], data["short_chg"])
        
        akshare_long_signal = bars[self.holding_data.long_open_chg_top20_symbol].close_price
        akshare_short_signal = bars[self.holding_data.short_open_chg_top20_symbol].close_price
        if akshare_long_signal != long_signal:
            print("mismatch", current_date, long_signal, akshare_long_signal, short_signal, akshare_short_signal)
        
        target_pos = {}
        if long_signal > self.threshold and short_signal < (0 - self.threshold):
            print("buy", price_code_list, current_date, long_signal, short_signal)
            if len(price_code_list) > 1:
                target_pos[price_code_list[1]] = self.trade_vol
        elif long_signal < (0 - self.threshold) and short_signal > self.threshold:
            print("short", price_code_list, current_date, long_signal, short_signal)
            if len(price_code_list) > 1:
                target_pos[price_code_list[1]] = 0 - self.trade_vol

        
        self.target_pos_map[current_date.strftime("%Y%m%d")] = target_pos
        self.target_pos_reason[current_date.strftime("%Y%m%d")] = f"今日多仓增加: {long_signal} 空仓增加: {short_signal} 阈值 {self.threshold}"
            
        self.trade_to_target_pos(target_pos, bars)

        self.put_event()
        

class SpiderStrategyBackTestingWrapper(BackTestingWrapper):
    def __init__(self, price_data, holding_data, data_provider=None):
        self.price_data = price_data
        self.holding_data = holding_data
        super().__init__(data_provider)
        
    def get_strategy_name(self):
        return f"{self.price_data.symbol}-{type(self).__name__}"
        
    def download_data(self):
        self.data_provider.download_data(self.price_data)
        self.data_provider.download_data(self.holding_data)
        
    def back_test_and_get_today_target_pos(self, start_date=None):
        self.engine = BacktestingEngine()

        symbol_list = self.price_data.get_monthly_symbol_list()
        
        symbol_list += [self.holding_data.long_open_chg_top20_symbol, 
                        self.holding_data.short_open_chg_top20_symbol]
        
        if start_date is None:
            start_date = self.price_data.start_date
        
        self.engine.set_parameters(
            vt_symbols=symbol_list,
            interval=self.price_data.interval,
            start=start_date,
            end=datetime.today(),
            rates=self.rates,
            slippages=self.slippages,
            sizes=self.get_future_size_for_symbol(self.price_data.symbol),
            priceticks=self.priceticks,
            capital=self.capital,
        )

        setting = {
            "price_data":  self.price_data,
            "holding_data": self.holding_data,
            "target_pos_map": self.target_pos_map,
            "target_pos_reason" : self.target_pos_reason,
            "trade_vol": 1,
            "threshold": 0,
        }
        self.engine.add_strategy(SpiderStrategy, setting)

        self.engine.load_data()
        self.engine.run_backtesting()
        