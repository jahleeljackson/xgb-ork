# XGBoosted Orchestrator

## Project Description

This project proposes to simplify the model deployment and monitoring workflow for the open-source [XGBoost](https://xgboost.readthedocs.io/en/stable/) library. Key features entail:

1. Realtime monitoring of model metrics
    
    Critical metrics of a model should be continuously presented to users via the terminal or browser. 

2. Model configuration

    The parameters of the model should be able to configured via the terminal in an elegant way. 

3. Model project instantiation

    Workflows are abstracted into individual project instances which contain specified configurations and metadata. 


## Motivations


## Instructions to Download

Prerequisites:

- install [uv](https://pypi.org/project/uv/)
- python [3.12.10] must be installed (https://www.python.org/downloads/release/python-31210/)

1. Clone this repo
```bash
% git clone https://github.com/jahleeljackson/xgb-ork.git
```

2. Navigate to project
```bash
% cd xgb-ork
``` 

3. Sync libraries with uv
```bash
% uv sync 
```

4. Activate the virtual environment
```bash
% source .venv/bin/activate
```

5. Install xgb
```bash
% pip install -e .
``` 






## Instructions to Run

Feel free to watch this [video]() of me giving a project demo. Otherwise follow the steps below:

1. Initialize a new project using the init command.
```bash
% xgb init foo c # initialized a classification (c) project named foo 
```

2. See existing projects.
```bash
% xgb list 
```

3. Add a dataset to the data store.
```bash
# test dataset provided 
% xgb add {pwd}/src/testing/test_data.csv foo # xgb add {source_file_path} {name of data in datastore}
```

**Curl Test Command**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
        "data": [
            {
                "Id": 1,
                "SepalLengthCm": 5.1,
                "SepalWidthCm": 3.5,
                "PetalLengthCm": 1.4,
                "PetalWidthCm": 0.2
            }
        ]
      }'
```



## Documentation

**XGB**

```bash
(xgb-ork) bash xgb-ork % xgb --help
Usage: xgb [OPTIONS] COMMAND [ARGS]...

  xgb is a supervised ML workflow orchestrator for xgboost models.

  xgb simplifies the development, tracking, monitoring, and deployment.

Options:
  --help  Show this message and exit.

Commands:
  add     Add dataset to datastore.
  config  Configure the model parameters for a project.
  data    Display available datasets.
  delete  Delete a project.
  expand  Display the contents of a particular dataset.
  init    Initialize a project.
  list    List existing projects.
  remove  Remove a dataset from the datastore.
  run     Run an inference server for the specified project and model.
  show    Display metadata of a project.
  train   Train XGB model with dataset.
```

### Commands 


```bash
(xgb-ork) bash xgb-ork % xgb add --help
Usage: xgb add [OPTIONS] DATA_PATH DATASET

  Add dataset to datastore.

Options:
  --help  Show this message and exit.
```


```bash
(xgb-ork) bash xgb-ork % xgb config --help
Usage: xgb config [OPTIONS] PROJECT_NAME

  Configure the model parameters for a project.

Options:
  --help  Show this message and exit.
```


```bash
(xgb-ork) bash xgb-ork % xgb data --help  
Usage: xgb data [OPTIONS]

  Display available datasets.

Options:
  --help  Show this message and exit.
```

```bash
(xgb-ork) bash xgb-ork % xgb delete --help
Usage: xgb delete [OPTIONS] PROJECT_NAME

  Delete a project.

Options:
  --help  Show this message and exit.
```


```bash
(xgb-ork) bash xgb-ork % xgb expand --help
Usage: xgb expand [OPTIONS] DATASET

  Display the contents of a particular dataset.

Options:
  --help  Show this message and exit.
```

```bash
(xgb-ork) bash xgb-ork % xgb init --help  
Usage: xgb init [OPTIONS] PROJECT_NAME {r|c}

  Initialize a project.

Options:
  --help  Show this message and exit.
```

```bash
(xgb-ork) bash xgb-ork % xgb list --help
Usage: xgb list [OPTIONS]

  List existing projects.

Options:
  --help  Show this message and exit.
```

```bash
(xgb-ork) bash xgb-ork % xgb remove --help
Usage: xgb remove [OPTIONS] DATASET

  Remove a dataset from the datastore.

Options:
  --help  Show this message and exit.
```

```bash
(xgb-ork) bash xgb-ork % xgb run --help   
Usage: xgb run [OPTIONS] PROJECT_NAME MODEL_NAME

  Run an inference server for the specified project and model.

Options:
  --help  Show this message and exit.
```

```bash
(xgb-ork) bash xgb-ork % xgb show --help
Usage: xgb show [OPTIONS] PROJECT_NAME

  Display metadata of a project.

Options:
  --help  Show this message and exit.
```

```bash
(xgb-ork) bash xgb-ork % xgb train --help
Usage: xgb train [OPTIONS] PROJECT_NAME DATASET

  Train XGB model with dataset.

Options:
  --help  Show this message and exit.
```