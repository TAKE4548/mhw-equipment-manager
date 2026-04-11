class LogicValidationError(Exception):
    """Exception raised for validation errors in the logic layer."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
