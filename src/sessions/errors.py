class InvalidSessionError(Exception):
    """
    Данная ошибка вызывается при невалидном токене
    """
    def __init__(self, token: str):
        self.message = f'Access token «{token}» of session is invalid'
        super().__init__(self.message)
