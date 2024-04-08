import logging


class Foo:
    name = "korngjrg"

    age = 3

    def __repr__(self):
        return self.name + " " + str(self.age)


logging.debug("%s", Foo())
