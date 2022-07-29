FROM chenditc/investment_data
COPY ./ /qlib_trading
RUN wget https://cosbrowser.cloud.tencent.com/software/coscli/coscli-linux -O /qlib_trading/coscli && chmod 755 /qlib_trading/coscli
CMD bash /qlib_trading/download_model_and_predict.sh