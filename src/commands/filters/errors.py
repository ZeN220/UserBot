class ParseUserError(Exception):
    def __init__(self, owner_id: int):
        self.owner_id = owner_id
        super().__init__(f'Not found user [{owner_id}]')
