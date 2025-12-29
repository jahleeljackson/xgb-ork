# XGBoosted Orchestrator

## Project Description

This project proposes to simplify the model deployment and monitoring workflow for the open-source [XGBoost](https://xgboost.readthedocs.io/en/stable/) library. Key features entail:

1. Realtime monitoring of model metrics
    
    Critical metrics of a model should be continuously presented to users via the terminal or browser. 

2. Logging & interval configuration

    Model events and metrics should be automatically logged to a persistent store. Access to logged information should be as simple and intuitive as possible.

3. Model configuration

    The parameters of the model should be able to configured via the terminal in an elegant way. 

4. Model project instantiation

    Workflows are abstracted into individual project instances which contain specified configurations and metadata. 


**Commands**

```bash
# Project Store level
xgb init {r|c} {project_name}
xgb list
xgb delete {project_name}

# Data Store level
xgb add {data_path} {data_name}
xgb data
xgb remove {data_name}

# Project Instance level
xgb train {project_name} {dataset}
xgb config {project_name} 
xgb show {project_name}

```