import os
import inspect
import pkgutil
import logging

from lib.cuckoo.common.constants import CUCKOO_ROOT
from lib.cuckoo.common.config import Config
from lib.cuckoo.common.abstracts import Report
from lib.cuckoo.common.exceptions import CuckooReportError
import modules.reporting as plugins

log = logging.getLogger(__name__)

class Reporter:
    def __init__(self, analysis_path, custom=""):
        self.analysis_path = analysis_path
        self.custom = custom
        self.cfg = Config(cfg=os.path.join(CUCKOO_ROOT, "conf/reporting.conf"))
        self.__populate(plugins)

    def __populate(self, modules):
        prefix = modules.__name__ + "."
        for loader, name, ispkg in pkgutil.iter_modules(modules.__path__):
            if ispkg:
                continue

            try:
                section = getattr(self.cfg, name)
            except AttributeError:
                continue

            if not section.enabled:
                continue

            path = "%s.%s" % (plugins.__name__, name)
            __import__(path, globals(), locals(), ["dummy"], -1)

    def run(self, results):
        Report()

        for plugin in Report.__subclasses__():
            current = plugin()
            current.set_path(self.analysis_path)
            module = inspect.getmodule(current)
            module_name = module.__name__.rsplit(".", 1)[1]
            current.set_options(self.cfg.get(module_name))

            try:
                current.run(results)
            except NotImplementedError:
                continue
            except CuckooReportError as e:
                log.error(e.message)
