from tortoise.models import Model
from tortoise import fields


class Message(Model):
    message_id = fields.IntField()
    user_id = fields.IntField()
    text = fields.TextField()
    attachments = fields.TextField(null=True)
    timestamp = fields.TextField()
    peer_id = fields.IntField(null=True)
    is_delete = fields.BooleanField()
    is_edit = fields.BooleanField()
    edit_history = fields.TextField()
