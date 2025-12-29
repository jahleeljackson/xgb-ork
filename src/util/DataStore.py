from typing import List
from pathlib import Path
import os
import subprocess
import click
from loguru import logger
import pandas as pd

from util.types import Status

class DataStore:
    def __init__(self):
        self.root: str = str(Path(__file__).parent.parent / "DATA-STORE")
        self.files: List[str] = self._get_files()

    def add(self, source_file: str, file_name: str) -> Status:

        if f"{file_name}.csv" in self.files:
            raise click.UsageError(f"{file_name}.csv already exists.")


        file_path: str = self.root + f"/{file_name}.csv"

        try:
            logger.info(f"Adding {file_path} to data store...")
            subprocess.run(["cp", "-r", source_file, file_path], check=True)
            self.files = self._get_files()
            logger.info(f"{file_path} successfully added.")
            return Status.Ok
        
        except:
            return Status.Err
        
    
    def expand(self, file_name: str):
        if not self.file_exists(file_name=file_name):
            raise click.UsageError(f"{file_name} is not an available dataset")
        data_path = self.root + f"/{file_name}.csv"
        df = pd.read_csv(data_path)
        print(df)


    def retrieve(self, file_name: str) -> pd.DataFrame:
        data_path = self.root + f"/{file_name}.csv"
        try:
            logger.info(f"{file_name} successfully retrieved from data store...")
            return pd.read_csv(data_path)
            
        except Exception as e:
            print(f"Error retrieving dataset {file_name}: ", e)


    def show(self) -> None:
        if len(self.files) == 0:
            print("No datasets available.")
        for file in self.files:
            print(file) 


    def delete(self, file_name: str) -> Status:

        if f"{file_name}.csv" not in self.files:
            raise click.UsageError(f"{file_name}.csv does not exist.")

        file_path: str = self.root + f"/{file_name}.csv"

        try:
            logger.info(f"{file_name} successfully deleted from data store...")
            subprocess.run(["rm", "-rf", file_path], check=True)
            self.files = self._get_files()
            return Status.Ok

        except:
            return Status.Err


    def file_exists(self, file_name: str) -> bool:
        return file_name + ".csv" in self.files


    def _get_files(self):
        return os.listdir(self.root)