import logging


class Logger:
    code = None

    log = None

    def __init__(self, log_file, name):
        self.code = name
        with open("machine/" + log_file, "w") as log:
            log.truncate(0)
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.DEBUG)
        handler = logging.FileHandler("machine/" + log_file, "w")
        formatter = logging.Formatter("%(levelname)s: %(message)s")

        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    def skip_information(self, tick):
        if self.code == "hello_machine.txt" and tick == 121:
            self.log.info("\n...Transfer the symbols 'e','l','l','o',' ','w','o','r','l','d','!'...\n")
        elif self.code == "cat_machine.txt" and tick == 124 or self.code == "hello_user_name_machine.txt" and tick == 165:
            self.log.info("\n...Transfer the left symbols...\n")
        elif self.code == "prob2_machine.txt" and tick == 118:
            self.log.info("\n...Continue calculating...\n")

    def can_log(self, tick):
        codes = {
            "hello_machine.txt": tick <= 120 or 1316 <= tick,
            "cat_machine.txt": tick <= 123 or 1019 <= tick,
            "hello_user_name_machine.txt": tick <= 165 or 2384 <= tick,
            "prob2_machine.txt": tick <= 118 or 736 <= tick
        }
        if self.code in codes:
            self.skip_information(tick)
        return codes[self.code] if self.code in codes else True

    def info(self, msg, tick=0):
        if self.can_log(tick):
            self.log.info(msg)

    def debug(self, object, tick=0):
        if self.can_log(tick):
            self.log.debug(object)

    def close(self):
        self.log.handlers.pop()
