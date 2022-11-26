from configparser import ConfigParser, ParsingError
from pathlib import Path

__all__ = ["config"]


class Config:
    def __init__(self, filename: str = "bot.cfg"):
        cfg = self.get_cfg_file(filename)

        self.top = cfg["window"].getint("top")
        self.left = cfg["window"].getint("left")
        self.width = cfg["window"].getint("width")
        self.height = cfg["window"].getint("height")

        self.player_name = cfg["player"].get("name")

        self.attack = cfg["skills"].getint("attack")
        self.pick_up = cfg["skills"].getint("pick_up")
        self.next_target = cfg["skills"].getint("next_target")
        self.sit = cfg["skills"].getint("sit")

    def get_cfg_file(self, filename: str) -> ConfigParser:
        path = Path(filename)

        if path.is_file():
            cfg = ConfigParser(allow_no_value=True)
            cfg.read(filename)
            return cfg

        else:
            self.make_cfg_file(filename)
            raise ParsingError("Создан файл настроек, необходимо заполнить")

    @staticmethod
    def make_cfg_file(filename: str):
        cfg = ConfigParser()

        cfg.read_dict({
            "window": {
                "top": "0",
                "left": "0",
                "width": "1366",
                "height": "768",
            },

            "player": {
                "name": "milf",
            },

            "skills": {
                "attack": "1",
                "pick_up": "4",
                "next_target": "11",
                "sit": "12",
            }
        })

        with open(filename, 'w') as configfile:
            cfg.write(configfile)


config = Config('bot.cfg')
