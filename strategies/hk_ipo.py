import livermore
import livermore.backend
import datetime
import time
import pandas
import logging

from utils.system_configs import livermore_config
from utils.email_util import send_notification

logger = logging.getLogger(__name__)
backend = livermore.backend.TradeBackend(key=livermore_config["key"], secret=livermore_config["secret"])

def get_holding_stock_df():
    stock_list = backend.get_stock_info(ignore_clean_stock="0", exchange_type="ALL")["data"]["list"]
    stock_list_df = pandas.DataFrame.from_dict(stock_list)
    stock_list_df
    return stock_list_df

def get_cancelable_order_df():
    order_list = backend.get_withdraw()["data"]["list"]
    order_list_df = pandas.DataFrame.from_dict(order_list)
    order_list_df
    return order_list_df

def cancel_all_orders():
    order_list_df = get_cancelable_order_df()
    for ix, order_row in order_list_df.iterrows():
        backend.entrust_withdraw(batch_flag="0", 
                                 entrust_amount=order_row["entrust_amount"],
                                 entrust_price=order_row["entrust_price"],
                                 entrust_no_first=order_row["entrust_no"], 
                                 stock_code=order_row["stock_code"], 
                                 entrust_type="2", 
                                 exchange_type=order_row["exchange_type"], 
                                 session_type="0")

def sell_current_holding_stock():
    # Sell current holding stock
    current_stock_df = get_holding_stock_df()
    sold_stock_map = {}

    # cancel current order and place again
    cancel_all_orders()
    time.sleep(5)


    for ix, stock_row in current_stock_df.iterrows():
        stock_name = stock_row["stock_namegb"]
        stock_code = stock_row["stock_code"]
        amount = stock_row["current_amount"]
        keep_cost_price = float(stock_row["keep_cost_price"])
        if float(amount) == 0:
            continue
        price = str(float(stock_row["last_price"]))
        result = backend.entrust_stock(stock_code=stock_code, 
                              entrust_amount=amount, 
                              entrust_price=price, 
                              entrust_bs="2",  # 卖出
                              entrust_type="0", # 买卖
                              entrust_prop="h", 
                              auto_exchange="True",
                              session_type="0") # 0 正股，2 暗盘
        if result["code"] != 0:
            logger.error(f"Failed to create sell order for stock {stock_name}")
            logger.error(result)
        else:
            sold_stock_map[stock_name] = {
                "price" : price,
                "amount" : amount,
                "cost_price": keep_cost_price
            }
    return sold_stock_map
        
def get_applied_ipo_info_list():
    data_list = []
    is_last = False
    last_position_str = "2050"
    while not is_last:
        result = backend.get_ipo_detail(last_position_str)
        data_list += result["data"]["data_list"]
        is_last = result["data"]["is_last"]
        last_position_str = result["data"]["last_position_str"]
    return data_list

def get_applied_ipo_code_map():
    data_list = get_applied_ipo_info_list()
    applied_code_map = { x["stock_code"]:x["deposit_amount"] for x in data_list }
    return applied_code_map
        
def check_new_allotted_stock():
    new_stock_allotted = {}

    today_str = datetime.datetime.today().strftime("%Y%m%d")
    ipo_apply_df = pandas.DataFrame.from_dict(get_applied_ipo_info_list())
    
    ipo_apply_df = ipo_apply_df[ipo_apply_df["status"] > "2"]
    ipo_apply_df = ipo_apply_df[ipo_apply_df["trading_date"] > today_str]

    for ix, stock_row in ipo_apply_df.iterrows():
        stock_name = stock_row["stock_namegb"]
        amount = float(stock_row["quantity_allotted"])
        apply_amount = stock_row["apply_amount"]
        if amount == 0:
            continue
        new_stock_allotted[stock_name] = apply_amount
        logger.info(f"新股中签：{amount}股{stock_name}共计{apply_amount}元")
    return new_stock_allotted
        
def apply_one_hand_ipo(stock_code, user_fund, future_fund):
    print(f"Applying for code {stock_code}")
    ipo_number = backend.get_ipo_number(stock_code)
    ipo_number["data"]["ipo_numbers"]
    ipo_num_df = pandas.DataFrame.from_dict(ipo_number["data"]["ipo_numbers"])
    first_row = ipo_num_df.iloc[0,:]
    quantity_apply = first_row["shared_applied"]
    apply_amount = first_row["applied_amount"]
    deposit_amount = first_row.get("min_cash", apply_amount)
    
    if user_fund < float(deposit_amount):
        if future_fund < float(deposit_amount):
            msg = f"打新钱不够。当前余额{user_fund} 需要: {deposit_amount}, 截止日: {future_fund}"
            return False, msg
        else:
            msg = f"暂时打新钱不够。当前余额{user_fund} 需要: {deposit_amount}, 截止日: {future_fund}"
            return False, msg
    
    apply_result = backend.set_ipo_detail(stock_code, quantity_apply=quantity_apply, apply_amount=apply_amount, deposit_rate="0", deposit_amount=deposit_amount, type_="1", action_in="0")
    apply_result
    
    if apply_result["code"] == 0:
        msg = f"apply_success: {apply_result}"
        return True, msg
    else:
        error_code = apply_result["data"]["error_no"]
        msg = f"apply_failed: {apply_result} error code: {error_code}"
        return False, msg

def get_user_ipo_balance():
    user_fund = backend.get_user_fund()
    current_ipo_balance = float(user_fund["data"]["ipo_balance"])
    return current_ipo_balance
    
    
def apply_ipo(sold_stock_map, new_stock_allotted):
    # 获取新股信息
    result = backend.get_ipo_list()
    ipo_list_df = pandas.DataFrame.from_dict(result["data"])

    if len(ipo_list_df) > 0:
        ipo_list_df = ipo_list_df[["stock_code", "stock_namegb", "lm_steady_hand", "lm_min_amount", "lm_low_price", "application_begins", "close_date", "deposit_date", "pre_over_subscribed_multiple", "lm_over_subscribed_multiple"]]
        ipo_list_df.loc[:,"pre_over_subscribed_multiple"] = ipo_list_df["pre_over_subscribed_multiple"].astype(float)

        # Only show close_date > today
        ipo_list_df = ipo_list_df[ipo_list_df["close_date"] > datetime.datetime.today().strftime("%Y%m%d")]
        # Sort by subscribed multiple
        ipo_list_df.loc[:,"over_subscribed"] = ipo_list_df["pre_over_subscribed_multiple"] > 1

        ipo_list_df = ipo_list_df.sort_values(["over_subscribed","deposit_date","pre_over_subscribed_multiple"], ascending=[False, True, False])

        ipo_list_df
    else:
        return
        
    applied_code_map = get_applied_ipo_code_map()
    current_ipo_balance = get_user_ipo_balance()

    failure_msg_list = []
    success_msg_list = []
    for ix, row in ipo_list_df.iterrows():
        stock_code = row["stock_code"]
        if stock_code in applied_code_map:
            logger.info(f"Already applied {stock_code}, skipping")
            continue

        refund_deposit = 0
        for refund_stock_code in ipo_list_df[ipo_list_df["deposit_date"] <= row["close_date"]]["stock_code"].to_list():
            refund_deposit += float(applied_code_map[refund_stock_code])

        success, msg = apply_one_hand_ipo(stock_code, current_ipo_balance, refund_deposit + current_ipo_balance)
        if not success:
            msg = row["stock_namegb"] + ":" + msg + f", close date: {row.close_date}"

            failure_msg_list.append(msg)
            logger.debug(msg)
        else:
            current_ipo_balance = get_user_ipo_balance()
            success_msg_list.append(row["stock_namegb"])


    final_msg = ""
    if len(failure_msg_list) == 0 and len(success_msg_list) == 0:
        final_msg = "今日无可操作新股"

    if len(failure_msg_list) > 0:
        final_msg += "打新失败:\n" + "\n".join(failure_msg_list)

    if len(success_msg_list) > 0: 
        final_msg += "\n成功打新: \n" + "\n".join(success_msg_list)

    if len(new_stock_allotted) > 0:
        for stock_name, amount in new_stock_allotted.items():
            final_msg += f"\n新股中签：{stock_name} 共 {amount} 元"
    else:
        final_msg += "\n无新股中签"

    if len(sold_stock_map) > 0:
        for stock_name, info_map in sold_stock_map.items():
            cost_price = float(info_map["cost_price"])
            price = float(info_map["price"])
            amount = float(info_map["amount"])
            profit = amount * (price - cost_price)
            final_msg += f"\n卖出{amount}股{stock_name}：成本价{cost_price},卖出价{price}，盈亏：{profit}"
    else:
        final_msg += "\n无卖出操作"

    logger.info(final_msg)
    send_notification("港股每日打新情况", final_msg)
    return final_msg
    
def main():
    # 登陆
    stock_info_result = backend.get_stock_info(ignore_clean_stock="0", exchange_type="ALL")
    stock_info_result

    if stock_info_result["code"] != 0:
        logger.warning(f"System is down:")
        send_notification("港股每日打新情况", f"系统错误无法使用：{stock_info_result}")
        raise Exception(stock_info_result)
        
    sold_stock_map = sell_current_holding_stock()
    new_stock_allotted = check_new_allotted_stock()
    apply_ipo(sold_stock_map, new_stock_allotted)
        
if __name__ == "__main__":
    main()