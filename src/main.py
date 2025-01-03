import os
from typing import Dict, List
from pydantic import BaseModel
from fastapi import FastAPI
from config_reader import ConfigBuilder, Config
from language import ServerLanguage

config_builder = ConfigBuilder("../config.json")
config = config_builder.get_config()
language = ServerLanguage(config)


class ExecuteObject(BaseModel):
    code: str
    args: Dict[str, str]


class CompleteObject(BaseModel):
    executors: List[str]
    core: List[str]
    language: List[str]


class Info(BaseModel):
    config: Config
    complete: CompleteObject
    versions: Dict[str, str]


app = FastAPI()


@app.post("/execute_default/{code}")
def execute_default(code: str, args: Dict[str, str]):
    if not os.path.isfile(os.path.join(config.folder, code)):
        return {"error": "File not found"}
    return language.execute_script_with_args(code, **args)


@app.post("/execute")
def execute(args: ExecuteObject):
    return language.execute_script_with_args(args.code, **args.args)


@app.get("/info")
def info() -> Info:
    config_clone = config.model_copy()
    for key in config_clone.modules_set:
        if key.object:
            key.object = "Object"
    for key in config_clone.users_set:
        key.password = "********"
    return Info(
        config=config,
        complete=CompleteObject(
            executors=list(language.possiblity.get_executors().keys()),
            core=list(language.possiblity.get_core_object().keys()),
            language=list(language.possiblity.get_language_object().keys()),
        ),
        versions=language.get_versions(),
    )
