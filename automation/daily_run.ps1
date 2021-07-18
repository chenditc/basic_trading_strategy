C:\vnstudio\Scripts\papermill.exe C:\Users\chenditc\Desktop\dev\strategies\cffex_back_testing.ipynb C:\Users\chenditc\Desktop\dev\daily_result\daily_ic_backtesting.ipynb -p strategy_name IC --cwd C:\Users\chenditc\Desktop\dev\strategies
C:\vnstudio\Scripts\papermill.exe C:\Users\chenditc\Desktop\dev\strategies\cffex_back_testing.ipynb C:\Users\chenditc\Desktop\dev\daily_result\daily_if_backtesting.ipynb -p strategy_name IF --cwd C:\Users\chenditc\Desktop\dev\strategies
jupyter nbconvert --to html C:\Users\chenditc\Desktop\dev\daily_result\daily_if_backtesting.ipynb
jupyter nbconvert --to html C:\Users\chenditc\Desktop\dev\daily_result\daily_ic_backtesting.ipynb
cp  -Recurse -Force C:\Users\chenditc\Desktop\dev\daily_result\ E:\