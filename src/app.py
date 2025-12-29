import click

from util.DataStore import DataStore 
from util.Project import Project
from util.ProjectStore import ProjectStore
from util.types import PredictionType

regression = PredictionType.R 
classification = PredictionType.C

datastore = DataStore()
projectstore = ProjectStore()


@click.group()
def cli():
    '''xgb is a supervised ML workflow orchestrator for xgboost models.\n
    xgb simplifies the development, tracking, monitoring, and deployment.'''
    pass

@cli.command()
@click.argument("project_name")
@click.argument("prediction_type", type=click.Choice(["r", "c"]))
def init(project_name: str, prediction_type: str):
    '''Initialize a project.'''

    if prediction_type == "r":
        ptype = PredictionType.R
    else:
        ptype = PredictionType.C

    projectstore.add(name=project_name, ptype=ptype)


@cli.command()
def list():
    '''List existing projects.'''
    projectstore.display()


@cli.command()
@click.argument("project_name")
def delete(project_name: str):
    '''Delete a project'''
    projectstore.delete(name=project_name)


@cli.command()
@click.argument("data_path")
@click.argument("dataset")
def add(data_path: str, dataset: str):
    '''Add dataset to datastore.'''
    datastore.add(source_file=data_path, file_name=dataset)


@cli.command()
def data():
    '''Display available datasets.'''
    datastore.show()



@cli.command()
@click.argument("dataset")
def remove(dataset: str):
    '''Remove a dataset from the datastore.'''
    datastore.delete(file_name=dataset)


@cli.command()
@click.argument("project_name")
@click.argument("dataset")
def train(project_name: str, dataset: str):
    '''Train XGB model with dataset.'''
    if projectstore.project_exists(name=project_name) and datastore.file_exists(file_name=dataset):
        project = Project(name=project_name)
        project.train_xgb(data_file=dataset)
    else:
        raise click.UsageError(f"{project_name} and/or {dataset} do not exist.")


@cli.command()
@click.argument("project_name")
def config(project_name: str):
    '''Configure the model parameters for a project.'''
    
    if projectstore.project_exists(name=project_name):
        project = Project(name=project_name)
        project.config_model()
    else:
        raise click.UsageError(f"{project_name} does not exist.")



@cli.command()
@click.argument("project_name")
def show(project_name: str):
    '''Display metadata of a project.'''

    if projectstore.project_exists(name=project_name):
        project = Project(name=project_name)
        project.show()
    else:
        raise click.UsageError(f"{project_name} does not exist.")


if __name__=="__main__":
    cli()