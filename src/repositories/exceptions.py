class DBIntegrityError(Exception):
    def __init__(self, model_name: str):
        super().__init__(f"Integrity error on creating {model_name}(s).")
