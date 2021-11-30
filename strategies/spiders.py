from typing import List, Dict
from datetime import datetime
        
from vnpy.app.portfolio_strategy import StrategyTemplate, StrategyEngine, BacktestingEngine
from vnpy.trader.object import BarData

from utils.back_testing_wrapper import BackTestingWrapper

class SpiderStrategy(StrategyTemplate):
    """"""

    author = "chendi"

    # params
    price_data = None
    holding_data = None
    target_pos_map = None
    trade_vol = 1
    threshold = 0

    # vars
    underlying_bars = []
    
    parameters = [
        "price_data",
        "holding_data",
        "target_pos_map",
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


    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        self.load_bars(1)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")
        
    def get_curr_pos(self):
        curr_pos = None
        curr_vol = 0
        for pos, vol in self.pos.items():
            if not pos.endswith(".CFFEX"):
                continue
            if vol == 0:
                continue
            assert(curr_pos == None)
            curr_pos = pos
            curr_vol = vol
        return curr_pos, curr_vol
    
    def trade_to_target_pos(self, target_pos, bars):
        curr_pos, curr_vol = self.get_curr_pos()
        if curr_pos in target_pos:
            #print("持仓不变不操作")
            return
        
        if curr_pos:
            if curr_vol > 0:
                self.sell(curr_pos, price=bars[curr_pos].close_price * 0.9, volume=abs(curr_vol))
                #print(f"平仓卖出 {curr_pos}")
            else:
                self.buy(curr_pos, price=bars[curr_pos].close_price * 1.1, volume=abs(curr_vol))
                #print(f"平仓买入 {curr_pos}")
                
                
        for pos, vol in target_pos.items():
            if vol > 0:
                self.buy(pos, price=bars[pos].close_price * 1.1, volume=abs(vol))
            else:
                self.sell(pos, price=bars[pos].close_price * 0.9, volume=abs(vol))
        
        
    def on_bars(self, bars: Dict[str, BarData]):
        """""" 
        self.cancel_all()
        
        current_date = list(bars.values())[0].datetime
        curr_pos = self.get_curr_pos()

        # 当前有数据的合约列表
        price_code_set = set(bars.keys()) & set(self.price_data.get_monthly_symbol_list())
        price_code_list = sorted(list(price_code_set))
        
        long_signal = bars[self.holding_data.long_open_chg_top20_symbol].open_price 
        short_signal = bars[self.holding_data.short_open_chg_top20_symbol].open_price
        
        target_pos = {}
        if long_signal > self.threshold and short_signal < (0 - self.threshold):
            #print("buy", current_date, long_signal, short_signal)
            target_pos[price_code_list[1]] = self.trade_vol
        elif long_signal < (0 - self.threshold) and short_signal > self.threshold:
            #print("short", current_date, long_signal, short_signal)
            target_pos[price_code_list[1]] = 0 - self.trade_vol

        
        self.target_pos_map[current_date.strftime("%Y%m%d")] = target_pos
            
        self.trade_to_target_pos(target_pos, bars)

        self.put_event()
        

class SpiderStrategyBackTestingWrapper(BackTestingWrapper):
    def __init__(self, price_data, holding_data, data_provider=None):
        self.price_data = price_data
        self.holding_data = holding_data
        super().__init__(data_provider)
        
    def download_data(self):
        self.data_provider.download_data(self.price_data)
        self.data_provider.download_data(self.holding_data)
        
    def back_test_and_get_today_target_pos(self):
        self.engine = BacktestingEngine()

        symbol_list = [self.holding_data.long_open_chg_top20_symbol, self.holding_data.short_open_chg_top20_symbol]
        symbol_list += self.price_data.get_monthly_symbol_list()
        
        self.engine.set_parameters(
            vt_symbols=symbol_list,
            interval=self.price_data.interval,
            start=self.price_data.start_date,
            end=datetime.today(),
            rates=self.rates,
            slippages=self.slippages,
            sizes=self.sizes,
            priceticks=self.priceticks,
            capital=self.capital,
        )

        setting = {
            "price_data":  self.price_data,
            "holding_data": self.holding_data,
            "target_pos_map": self.target_pos_map,
            "trade_vol": 1,
            "threshold": 0,
        }
        self.engine.add_strategy(SpiderStrategy, setting)

        self.engine.load_data()
        self.engine.run_backtesting()
        