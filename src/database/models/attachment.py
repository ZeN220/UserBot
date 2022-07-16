from typing import Optional, List

from tortoise import Model, fields


class Attachment(Model):
    template_id = fields.IntField()
    owner_id = fields.IntField()
    trigger = fields.CharField(max_length=64, unique=True)
    document = fields.TextField()

    @classmethod
    async def get_documents_list(cls, template_id: int) -> Optional[List[str]]:
        attachments = await cls.filter(template_id=template_id)
        if not attachments:
            return

        result = []
        for attachment in attachments:
            result.append(attachment.document)
        return result

    class Meta:
        table = 'attachments'
