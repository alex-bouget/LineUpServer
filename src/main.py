import os
from typing import Dict, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from config_reader import ConfigBuilder, Config
from language import ServerLanguage
from lineup_lang.error import LineupError, UnexpectedError

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
    return ServerLanguage(config, no_error=False)


def process_error(e: LineupError):
    if isinstance(e, UnexpectedError):
        return HTTPException(status_code=500, detail=str(e))
    return HTTPException(status_code=400, detail=str(e))


app = FastAPI()


@app.post("/execute_default/{code}")
def execute_default(code: str, args: Dict[str, str]):
    if not os.path.isfile(os.path.join(config.folder, code)):
        return HTTPException(status_code=404, detail="File not found")
    try:
        language = create_language()
        return language.execute_file(os.path.join(config.folder, code), **args)
    except LineupError as e:
        return process_error(e)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
def execute(args: ExecuteObject):
    language = create_language()
    try:
        return language.execute_script_with_args(args.code, **args.args)
    except LineupError as e:
        return process_error(e)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


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
