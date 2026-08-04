"""
json_storage.py

Json Storage class to write and load events.

"""
#Standard modules
from pathlib import Path
import json


class JsonStorage():

    def load(self,json_path:str|Path):
        if not json_path.exists():
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

            if not content:
                return []

        return json.loads(content)

    def save(self,json_path:str|Path,raw_data:str|list|dict,overwrite:bool=False):
        if overwrite:
            current_data = list(raw_data) if isinstance(raw_data, list) else raw_data
        else:
            try:
                current_data = self.load(json_path) or []
            except:
                current_data = []

            current_data.extend(raw_data)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False, indent=4)