from vnpy.trader.database import get_database

from collections import defaultdict

from market_data.akshare_data_provider import AkShareDataProvider

class BackTestingWrapper():
    def __init__(self, data_provider=None):
        self.rates = defaultdict(lambda:0.000023)
        self.slippages = defaultdict(lambda:0)
        self.sizes = defaultdict(lambda:300)
        self.priceticks = defaultdict(lambda:0.1)
        self.capital = 1_000_000
        
        self.target_pos_map = {}
        self.target_pos_reason = {}
        
        self.engine = None
        
        if data_provider:
            self.data_provider = data_provider
        else:
            self.data_provider = AkShareDataProvider(get_database())
                        
    def get_strategy_name(self):
        return type(self).__name__
                
    def show_result(self):
        df = self.engine.calculate_result()

        self.engine.calculate_statistics()
        self.engine.show_chart()
        
    def get_latest_pos_date(self):
        return max(self.target_pos_map.keys())
    
    def get_latest_pos(self):
        latest_date = self.get_latest_pos_date()
        return self.target_pos_map[latest_date]
    
    def get_latest_pos_reasoning(self):
        latest_date = self.get_latest_pos_date()
        return self.target_pos_reason[latest_date]
