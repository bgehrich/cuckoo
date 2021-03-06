import os

from lib.cuckoo.common.abstracts import Processing

class Debug(Processing):
    def run(self):
        self.key = "debug"
        debug = {}

        if os.path.exists(self.log_path):
            debug["log"] = open(self.log_path, "rb").read()
        else:
            debug["log"] = ""

        return debug
