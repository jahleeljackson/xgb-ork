import click

from util.DataStore import DataStore 
from util.Project import Project
from util.ProjectStore import ProjectStore
from util.types import Status, PredictionType, ModelRun

regression = PredictionType.R 
classification = PredictionType.C

datastore = DataStore()
projectstore = ProjectStore() 


projectstore.add("foo", ptype=PredictionType.C)
foo = Project(name="foo", ptype=PredictionType.C)
foo.show()