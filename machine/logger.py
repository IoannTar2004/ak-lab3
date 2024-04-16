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
            "hello_machine.txt": tick == 159 or tick == 405,
            "cat_machine.txt": tick == 162 or tick == 410,
            "hello_user_name_machine.txt": tick == 188 or tick == 435,
            "prob2_machine.txt": tick == 118
        }
        if codes[self.code]:
            self.log.warning("\n... Continue! ...\n")

    def skip_spi_information(self, tick):
        codes = {
            "hello_machine.txt": tick == 824,
            "cat_machine.txt": tick == 824,
            "hello_user_name_machine.txt": tick == 878,
            "prob2_machine.txt": False
        }
        if codes[self.code]:
            self.log.warning("\n... Continue! ...\n")

    def can_log(self, tick):
        codes = {}
        if self.type == "processor":
            codes = {
                "hello_machine.txt": tick <= 159 or 396 <= tick <= 405 or tick >= 5205,
                "cat_machine.txt": tick <= 162 or 396 <= tick <= 410 or tick >= 4051,
                "hello_user_name_machine.txt": tick <= 188 or 424 <= tick <= 435 or tick >= 8353,
                "prob2_machine.txt": tick <= 118 or 736 <= tick
            }
        elif self.type == "spi":
            codes = {
                "hello_machine.txt": tick <= 824,
                "cat_machine.txt": tick <= 824,
                "hello_user_name_machine.txt": tick <= 878,
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
