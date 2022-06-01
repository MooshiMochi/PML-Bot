import os


class Constants:
    def __init__(self):
        self.exts = (
            "cogs.mc_madness",
            "cogs.messages_lb",
            "cogs.private_chat",
            "cogs.riddles",
            "events.error_handler"
        )

        self.DEBUG = True
        if os.getlogin() == "Administrator":
            self.DEBUG = False


const = Constants()
