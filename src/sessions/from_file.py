import toml
from typing import List


class SessionsFile:
    def __init__(self, file: str):
        self.file = file

    def get_sessions(self) -> List[dict]:
        sessions = toml.load(self.file)['sessions']
        # При отсутствии сессий в sessions будет лежать [{}], из за этого нужно проверять длину списка и возвращать пустой список
        if len(sessions) == 1 and not sessions[0]:
            return []
        return sessions
