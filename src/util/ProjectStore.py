from pathlib import Path
import subprocess
import os
from typing import List
from loguru import logger
import click
from datetime import datetime 
from zoneinfo import ZoneInfo

from util.types import PredictionType
from util.ModelInfo import ModelInfo

class ProjectStore:
    def __init__(self):
        self.root: str = str(Path(__file__).parent.parent / "PROJECT-STORE")
        self.projects: List[str] = self._get_projects()


    def add(self, name: str, ptype: PredictionType):

        logger.info(f"Adding {name} to project store...")

        project_path: str = self.root + f"/{name}"
        template_dir: str = str(Path(__file__).parent.parent / "templates" / ("c_template" if ptype == PredictionType.C else "r_template"))


        try:
            subprocess.run(["cp", "-r", template_dir, project_path], check=True)

            modelinfo = ModelInfo(project_name=name)
            modelinfo.update(info_title="created_at", value=self._get_datetime())
            modelinfo.update(info_title="name", value=name)

            self.projects = self._get_projects()
            logger.info(f"{name} successfully added to project store.")
        
        except Exception as e:
            print(f"Error add {name} to project store.")


    def display(self):
        projects: List[str] = self.projects
        if len(projects) == 0:
            print("No existing projects.")

        else:
            print("Projects:")
            for project in projects:
                print(f"- {project}")


    def delete(self, name: str):

        if name not in self.projects:
            raise click.UsageError(f"{name} is not an existing project.")



        project_path: str = self.root + f"/{name}"

        try:
            subprocess.run(["rm", "-rf", project_path], check=True)
            logger.info(f"{name} successfully deleted.")
        
        except Exception as e:
            print(f"Error add {name} to project store.")


    def project_exists(self, name: str) -> bool:
        if name in self.projects:
            return True 
        return False

    def _get_projects(self) -> List[str]:
        return os.listdir(self.root)


    def _get_datetime(self) -> str:
        tz = ZoneInfo("UTC")
        now = datetime.now(tz)
        return str(now)[:10]
    

