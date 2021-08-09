import json
import re
from collections import defaultdict
from datetime import datetime
from importlib import reload
from typing import List, Dict

import vnpy.app.portfolio_strategy
from vnpy.app.portfolio_strategy import BacktestingEngine
from vnpy.app.portfolio_strategy import StrategyTemplate, StrategyEngine
from vnpy.trader.constant import Interval
from vnpy.trader.object import BarData
from vnpy.trader.utility import ArrayManager

from utils.email_util import send_server_chan
from utils.tushare_data_download import prepare_ic_data_set


class IndexFutureBasisStrategy(StrategyTemplate):
    """"""

    author = "chendi"

    # params
    min_basis = 0
    underlying = "000905.SSE"
    basis_return_only = False
    future_prefix = "IC"

    # vars
    underlying_bars = []
    basis_bars = []
    basis_am = ArrayManager(2000)

    parameters = [
        "min_basis",
        "underlying",
        "basis_return_only",
        "future_prefix"
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

        self.targets: Dict[str, int] = {}

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

    def get_expired_date(self, code):
        if code.endswith(".CFFEX"):
            expire_month_str = re.match("{}(\d+).CFFEX".format(self.future_prefix), code).groups()[0]
            expire_month_date = datetime.strptime(expire_month_str + "15", "%y%m%d")
            expire_month_date = expire_month_date.replace(day=(15 + (4 - expire_month_date.weekday()) % 7))
            return expire_month_date
        else:
            return None

    def get_curr_pos(self):
        curr_pos = None
        for pos, vol in self.pos.items():
            if not pos.endswith(".CFFEX"):
                continue
            if vol == 0:
                continue
            assert (curr_pos == None)
            curr_pos = pos
        return curr_pos

    def on_bars(self, bars: Dict[str, BarData]):
        """"""
        self.cancel_all()

        current_date = list(bars.values())[0].datetime
        curr_pos = self.get_curr_pos()

        # 当前有数据的合约列表
        code_list = sorted(filter(lambda x: x.endswith(".CFFEX"), bars.keys()))
        print(f"{current_date}  code list: {code_list}")

        # Check if we have position, buy first future if no position
        if curr_pos == None:
            symbol_to_buy = code_list[0]
            self.write_log("Init buy:" + symbol_to_buy)
            price = bars[symbol_to_buy].close_price * 1.08
            self.buy(vt_symbol=code_list[0], price=price, volume=1)
            # If we only want to analyze basis return, sell an underlying to hedge the beta.
            if self.basis_return_only:
                self.sell(vt_symbol=self.underlying, price=bars[self.underlying].close_price * 0.92, volume=1)
            self.put_event()
            return

            # If we find future basis more attractive, we roll
        # basis point = underlying price - future price
        basis_point_map = {}
        basis_point_percentage_map = {}
        # relative basis point = next month's basis point - current month's basis point
        relative_basis_point_map = {}
        # relative basis_percentage = (relative basis point / relative expire day / underlying price) * 365
        relative_basis_percentage_map = {}

        for code in code_list:
            basis_point = bars[self.underlying].close_price - bars[code].close_price
            basis_point_map[code] = basis_point

        # Anualized basis return percentage
        for code in code_list:
            days_to_expire = (self.get_expired_date(code) - current_date).days + 1
            basis_point_percentage_map[code] = basis_point_map[code] * 100 / bars[
                self.underlying].close_price / days_to_expire * 365

            relative_basis_point_map[code] = basis_point_map[code] - basis_point_map[code_list[0]]
            relative_days_to_expire = (self.get_expired_date(code) - self.get_expired_date(code_list[0])).days + 1
            adj_basis_point = relative_basis_point_map[code] * 100 / bars[
                self.underlying].close_price / relative_days_to_expire * 365
            relative_basis_percentage_map[code] = adj_basis_point

        avg_adj_basis = sum([x for x in relative_basis_percentage_map.values() if x != 0]) / 3
        underlying_bar = bars[self.underlying]
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

        print(f"Relative basis map: {relative_basis_percentage_map} boll_up: {boll_up}")

        # Calculate which code to roll
        roll_to_code = None
        basis_map_str = json.dumps(basis_point_percentage_map, indent=2)
        relative_basis_percentage_map_str = json.dumps(relative_basis_percentage_map, indent=2)
        roll_reason = f"basis_map {basis_map_str} \n\n relative_basis_map {relative_basis_percentage_map_str} \n\n boll_up {boll_up}"

        days_to_expire = (self.get_expired_date(curr_pos) - current_date).days
        print(f"{current_date} 当前合约 {curr_pos} {days_to_expire} 日后到期")
        if days_to_expire == 1:
            roll_reason += "\n\n当前合约{curr_pos} {days_to_expire} 日后到期，即将到期，强制滚动"
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

        # 强制挂钩实盘仓位
        if current_date.date() == datetime(2021, 6, 28).date() and "IC2107.CFFEX" in code_list:
            roll_to_code = "IC2107.CFFEX"
        if current_date.date() == datetime(2021, 6, 28).date() and "IF2107.CFFEX" in code_list:
            roll_to_code = "IF2107.CFFEX"

        msg = f"{current_date} {roll_reason}"
        if roll_to_code is not None:
            # Roll position:
            print(msg)
            self.sell(curr_pos, price=bars[curr_pos].close_price * 0.92, volume=1)
            self.buy(roll_to_code, price=bars[roll_to_code].close_price * 1.08, volume=1)

        # 如果日期是今日，发送操作邮件
        if current_date.date() == datetime.today().date():
            if roll_to_code:
                print(f"{strategy_name}明日滚动\n{msg}")
                # send_server_chan(f"{strategy_name}明日滚动", msg)
            else:
                print(f"{strategy_name}不滚动\n{msg}")
                # send_server_chan(f"{strategy_name}不滚动", msg)

        self.put_event()


if __name__ == '__main__':
    strategy_name = "IC"
    # ic_symbol_list = prepare_ic_data_set(False)
    ic_symbol_list = ['000905.SSE', 'IC1602.CFFEX', 'IC1603.CFFEX', 'IC1604.CFFEX', 'IC1605.CFFEX', 'IC1606.CFFEX', 'IC1607.CFFEX', 'IC1608.CFFEX', 'IC1609.CFFEX', 'IC1610.CFFEX', 'IC1611.CFFEX', 'IC1612.CFFEX', 'IC1701.CFFEX', 'IC1702.CFFEX', 'IC1703.CFFEX', 'IC1704.CFFEX', 'IC1705.CFFEX', 'IC1706.CFFEX', 'IC1707.CFFEX', 'IC1708.CFFEX', 'IC1709.CFFEX', 'IC1710.CFFEX', 'IC1711.CFFEX', 'IC1712.CFFEX', 'IC1801.CFFEX', 'IC1802.CFFEX', 'IC1803.CFFEX', 'IC1804.CFFEX', 'IC1805.CFFEX', 'IC1806.CFFEX', 'IC1807.CFFEX', 'IC1808.CFFEX', 'IC1809.CFFEX', 'IC1810.CFFEX', 'IC1811.CFFEX', 'IC1812.CFFEX', 'IC1901.CFFEX', 'IC1902.CFFEX', 'IC1903.CFFEX', 'IC1904.CFFEX', 'IC1905.CFFEX', 'IC1906.CFFEX', 'IC1907.CFFEX', 'IC1908.CFFEX', 'IC1909.CFFEX', 'IC1910.CFFEX', 'IC1911.CFFEX', 'IC1912.CFFEX', 'IC2001.CFFEX', 'IC2002.CFFEX', 'IC2003.CFFEX', 'IC2004.CFFEX', 'IC2005.CFFEX', 'IC2006.CFFEX', 'IC2007.CFFEX', 'IC2008.CFFEX', 'IC2009.CFFEX', 'IC2010.CFFEX', 'IC2011.CFFEX', 'IC2012.CFFEX', 'IC2101.CFFEX', 'IC2102.CFFEX', 'IC2103.CFFEX', 'IC2104.CFFEX', 'IC2105.CFFEX', 'IC2106.CFFEX', 'IC2107.CFFEX', 'IC2108.CFFEX', 'IC2109.CFFEX', 'IC2110.CFFEX', 'IC2111.CFFEX', 'IC2112.CFFEX', 'IC2201.CFFEX', 'IC2202.CFFEX', 'IC2203.CFFEX', 'IC2204.CFFEX', 'IC2205.CFFEX', 'IC2206.CFFEX', 'IC2207.CFFEX', 'IC2208.CFFEX', 'IC2209.CFFEX']
    # print(f"IC SYMBOL LIST: {ic_symbol_list}")

    reload(vnpy.app.portfolio_strategy)

    engine = BacktestingEngine()

    rates = defaultdict(lambda: 0)
    slippages = defaultdict(lambda: 0)
    sizes = defaultdict(lambda: 300)
    priceticks = defaultdict(lambda: 0.1)

    start = datetime(2017, 1, 12)
    end = datetime.today()

    engine.set_parameters(
        vt_symbols=ic_symbol_list,
        interval=Interval.DAILY,
        start=start,
        end=end,
        rates=rates,
        slippages=slippages,
        sizes=sizes,
        priceticks=priceticks,
        capital=1_000_000,
    )

    setting = {
        "min_basis": 0,
        "underlying": '000905.SSE',
        "basis_return_only": False,
        "future_prefix": "IC"
    }
    engine.add_strategy(IndexFutureBasisStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()
