# basic_trading_strategy
基本的交易策略以及自动化

-------
# 安装设置
## 使用预先打包的 docker
```shell
docker run  -it --rm \
  -v $(pwd)/vt_setting.json:/root/.vntrader/vt_setting.json \
  -v $(pwd)/system_config.py:/strategies/utils/system_configs.py \
  chenditc/ditrading:latest
```
- 配置运行目录下的 vt_settings.json 可以使用不同的数据库，不配置则使用临时的 sqlite 数据库，docker 停止后即销毁。配置方式参考 [vnpy数据库配置](https://www.bookstack.cn/read/vnpy-2.5-zh/87bfaf6600a70114.md)
- 配置运行目录下的 system_config.py 可以调整其他的参数，例如推送的配置，回调，Azure App Insight 的配置。配置样例参考 [sample_system_config.py](https://github.com/chenditc/basic_trading_strategy/blob/main/strategies/utils/sample_system_configs.py)

## 自己编译docker
如果需要自己编译 docker，使用 Dockerfile 编译后运行即可。

# 数据准备
目前使用的是
1. [tushare](https://tushare.pro/document/2)
2. [akshare](https://www.akshare.xyz/)

在策略执行时会自动进行数据的下载更新

# 回测开发
启动开发环境：
```shell
docker run  -it --rm \
  -e JUPYTER_TOKEN=xxxxxx \
  -v $(pwd)/vt_setting.json:/root/.vntrader/vt_setting.json \
  -v $(pwd):/strategies \
  -p 8888:8888 \
  chenditc/ditrading:latest
```

将本地目录挂载至 jupyter 的启动目录，然后在 jupyter notebook 中进行测试和调试。Jupyter notebook 的访问 token 是 `JUPYTER_TOKEN` 环境变量对应的值。

在尝试了若干回测框架后发现 vnpy 的相对更灵活，可以对多个标的进行灵活切换，适合作为多资产配置的回测引擎。目前使用 vnpy 作为回测引擎。

# 实盘交易
实盘运行：
```shell
docker run -d --rm \
  -v $(pwd)/vt_setting.json:/root/.vntrader/vt_setting.json \
  -v $(pwd)/system_config.py:/strategies/utils/system_configs.py
  chenditc/ditrading:latest \
  python3 /scripts/daily_strategy_run.py 
```

在 [scripts/daily_strategy_run.py](scripts/daily_strategy_run.py) 中存放了每日需要跑的策略定义。 

目前实盘主要靠每日执行回测生成的交易信号发送推送，在第二天开盘前用集合竞价的方式成交。
目前设置为：
1. 早上10点执行港股自动打新策略。
2. 每天晚上8点跑 IF 和 IC 基差滚动策略。
3. 早上10点执行A股自动打新策略。

--------
# 策略目录

- [股指期货基差套利](strategies/spread_rolling_bt.ipynb)
- [港股自动打新](strategies/hk_ipo_strategy.ipynb)
- [蜘蛛网策略](strategies/spider_back_testing.ipynb)


