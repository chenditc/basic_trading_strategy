#encoding:gbk
'''
自动打新并且开板后卖出
'''
import requests
import datetime
import json

class MyStrategyObject():
	ipo_complete_map = {}
	new_stock_tracking_complete_map = {}
	new_stock_tracking_start_map = {}
	ipo_bond_complete_map = {}

def send_notification_log(title, text):
	print("Logging to azure", title, text)
	url = "https://di-trading-log.azurewebsites.net/api/log_event?code=gMcbj7J1vKh/VCs8e2MkVaHRp/4NLz8dttpgk03p8SMKcJQHo/8JKQ=="
	data = {
		"title" : title,
		"desp" : text,
	}
	try_cnt = 0
	while try_cnt < 5:
		try:
			response = requests.post(url, data=json.dumps(data))
			print(response.content)
			return
		except Exception as e:
			print(e)
			try_cnt += 1
    
def get_applied_code_set(ContextInfo):
	applied_code_set = set()
	order_list = get_trade_detail_data(ContextInfo.accID, "STOCK", "ORDER")
	for order in order_list:
		if order.m_nOrderStatus == 57: #  废单
			continue
		elif order.m_nOrderStatus == 50:
			stock_code = f"{order.m_strInstrumentID}.{order.m_strExchangeID}"
			applied_code_set.add(stock_code)
		else:
			print(f"Unknown status code: {order.m_strCancelInfo}")
	return applied_code_set
	
def get_blacklist_fail_code(ContextInfo, threshold=6):
	failed_reason_map = {}
	order_list = get_trade_detail_data(ContextInfo.accID, "STOCK", "ORDER")
	for order in order_list:
		if order.m_nOrderStatus == 57: #  废单
			stock_code = f"{order.m_strInstrumentID}.{order.m_strExchangeID}"
			print(stock_code, order.m_strCancelInfo)
			reason_list = failed_reason_map.get(stock_code, [])
			reason_list.append(order.m_strCancelInfo)
			failed_reason_map[stock_code] = reason_list

	blacklist_code = {}
	for code, reason_list in failed_reason_map.items():
		if len(reason_list) > threshold:
			blacklist_code[code] = set(reason_list)
	return blacklist_code
	
def init(ContextInfo):
	print("Init strategy")
	ContextInfo.accID = '102666'
	ContextInfo.strategy_obj = MyStrategyObject()
	
def handlebar(ContextInfo):
	# Only last bar can trade
	if not ContextInfo.is_last_bar():
		return 
	
	# First bar is not stable
	if 	ContextInfo.time_tick_size <= 1:
		return
		
	# Run once for each bar, when new bar is generated
	if not ContextInfo.is_new_bar():
		return
		
	current_time_str = datetime.datetime.now().strftime("%H%M")
	if current_time_str < "0930" or current_time_str > "1500":
		print("不在交易时间")
		return
		
	if current_time_str > "1130" and current_time_str < "1300":
		print("不在交易时间")
		return
		
	today_date = datetime.datetime.today().date().strftime("%Y-%m-%d")

	
	if today_date not in ContextInfo.strategy_obj.ipo_complete_map:
		# 获取当日可打新股
		print("开始打新股")
		ipo_stock = get_ipo_data("STOCK")
		ipo_bond = get_ipo_data("BOND")
		ipo_stock.update(ipo_bond)
		print("今日新股：", ipo_stock)
		blacklist_code = get_blacklist_fail_code(ContextInfo)
		applied_code_set = get_applied_code_set(ContextInfo)
		print("applied code:", applied_code_set)
		print("black list code:", blacklist_code)
		
		ipo_stock_to_apply = [ stock_code for stock_code in ipo_stock.keys() if 
			(stock_code not in applied_code_set and stock_code not in blacklist_code)]
		if len(ipo_stock_to_apply) == 0:
			text = f"{today_date}所有新股完成申购完成，已申购成功： {applied_code_set}"
			if len(blacklist_code) > 0:
				text += f"，申购失败： {blacklist_code}"
			send_notification_log("A股新股申购完成", text)
			ContextInfo.strategy_obj.ipo_complete_map[today_date] = text
		
		# 针对每只新股下单
		for stock_code in ipo_stock_to_apply:
			stock_info = ipo_stock[stock_code]
			print(f"Place ipo order for {stock_code}")
			#order_shares(stock_code, stock_info["maxPurchaseNum"], ContextInfo, ContextInfo.accID)
			print(stock_info)
			passorder(23,1101,ContextInfo.accID,stock_code,5,stock_info["issuePrice"],stock_info["maxPurchaseNum"],1,ContextInfo)
	
	if today_date not in ContextInfo.strategy_obj.new_stock_tracking_complete_map:
		# 查看当前持仓情况，获取次新股列表
		two_month_ago = (datetime.datetime.today() - datetime.timedelta(days=60)).strftime("%Y%m%d")
		position_list = get_trade_detail_data(ContextInfo.accID, "STOCK", "POSITION")
		new_pos_map = {}
		for position in position_list:
			stock_code = f"{position.m_strInstrumentID}.{position.m_strExchangeID}"
			open_date = ContextInfo.get_open_date(stock_code)
			up_stop_price = ContextInfo.get_instrumentdetail(stock_code)["UpStopPrice"]
			last_price = ContextInfo.get_market_data(["close"], stock_code = [stock_code], skip_paused = True, period = '1m', dividend_type = 'none', count = -1)
			if str(open_date) > two_month_ago and position.m_nVolume != 0:
				new_pos_map[stock_code] = {
					"up_stop_price" : up_stop_price,
					"name" : position.m_strInstrumentName,
					"vol": position.m_nVolume,
					"open_date": str(open_date),
					"last_price" : last_price
				}
			print(stock_code, position.m_strInstrumentName, open_date)
		print("当前新股持仓: ", new_pos_map)
		
		if len(new_pos_map) == 0:
			print("新股跟踪已完成")
			send_notification_log("A股新股跟踪", "新股跟踪已完成")
			ContextInfo.strategy_obj.new_stock_tracking_complete_map[today_date] = "No new stock"
		elif today_date not in ContextInfo.strategy_obj.new_stock_tracking_start_map:
			ContextInfo.strategy_obj.new_stock_tracking_start_map[today_date] = 1
			send_notification_log("A股新股跟踪", f"开始跟踪新股走势: {new_pos_map}")
	
		# 查看对应股票的最新价是否为涨停价
		for stock_code, pos_info in new_pos_map.items():
			name = pos_info["name"]
			if ContextInfo.get_bvol(stock_code) == 0:
				print(f"No volume, skip this stock {name} for now")
				continue
			if pos_info["last_price"] < pos_info["up_stop_price"] * 0.99:
				last_price = pos_info["last_price"]
				up_stop_price = pos_info["up_stop_price"]
				text = f"新股开板，应当卖出{name},当前价格: {last_price},涨停价格: {up_stop_price}"
				send_notification_log("A股新股卖出", text)
		
		# 卖出非涨停且不在上涨趋势的股票，上涨趋势定义为30分钟均线高于3小时均线。
	
	print("======================================================")
