import os
from typing import Dict, List
from pydantic import BaseModel
from fastapi import FastAPI
from config_reader import ConfigBuilder, Config
from language import ServerLanguage

if os.environ.get("LUP_SERVER_DOCKER"):
    config_builder = ConfigBuilder("/app/config.json")
else:
    config_builder = ConfigBuilder("../config.json")
config = config_builder.get_config()


class ExecuteObject(BaseModel):
    code: str
    args: Dict[str, str]


class CompleteObject(BaseModel):
    executors: List[str]
    core: List[str]
    language: List[str]


class Info(BaseModel):
    error: str = ""
    config: Config
    complete: CompleteObject
    versions: Dict[str, str]


def create_language() -> ServerLanguage:
    global config
    return ServerLanguage(config)


app = FastAPI()


@app.post("/execute_default/{code}")
def execute_default(code: str, args: Dict[str, str]):
    if not os.path.isfile(os.path.join(config.folder, code)):
        return {"error": "File not found"}
    language = create_language()
    result = language.execute_script_with_args(code, **args)
    language.close()
    return result


@app.post("/execute")
def execute(args: ExecuteObject):
    language = create_language()
    result = language.execute_script_with_args(args.code, **args.args)
    language.close()
    return result


@app.get("/info")
def info() -> Info:
    config_clone = config.model_copy(deep=True)
    for key in config_clone.modules_set:
        if key.object:
            key.object = "Object"
    for key in config_clone.users_set:
        key.password = "********"
    try:
        language = create_language()
    except Exception as e:
        return Info(
            error=f"Error occurred: {str(e)}",
            config=config_clone,
            complete=CompleteObject(
                executors=[],
                core=[],
                language=[],
            ),
            versions={},
        )
    result = Info(
        config=config_clone,
        complete=CompleteObject(
            executors=list(language.possiblity.get_executors().keys()),
            core=list(language.possiblity.get_core_object().keys()),
            language=list(language.possiblity.get_language_object().keys()),
        ),
        versions=language.get_versions(),
    )
    language.close()
    return result
