class NotEnoughArgs(Exception):
    def __init__(self, command_name: str, owner_id: int):
        self.command_name = command_name
        super().__init__(f'Not enough arguments for «{command_name}» command [{owner_id}]')
