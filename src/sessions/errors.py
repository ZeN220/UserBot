class UndefinedSessionError(Exception):
    def __init__(self, token: str):
        # В сообщении показываются только первые 30 символов в целях безопасности.
        self.message = f'Session with access token «{token[:30]}» is undefined'
        super().__init__(self.message)


class InvalidSessionError(Exception):
    """
    Данная ошибка вызывается при невалидном токене
    """
    def __init__(self, token: str):
        self.message = f'Access token «{token}» of session is invalid'
        super().__init__(self.message)
