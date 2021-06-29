import sys

class col:
    HEADER = '\033[35m'# PINK
    DIR = '\033[34m' # BLUE
    ITEM = '\033[37m' # LGRAY
    PROMPT = '\033[32m' # GREEN
    WARNING = '\033[33m' # YELLOW
    FAIL = '\033[31m' # RED
    ENDC = '\033[39m' # BLACK

class CText():
    def _color(self, c, e):
        print (c + str(e) + col.ENDC)
    def warn(self, e):
        self._color(col.WARNING, e)
    def error(self, e):
        self._color(col.FAIL, e)
    def item(self, e):
        self._color(col.ITEM, e)
    def info(self, e):
        print (str(e))
