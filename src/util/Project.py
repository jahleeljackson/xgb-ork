from pathlib import Path 
from typing import Dict, List
import subprocess 
import os
import yaml
from loguru import logger
from xgboost import XGBClassifier, XGBRegressor, Booster
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import click
import pandas as pd
from datetime import datetime 
from zoneinfo import ZoneInfo
import time
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json 
import numpy as np 

from util.types import Status, PredictionType
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

        logger.info(f"Training XGBoosted model.")

        logger.info("Retrieving parameters from params.yaml.")
        self.params: Dict = self._get_params()

        
        logger.info("Retrieving dataset from data store.")
        dataset: pd.DataFrame = datastore.retrieve(file_name=data_file)

        try:
            X = dataset.drop(columns=self.params["target_column"], axis=1)
            y = dataset[self.params["target_column"]]
        except:
            raise click.UsageError(f"Error getting target column. Make sure column is defined in params.yaml.")

        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y)

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

        start = time.perf_counter()
        xgb.fit(X_train_scaled, y_train)
        stop = time.perf_counter()

        duration = str(round(stop - start, 5)) + " seconds"

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

        run_time = self._get_time()

        metrics["train_time"] = duration

        model_run = {
            "name": model_name,
            "run time": run_time,
            "dataset": data_file,
            "metrics": metrics
        }

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


    def run(self, model: str) -> None: 
        model_path = self.path + f"/models/{model}.json"

        if not os.path.exists(model_path):
            raise click.UsageError(f"Model file {model}.json does not exist in project models directory.")

        logger.info(f"Loading XGBoost model from: {model_path}")

        # Load model
        booster = Booster()
        booster.load_model(model_path)

        # FastAPI Application ---------------------------------------------------
        app = FastAPI(
            title=f"{self.name} Inference Server",
            description="XGBoost model inference API with logging and monitoring.",
            version="1.0",
        )

        # Store monitoring stats
        inference_count = {"total": 0}
        last_latencies = []

        # Request schema
        class PredictRequest(BaseModel):
            data: List[Dict]

        # ----------------------------------------------------------------------
        # Routes
        # ----------------------------------------------------------------------

        @app.get("/health")
        def health():
            return {"status": "ok", "model": model}

        @app.get("/metadata")
        def metadata():
            return {
                "project": self.name,
                "model_file": f"{model}.json",
                "prediction_type": str(self.ptype),
                "loaded": True
            }

        @app.get("/metrics")
        def metrics():
            return {
                "total_inferences": inference_count["total"],
                "recent_latencies_ms": last_latencies[-20:]
            }

        @app.post("/predict")
        def predict(payload: PredictRequest):
            logger.info("Received prediction request")

            # Convert to matrix
            try:
                df = pd.DataFrame(payload.data)
            except Exception as e:
                logger.error(f"Invalid input format: {e}")
                return {"error": "Invalid input format"}

            start = time.perf_counter()

            try:
                # Booster requires DMatrix input
                import xgboost as xgb
                dmatrix = xgb.DMatrix(df)
                preds = booster.predict(dmatrix)
                preds_list = preds.tolist()
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                return {"error": "Prediction failure"}

            stop = time.perf_counter()
            latency_ms = round((stop - start) * 1000, 4)

            inference_count["total"] += 1
            last_latencies.append(latency_ms)

            logger.info(
                f"Prediction done | latency={latency_ms}ms | num_records={len(df)}"
            )

            return {
                "predictions": preds_list,
                "latency_ms": latency_ms,
                "records": len(df)
            }

        # ----------------------------------------------------------------------
        # Start server
        # ----------------------------------------------------------------------

        logger.info("Starting inference server...")

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )


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
        print(f"Latest Model Run: {info["project_info"]["models"][-1]}") 



    def save_model(self, model_name: str, model: XGBClassifier | XGBRegressor) -> Status:
        
        model_path = self.path + f"/models/{model_name}.json"

        try:
            booster = model.get_booster()
            booster.save_model(model_path)
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
    
    def _get_time(self) -> str:
        tz = ZoneInfo("UTC")
        now = datetime.now(tz)
        return str(now)[10:19]