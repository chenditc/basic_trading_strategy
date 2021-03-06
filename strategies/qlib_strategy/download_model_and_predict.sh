# Download model
/qlib_trading/coscli cp cos://trade/models/alpha_158_open_8.ml /qlib_trading//alpha_158_open_8.ml 
# Dump latest data
cd /investment_data/
bash /investment_data/dump_qlib_bin.sh
mkdir -p ~/.qlib/qlib_data/cn_data
tar -zxvf qlib_bin.tar.gz -C ~/.qlib/qlib_data/cn_data --strip-components=2
# Run prediction
cd /qlib_trading/
python predict.py --model_path /qlib_trading//alpha_158_open_8.ml
for file in $(ls *.csv) 
do   
  /qlib_trading/coscli cp $file cos://trade/predict/$file
done
