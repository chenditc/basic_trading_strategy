# basic_trading_strategy
基本的交易策略以及自动化

-------
# 安装设置
1. 安装 [vnpy studio](https://download.vnpy.com/vnstudio-2.4.0.exe)
2. 将 [strategies/utils/sample_system_configs.py](strategies/utils/sample_system_configs.py) 复制到 strategies/utils/system_configs.py 并修改成自己的值。

# 数据准备
目前使用的是 [tushare](https://tushare.pro/document/2) 的数据，下载后使用 vnpy 的数据管理库保存至本地 sqlite，如果希望接入其他数据源，可以参考 strategies/utils/tushare_data_download.py 的实现。

# 回测以及实盘交易
## 回测

在尝试了若干回测框架后发现 vnpy 的相对更灵活，可以对多个标的进行灵活切换，适合作为多资产配置的回测引擎。目前回测在 jupyter notebook 中执行。

## 实盘交易

目前实盘主要靠每日执行回测生成的交易信号发送邮件，在第二天开盘前用集合竞价的方式成交。

--------
# 策略目录

- [股指期货基差套利](strategies/cffex_back_testing.ipynb)
- [港股自动打新](hk_ipo_strategy.ipynb)


