import logging


class Logger:
    def __init__(self, name, type):
        self.code = name
        self.type = type

        with open(f"machine/logs/{type}.txt", "w") as log:
            log.truncate(0)

        self.log = logging.getLogger(type)
        self.log.setLevel(logging.DEBUG)
        handler = logging.FileHandler(f"machine/logs/{type}.txt", "w")
        formatter = logging.Formatter("%(levelname)s: %(message)s")

        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    def skip_processor_information(self, tick):
        codes = {
            "hello_machine.txt": tick == 153 or tick == 390,
            "cat_machine.txt": tick == 154 or tick == 394,
            "hello_user_name_machine.txt": tick in [182, 423, 8782],
            "prob2_machine.txt": tick == 118
        }
        if codes[self.code]:
            self.log.warning("\n... Continue! ...\n")

    def skip_spi_information(self, tick):
        codes = {
            "hello_machine.txt": tick == 782,
            "cat_machine.txt": tick == 792,
            "hello_user_name_machine.txt": tick == 823 or tick == 9445,
            "prob2_machine.txt": False
        }
        if codes[self.code]:
            self.log.warning("\n... Continue! ...\n")

    def can_log(self, tick):
        codes = {}
        if self.type == "processor":
            codes = {
                "hello_machine.txt": tick <= 153 or 380 <= tick <= 390 or tick >= 4986,
                "cat_machine.txt": tick <= 154 or 380 <= tick <= 394 or tick >= 3881,
                "hello_user_name_machine.txt": tick <= 182 or 409 <= tick <= 423
                                               or 8631 <= tick <= 8782 or tick >= 13787,
                "prob2_machine.txt": tick <= 118 or 736 <= tick
            }
        elif self.type == "spi":
            codes = {
                "hello_machine.txt": tick <= 782,
                "cat_machine.txt": tick <= 792,
                "hello_user_name_machine.txt": tick <= 823 or 9045 <= tick <= 9445,
                "prob2_machine.txt": False
            }
        return codes[self.code]

    def info(self, msg, tick=0):
        if self.can_log(tick):
            self.log.info(msg)

    def debug(self, object, tick=0):
        if self.can_log(tick):
            self.log.debug(object)
            self.skip_processor_information(tick)
            self.skip_spi_information(tick)

    def close(self):
        self.log.handlers.pop()
