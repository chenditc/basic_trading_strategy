from typing import List, Dict
from datetime import datetime
import re
import json
        
from vnpy.app.portfolio_strategy import StrategyTemplate, StrategyEngine, BacktestingEngine

class TargetPosStrategyTemplate(StrategyTemplate):

    author = "chendi"

    # params
    verbose = False
    target_pos_map = None

    parameters = [
        "target_pos_map",
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
            if vol == 0:
                continue
            assert(curr_pos == None)
            curr_pos = pos
            curr_vol = vol
        return curr_pos, curr_vol
        
    def get_curr_pos_map(self):
        curr_pos_map = {}
        for pos, vol in self.pos.items():
            if vol == 0:
                continue
            assert(pos != None)
            curr_pos_map[pos] = vol
        return curr_pos_map
        
    def trade_to_target_pos(self, target_pos, bars, on_error="stop"):
        curr_pos_map = self.get_curr_pos_map()
        if curr_pos_map == target_pos:
            #print("持仓不变不操作")
            return
        
        for pos in (set(target_pos.keys()) | set(curr_pos_map.keys())):
            pos_diff = target_pos.get(pos, 0) - curr_pos_map.get(pos, 0) 
            if pos_diff == 0:
                continue
                
            if pos not in bars:
                if on_error == "continue":
                    continue
                else:
                    raise Exception(f"No price for {pos}")
                
            if pos_diff > 0:
                self.buy(pos, price=bars[pos].close_price * 1.1, volume=abs(pos_diff))
            else:
                self.sell(pos, price=bars[pos].close_price * 0.9, volume=abs(pos_diff))