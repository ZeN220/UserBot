from typing import Optional, List

from vkwave.api import APIOptionsRequestContext
from vkwave.bots.utils.uploaders import DocUploader, VoiceUploader, PhotoUploader
from vkwave.types.objects import MessagesMessageAttachment

from src.services import HolderGateway
from src.sessions import Session
from .base import command_manager, CommandResponse, BaseHandler, Priority
from .filters import ParseDataFromReply, ParseDataFromFwd


@command_manager.register(
    ParseDataFromReply() | ParseDataFromFwd(), name='add_template', module='templates',
    aliases=['addtemplate', 'template+', 'добавитьшаблон', 'шаблон+'], priority=Priority.MEDIUM,
    args_syntax=r'(?P<trigger>\w+)'
)
class AddTemplateHandler(BaseHandler):
    async def execute(
        self,
        gateway: HolderGateway,
        session: Session,
        trigger: str,
        text: str,
        attachments: Optional[List[MessagesMessageAttachment]] = None,
    ) -> 'CommandResponse':
        owner_id = session.owner_id
        if len(trigger) > 64:
            return CommandResponse(
                response='[⚠] Длина названия шаблона не должна превышать 64 символа.'
            )

        exists_template = await gateway.template.exists(trigger, owner_id)
        if exists_template:
            return CommandResponse(
                response=f'[⚠] Шаблон с названием «{trigger}» уже существует.'
            )

        if attachments is not None:
            attachments = await upload_attachments(
                attachments, session.user.api_context, owner_id
            )
        await gateway.template.create(
            trigger=trigger, owner_id=owner_id, answer=text, attachments=attachments
        )
        return CommandResponse(
            response=f'[📖] Шаблон с названием «{trigger}» успешно добавлен.'
        )


async def upload_attachments(
    attachments: List[MessagesMessageAttachment],
    api_context: APIOptionsRequestContext,
    peer_id: int
) -> List[str]:
    result = []
    for attachment in attachments:
        attachment = await upload_attachment(attachment, api_context, peer_id)
        result.append(attachment)
    return result


async def upload_attachment(
    attachment: MessagesMessageAttachment,
    api_context: APIOptionsRequestContext,
    peer_id: int
) -> str:
    audio_message = attachment.audio_message
    document = attachment.doc
    photo = attachment.photo
    """
    Из-за того, что в сообщении может быть несколько вложений разных видов, 
    на каждое вложение нужно создавать свой объект загрузчика
    """
    if audio_message is not None:
        url = audio_message.link_ogg
        uploader = VoiceUploader(api_context)
    elif document is not None:
        url = document.url
        uploader = DocUploader(api_context)
    elif photo is not None:
        url = photo.sizes[-1].url
        uploader = PhotoUploader(api_context)
    else:
        raise TypeError('This attachment type is not supported')

    attachment = await uploader.get_attachment_from_link(
        peer_id=peer_id, link=url
    )
    return attachment
