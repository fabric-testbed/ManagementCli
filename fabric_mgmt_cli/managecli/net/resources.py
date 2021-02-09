import yaml

class Inventory:
    def __init__(self, yfile):
        self.nodes = dict()
        self.paths = dict()
        with open(yfile, "r") as inv:
            try:
                data = yaml.safe_load(inv)
                for k,v in data.items():
                    if isinstance(v, dict):
                        if (k == "paths"):
                            self.paths.update(v)
                        if (k == "nodes"):
                            self.nodes.update(v)
            except Exception as e:
                raise Exception(f"Could not load configuration file: {ifile}: {e}")
            inv.close()

    def resolve_resource(self, rname):
        if rname not in self.nodes:
            raise Exception(f"Node not found: {rname}")
        ret = self.nodes.get(rname)
        path = ret.get("path", None)
        if not path:
            ret["ero"] = None
        else:
            if path not in self.paths:
                raise Exception(f"Path not found: {rname} -> {path}")
            ret["ero"] = self.paths.get(path)
        return ret

