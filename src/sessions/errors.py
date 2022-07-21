class UndefinedSessionError(Exception):
    def __init__(self, token: str):
        message = f'Session with access token {token} is undefined'
        super().__init__(message)
