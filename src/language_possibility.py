from config_reader import Config
from lineup_lang.language_object import LanguageExecutorInterface, LanguageObjectInterface
from lineup_lang import lucore, luexec


class LanguagePossibility:
    config: Config
    _executors: dict[str, LanguageExecutorInterface]
    _core_object: dict[str, LanguageObjectInterface]
    _language_object: dict[str, LanguageObjectInterface]

    def __init__(self, config: Config):
        self.config = config
        self._executors = {
            "default": luexec.DefaultExecutor,
            "jumper": luexec.JumperExecutor,
        }
        self._core_object = {
            "condition": lucore.ConditionsJumpObject(),
        }
        self._language_object = {}
        self.append_with_config()
        self._core_object["variable"] = lucore.VariableObject({
            **self.config.default_vars,
            **self._language_object,
        })

    def append_with_config(self):
        for module in self.config.modules_set:
            if module.type == "executor":
                self._executors[module.name] = module.object
            elif module.type == "core":
                self._core_object[module.name] = module.object
            elif module.type == "language":
                self._language_object[module.name] = module.object

    def get_executors(self):
        return self._executors

    def get_core_object(self):
        return self._core_object

    def get_language_object(self):
        return self._language_object

    def get_executor(self, name: str):
        return self._executors.get(name, self._executors["default"])

    def get_core(self, name: list[str]):
        result = []
        for core in name:
            result.append(self._core_object.get(core, None))
        return result
