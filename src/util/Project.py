from pathlib import Path 
from typing import Dict, List
import subprocess 
import os
import yaml
from loguru import logger
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
import click
import pandas as pd

from util.types import Status, PredictionType, ModelRun
from util.DataStore import DataStore 
from util.ModelInfo import ModelInfo


datastore = DataStore()


class Project:
    def __init__(self, name: str):
        self.name: str = name 
        self.ptype: PredictionType = self._get_ptype()
        self.path: str = str(Path(__file__).parent.parent / "PROJECT-STORE" / name)
        self.params: Dict
        self.models: List[str] = self._get_models()
        self.champion: str
        self.modelinfo = ModelInfo(project_name=self.name)


    def train_xgb(self, data_file: str) -> None:

        if not datastore.file_exists(file_name=data_file):
            raise click.UsageError(f"{data_file} does not exist in data store.")

        logger.info(f"Training XGBoosted {self.ptype.value} model.")

        logger.info("Retrieving parameters from params.yaml.")
        self.params: Dict = self._get_params()

        
        logger.info("Retrieving dataset from data store.")
        dataset: pd.DataFrame = datastore.retrieve(file_name=data_file)

        X = dataset.drop(columns=self.params["target_column"])
        y = dataset[self.params["target_column"]]

        X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                            test_size=self.params["test_size"],
                                                            random_state=self.params["random_state"])
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model_params = {
            k: v for k, v in self.params.items()
            if k not in ["target_column", "test_size", "model_name"]
        }

        if self.ptype == PredictionType.R:
            xgb = XGBRegressor(**model_params)
        else:
            xgb = XGBClassifier(**model_params)

        
        xgb.fit(X_train_scaled, y_train)

        if self.ptype == PredictionType.R:
            preds = xgb.predict(X_test_scaled)
            metrics = {
                "MAE": mean_absolute_error(y_test, preds),
                "MSE": mean_squared_error(y_test, preds),
                "R2": r2_score(y_test, preds)
            }
        else:
            preds = xgb.predict(X_test_scaled)
            metrics = {
                "Accuracy": accuracy_score(y_test, preds),
                "F1": f1_score(y_test, preds, average="weighted"),
                "Precision": precision_score(y_test, preds, average="weighted", zero_division=0),
                "Recall": recall_score(y_test, preds, average="weighted", zero_division=0)
            }

        logger.info(f"Model performance: {metrics}")


        model_name = self.params["model_name"]
        
        model_run = ModelRun(name=model_name, metrics=metrics)

        self.modelinfo.update(info_title="models", value=model_run)

        logger.info(f"Model metrics successfully saved for {model_name}")

        if self.save_model(model_name=model_name, model=xgb) == Status.Ok:
            print(f"XGBoost model successfully saved to {model_name}.")


    def config_model(self) -> None:

        params_file = self.path + f"/config/params.yaml"

        try:
            subprocess.run(["vim", params_file], check=True)

        except Exception as e:
            print(f"Error configuring {self.name}'s model parameters: ", e)


    def run(self, model: str, data_path: str, mode: str = "default") -> None: 
        pass


            

    def delete_model(self, name: str) -> Status:

        model_path = self.path + f"/models/{name}.pkl"

        try:
            subprocess.run(["rm", "-rf", model_path], check=True)
            self.models = self._get_models()
            return Status.Ok
        
        except:
            return Status.Err
        

    def show(self) -> None:
        info: Dict = self.modelinfo.read()
        print(f"Project Name: {info["project_info"]["name"]}") 
        print(f"Created At: {info["project_info"]["created_at"]}")
        print(f"Prediction Type: {info["project_info"]["prediction_type"]}") 
        print(f"Model Runs: {info["project_info"]["models"]}") 



    def save_model(self, model_name: str, model: XGBClassifier | XGBRegressor) -> Status:
        
        model_path = self.path + f"/models/{model_name}.json"

        try:
            model.save_model(model_path)
            return Status.Ok

        except Exception as e:
            print(f"Error saving {model_name}.json to {self.name}: ", e)
            return Status.Err


    def _get_ptype(self):
        modelinfo = ModelInfo(project_name=self.name).read()
        return modelinfo["project_info"]["prediction_type"]


    def _get_params(self):

        params_file = self.path + f"/config/params.yaml"

        try:
            with open(params_file, 'r') as file:
                return yaml.safe_load(file)
        
        except Exception as e:
            print(f"Error loading model parameters for {self.name}: ", e)


    def _get_champion(self):
        pass


    def _get_models(self):
        models_dir = self.path + "/models"
        return os.listdir(models_dir)