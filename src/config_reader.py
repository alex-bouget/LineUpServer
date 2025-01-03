from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os
import json
import inspect
from runpy import run_path
from lineup_lang.language_object import LanguageInterface, \
    LanguageExecutorInterface, LanguageObjectInterface


class Module(BaseModel):
    name: str
    type: str
    file: str
    object: Any = None


class User(BaseModel):
    name: str
    password: str


class Config(BaseModel):
    chdir: str = "."
    folder: str = "scripts"
    folder_modules: str = "modules"
    modules: List[str] = []
    core: List[str] = []
    executor: str = ""
    default_args: dict = {}
    default_vars: dict = {}
    users: List[Dict[str, str]] = []
    modules_set: List[Module] = []
    users_set: List[User] = []


class ConfigBuilder:
    config: Config

    def __init__(self, config: str | None) -> None:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        json_config = self.load_json(config)
        if not json_config:
            print("Config not found")
            self.config = Config()
            return
        self.config = Config(**json_config)
        self.create_folders()
        self.generate_modules()
        self.config.users_set = [User(**user) for user in self.config.users]

    def load_json(self, config: str | None) -> dict | bool:
        if not config:
            return False
        if not os.path.isfile(config):
            return False
        with open(config, "r") as f:
            return json.loads(f.read())
        return False

    def create_folders(self) -> None:
        if self.config.chdir != ".":
            if not os.path.isdir(self.config.chdir):
                os.makedirs(self.config.chdir)
            os.chdir(self.config.chdir)
        if not os.path.isdir(self.config.folder):
            os.makedirs(self.config.folder)
        if not os.path.isdir(self.config.folder_modules):
            os.makedirs(self.config.folder_modules)

    def generate_modules(self) -> None:
        for module in self.config.modules:
            if os.path.isabs(module):
                name, type, file, object = self.generate_module_abs(module)
            else:
                name, type, file, object = self.generate_module_rel(module)
            self.config.modules_set.append(Module(
                name=name,
                type=type,
                file=file,
                object=object
            ))

    def generate_module_abs(self, module: str) -> tuple[str, str, str, any]:
        if not os.path.isfile(module):
            return module, "", "", None
        name = os.path.basename(module)
        name = os.path.splitext(name)[0]
        if name == "lup_module":
            name = os.path.basename(os.path.dirname(module))
        file = module
        sys.path.append(os.path.dirname(file))
        result = run_path(module, {"__server_config__": self.config})
        obj = result["__lineup__"]
        type = self.get_module_type(obj)
        return name, type, file, obj

    def generate_module_rel(self, module: str) -> tuple[str, str, str, any]:
        name = module
        file = os.path.join(self.config.folder_modules, module)
        if os.path.isdir(file):
            file = os.path.join(file, "lup_module.py")
        else:
            name = os.path.basename(module)
            name = os.path.splitext(name)[0]
        if not os.path.isfile(file):
            return name, "", "", None
        sys.path.append(os.path.dirname(file))
        result = run_path(file, {"__server_config__": self.config})
        obj = result["__lineup__"]
        type = self.get_module_type(obj)
        return name, type, file, obj

    def get_module_type(self, obj: any) -> str:
        if not inspect.isclass(obj):
            obj = obj.__class__
        if issubclass(obj, LanguageObjectInterface):
            return "core"
        if issubclass(obj, LanguageExecutorInterface):
            return "executor"
        if issubclass(obj, LanguageInterface):
            return "language"
        return ""

    def get_config(self) -> Config:
        return self.config
