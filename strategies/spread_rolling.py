from typing import List, Dict
from datetime import datetime
import re
import json
        
from vnpy.app.portfolio_strategy import StrategyEngine, BacktestingEngine
from vnpy.trader.object import BarData
from vnpy.trader.utility import ArrayManager

from utils.back_testing_wrapper import BackTestingWrapper
from utils.target_pos_strategy_template import TargetPosStrategyTemplate

class SpreadRollingStrategy(TargetPosStrategyTemplate):
    """"""

    author = "chendi"

    # params
    min_basis = 0
    underlying_data = None
    basis_return_only = False
    future_data = None
    verbose = False
    target_pos_map = None
    target_pos_reason = None

    # vars
    underlying_bars = []
    basis_bars = []
    basis_am = ArrayManager(2000)
    
    parameters = [
        "min_basis",
        "underlying_data",
        "basis_return_only",
        "future_data",
        "target_pos_map",
        "target_pos_reason",
        "verbose"
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

    def get_expired_date(self, code):
        expire_month_str = re.match("{}(\d+).{}".format(self.future_data.symbol, self.future_data.exchange.value), code).groups()[0]
        expire_month_date = datetime.strptime(expire_month_str + "15", "%y%m%d")
        expire_month_date = expire_month_date.replace(day=(15 + (4 - expire_month_date.weekday()) % 7))
        return expire_month_date
        
    def on_bars(self, bars: Dict[str, BarData]):
        """""" 
        self.cancel_all()
        
        current_date = list(bars.values())[0].datetime
        curr_pos, curr_vol = self.get_curr_pos()

        # 当前有数据的合约列表
        code_set = set(bars.keys()) & set(self.future_data.get_monthly_symbol_list())
        code_list = sorted(list(code_set))

        target_pos = {}
        
        # Check if we have position, buy first future if no position
        if curr_pos == None:
            symbol_to_buy = code_list[0]
            target_pos[symbol_to_buy] = 1
            self.trade_to_target_pos(target_pos, bars)
            self.put_event()
            return 
        else:
            target_pos[curr_pos] = curr_vol
        
        # If we find future basis more attractive, we roll
        # basis point = underlying price - future price
        basis_point_map = {}
        basis_point_percentage_map = {}
        # relative basis point = next month's basis point - current month's basis point
        relative_basis_point_map = {}
        # relative basis_percentage = (relative basis point / relative expire day / underlying price) * 365
        relative_basis_percentage_map = {}

        for code in code_list:
            basis_point = bars[self.underlying_data.get_vnpy_symbol()].close_price - bars[code].close_price
            basis_point_map[code] = basis_point
            
        # Anualized basis return percentage
        for code in code_list:
            days_to_expire = (self.get_expired_date(code).date() - current_date.date()).days + 1
            basis_point_percentage_map[code] = basis_point_map[code] * 100 / bars[self.underlying_data.get_vnpy_symbol()].close_price / days_to_expire * 365
            relative_basis_point_map[code] = basis_point_map[code] - basis_point_map[curr_pos]
            relative_days_to_expire = (self.get_expired_date(code).date() - self.get_expired_date(curr_pos).date()).days + 1
            adj_basis_point = relative_basis_point_map[code] * 100 / bars[self.underlying_data.get_vnpy_symbol()].close_price / relative_days_to_expire * 365
            relative_basis_percentage_map[code] = adj_basis_point
                    
        # Update basis bar time series
        near_code = code_list[1]
        
        avg_adj_basis = sum([x for x in relative_basis_percentage_map.values() if x != 0 and x > 0]) / 3
        #print(avg_adj_basis)
        underlying_bar = bars[self.underlying_data.get_vnpy_symbol()]
        self.underlying_bars.append(underlying_bar)

        basis_bar = BarData(gateway_name='backtesting', 
                          symbol=underlying_bar.symbol + "basis",  
                          exchange=underlying_bar.exchange, 
                          datetime=underlying_bar.datetime,
                          interval=underlying_bar.interval,
                          volume=underlying_bar.volume,
                          open_price=avg_adj_basis,
                          high_price=avg_adj_basis,
                          low_price=avg_adj_basis,
                          close_price=avg_adj_basis
                         )
        self.basis_bars.append(basis_bar)
        
        self.basis_am.update_bar(basis_bar)

        indicator_sma120 = self.basis_am.sma(120)
        boll_up, boll_down = self.basis_am.boll(120, 0.5)

        if self.verbose:
            print(f"Relative basis map: {relative_basis_percentage_map} boll_up: {boll_up}")
        
        
        # Calculate which code to roll
        roll_to_code = None
        basis_map_str = json.dumps(basis_point_percentage_map, indent=2)
        relative_basis_percentage_map_str = json.dumps(relative_basis_percentage_map, indent=2)
        roll_reason = f"basis_map {basis_map_str} \n\n relative_basis_map {relative_basis_percentage_map_str} \n\n boll_up {boll_up}"
       
        days_to_expire = (self.get_expired_date(curr_pos).date() - current_date.date()).days
        if self.verbose:
            print(f"{current_date} 当前合约 {curr_pos} {days_to_expire} 日后到期")
        if days_to_expire == 1:
            roll_reason += f"\n\n当前合约{curr_pos} {days_to_expire} 日后到期，即将到期，强制滚动"
            roll_to_code = code_list[1]
            
        
        for code in code_list:
            # 只向后滚动，获取额外基差
            if code <= curr_pos:
                continue
                
            # 基差为负数，不操作
            if relative_basis_percentage_map[code] < self.min_basis:
                continue

            # 只有在基差大于 boll_up 
            if relative_basis_percentage_map[code] < boll_up:
                roll_reason += f"\n\n{code} relative basis < boll_up"
                continue
            
            # 只有基差更大时滚动
            if basis_point_percentage_map[code] < basis_point_percentage_map[curr_pos]:
                roll_reason += f"\n\n{code} relative basis < {curr_pos}"
                continue
            
            roll_reason += f"\n\nRoll {curr_pos} to {code}"
            roll_to_code = code
            break
                        
        msg = f"{current_date} {roll_reason}"
        if roll_to_code is not None:
            # Roll position:
            print(msg)
            target_pos = {roll_to_code: 1}
        self.trade_to_target_pos(target_pos, bars)
        self.target_pos_map[current_date.date()] = target_pos
        self.target_pos_reason[current_date.date()] = msg

        self.put_event()
        
class SpreadRollingStrategyBackTestingWrapper(BackTestingWrapper):
    def __init__(self, future_data, underlying_data, data_provider=None):
        self.future_data = future_data
        self.underlying_data = underlying_data
        super().__init__(data_provider)
        
    def get_strategy_name(self):
        return f"{self.future_data.symbol}-{type(self).__name__}"
        
    def download_data(self):
        self.data_provider.download_data(self.future_data)
        self.data_provider.download_data(self.underlying_data)
        
    def back_test_and_get_today_target_pos(self, start_date=None):
        self.engine = BacktestingEngine()

        symbol_list = [self.underlying_data.get_vnpy_symbol()]
        symbol_list += self.future_data.get_monthly_symbol_list()
        
        if start_date is None:
            start_date = self.future_data.start_date
        
        self.engine.set_parameters(
            vt_symbols=symbol_list,
            interval=self.future_data.interval,
            start=start_date,
            end=datetime.today(),
            rates=self.rates,
            slippages=self.slippages,
            sizes=self.sizes,
            priceticks=self.priceticks,
            capital=self.capital,
        )

        setting = {
            "min_basis": 0,
            "underlying_data": self.underlying_data,
            "basis_return_only": False,
            "future_data": self.future_data,
            "target_pos_map": self.target_pos_map,
            "target_pos_reason" : self.target_pos_reason,
            "verbose": False
        }
        self.engine.add_strategy(SpreadRollingStrategy, setting)

        self.engine.load_data()
        self.engine.run_backtesting()