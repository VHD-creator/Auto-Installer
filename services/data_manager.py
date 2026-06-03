import json

class DataManager:
    def __init__(self):
        self.category_file = "./core/config/categories.json"

    def load_categories(self):
        try:
            with open(
                self.category_file,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)
        except FileNotFoundError:
            return []
    def save_categories(self, categories):
        with open(
            self.category_file, "w",
            encoding="utf-8"
        ) as file: json.dump(
            categories,
            file,
            indent=4,
            ensure_ascii=False
        )