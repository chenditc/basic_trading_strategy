import qlib
from qlib.constant import REG_CN
from qlib.utils import exists_qlib_data, init_instance_by_config
import pickle
import os
from pathlib import Path
import fire

def dump_predict_using_model(model_path = "trained_model", output_directory = "./"):
  # Init data
  provider_uri = "~/.qlib/qlib_data/cn_data"
  if not exists_qlib_data(provider_uri):
      raise Exception(f"Qlib data is not found in {provider_uri}")
  qlib.init(provider_uri=provider_uri, region=REG_CN)

  # Prepare dataset 
  data_handler_config = {
    "start_time": "2022-07-01",
    "end_time": "2055-07-22",
    "fit_start_time": "2022-07-01",
    "fit_end_time": "2022-07-02",
    "instruments": "csi300",
  }

  dataset_config =  {
          "class": "DatasetH",
          "module_path": "qlib.data.dataset",
          "kwargs": {
              "handler": {
                  "class": "Alpha158",
                  "module_path": "qlib.contrib.data.handler",
                  "kwargs": data_handler_config,
              },
              "segments": {
                  "test": ("2022-07-01", "2025-07-29"),
              },
          },
  }
  dataset = init_instance_by_config(dataset_config)

  with Path(model_path).open("rb") as f:
    model = pickle.Unpickler(f).load()

  pred_df = model.predict(dataset)

  last_item_index = pred_df.iloc[-1:].index[0]
  last_item_datetime = last_item_index[0]
  latest_score_list = pred_df.at[last_item_datetime].sort_values(ascending=False)

  output_file_name = last_item_datetime.strftime("%Y-%m-%d") + ".csv"

  output_file_path = os.path.join(output_directory, output_file_name)
  latest_score_list.to_csv(output_file_path)

if __name__ == "__main__":
  fire.Fire(dump_predict_using_model)