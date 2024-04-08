import logging


class Logger:
    code = None

    @staticmethod
    def init(code):
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s", filename="py_log.txt",
                            filemode="w")
        Logger.code = code

    @staticmethod
    def skip_information(tick):
        if Logger.code == "hello_machine.txt" and tick == 119:
            logging.info("\n\t...Transfer the symbols 'e','l','l','o',' ','w','o','r','l','d','!'...\n")
        elif Logger.code == "cat_machine.txt" and tick == 122:
            logging.info("\n\t...Transfer the left symbols...\n")
        elif Logger.code == "hello_user_name_machine.txt" and tick == 163:
            logging.info("\n\t...Transfer the left symbols...\n")
        elif Logger.code == "prob2_machine.txt" and tick == 118:
            logging.info("\n\t...Continue calculating...\n")

    @staticmethod
    def can_log(tick):
        codes = {
            "hello_machine.txt": tick <= 118 or 1316 <= tick,
            "cat_machine.txt": tick <= 121 or 1019 <= tick,
            "hello_user_name_machine.txt": tick <= 163 or 2384 <= tick,
            "prob2_machine.txt": tick <= 118 or 736 <= tick
        }
        if Logger.code in codes:
            Logger.skip_information(tick)
        return codes[Logger.code] if Logger.code in codes else True

    @staticmethod
    def info(msg, tick):
        if Logger.can_log(tick):
            logging.info(msg)

    @staticmethod
    def debug(dp, tick):
        if Logger.can_log(tick):
            logging.debug(dp)
