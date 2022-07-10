from tortoise import Model, fields


class SessionModel(Model):
    user_token = fields.TextField()
    bot_token = fields.TextField()
    commands_prefix = fields.CharField(max_length=16)

    class Meta:
        table = 'sessions'
