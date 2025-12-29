from enum import Enum 
from dataclasses import dataclass
from typing import Dict

class Status(Enum):
    Ok = True 
    Err = False

class PredictionType(Enum):
    C = "classification"
    R = "regression"

@dataclass 
class ModelRun:
    name: str
    metrics: Dict