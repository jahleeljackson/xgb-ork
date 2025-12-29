from typing import Any, Dict
from pathlib import Path
import json



class ModelInfo:
    def __init__(self, project_name: str):
        self.project_name: str = project_name 
        self.file_path: str = str(Path(__file__).parent.parent / "PROJECT-STORE" / self.project_name / "info.json")
        self.json: Dict = self._get_info()


    def update(self, info_title: str, value: Any):
        info = self.json
        
        if info_title == "name":
            info["project_info"]["name"] = value
        if info_title == "models":
            info["project_info"]["models"].append(value)
        if info_title == "created_at": 
            info["project_info"]["created_at"] = value
        if info_title == "champion":
            info["project_info"]["champion"] = value

        self.json = info
        with open(self.file_path, 'w') as file:
            json.dump(info, file, indent=4)


    def read(self) -> Dict:
        return self.json


    def _get_info(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)  # Deserializes file content to a Python object

