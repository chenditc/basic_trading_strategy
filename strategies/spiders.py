from typing import List, Dict
from datetime import datetime
        
from vnpy.app.portfolio_strategy import StrategyTemplate, StrategyEngine, BacktestingEngine
from vnpy.trader.object import BarData

from utils.back_testing_wrapper import BackTestingWrapper
from utils.target_pos_strategy_template import TargetPosStrategyTemplate

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
        
        if len(price_code_list) == 0:
            return
        
        long_signal = bars[self.holding_data.long_open_chg_top20_symbol].open_price 
        short_signal = bars[self.holding_data.short_open_chg_top20_symbol].open_price
        
        target_pos = {}
        if long_signal > self.threshold and short_signal < (0 - self.threshold):
            #print("buy", price_code_list, current_date, long_signal, short_signal)
            target_pos[price_code_list[1]] = self.trade_vol
        elif long_signal < (0 - self.threshold) and short_signal > self.threshold:
            #print("short", price_code_list, current_date, long_signal, short_signal)
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

        symbol_list = [self.holding_data.long_open_chg_top20_symbol, self.holding_data.short_open_chg_top20_symbol]
        symbol_list += self.price_data.get_monthly_symbol_list()
        
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
        