from config_reader import Config
from language_possibility import LanguagePossibility
from lineup_lang import Language


class ServerLanguage(Language):
    config: Config
    possiblity: LanguagePossibility

    def __init__(self, config: Config, no_error: bool = True,
                 log_level: str = "WARN"):
        self.config = config
        self.possiblity = LanguagePossibility(config)
        executor = self.possiblity.get_executor(self.config.executor)
        core = self.possiblity.get_core(self.config.core)
        super().__init__(executor(core), no_error, log_level)
