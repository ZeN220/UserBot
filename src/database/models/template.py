from typing import List, Optional, Tuple

from tortoise import Model, fields

from .attachment import Attachment


class Template(Model):
    id = fields.IntField(pk=True)
    trigger = fields.CharField(max_length=64, unique=True)
    answer = fields.TextField()
    owner_id = fields.IntField()

    @classmethod
    async def get_template(cls, trigger: str, owner_id: int) -> Optional[Tuple[str, List[str]]]:
        template = await cls.get_or_none(trigger=trigger, owner_id=owner_id)
        if not template:
            return

        attachments = await Attachment.get_documents_list(template_id=template.id)
        return template.answer, attachments

    class Meta:
        table = 'templates'
