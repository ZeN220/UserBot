from typing import List, Dict, Union
from datetime import datetime
import asyncio
import time

from vkwave.api.methods._error import APIError
from vkwave.bots import (
    EventTypeFilter,
    FromGroupFilter,
    RegexFilter,
    PeerIdFilter,
    TextFilter,
    SimpleUserEvent,
    PhotoUploader,
    FromMeFilter,
    StickerFilter
)
from vkwave.client import AIOHTTPClient
from vkwave.api import API
import toml

from utils import config, get_user_id, send_message_to_me
from dispatching import Router
from database import Message


logger = Router(
    'logger',
    'Роутер для логирования входящих сообщений, '
    'а также для уведомлений о удалении и редактировании сообщений'
)

api = API(clients=AIOHTTPClient(), tokens=config['VK']['user_token'])
uploader = PhotoUploader(api.get_context())

blacklist_chats = config["blacklist_chats"]
del_notify = config['logger']['delete_notification']
edit_notify = config['logger']['edit_notification']


@logger.message_handler(
    TextFilter('чсчат-'),
    FromMeFilter(True)
)
async def remove_chat_to_blacklist(event: SimpleUserEvent):
    chat = int(event.peer_id)
    name = (
        await event.api_ctx.messages.get_chat_preview(peer_id=chat)
    ).response.preview.title
    message = (
        f'Чат {name} успешно удален из черного списка ' 
        'и продолжит логироваться.'
    )
    blacklist_chats.remove(chat)

    toml.dump(config, open('config.toml', 'w', encoding='utf-8'))
    await send_message_to_me(
        message=message,
    )


@logger.message_handler(
    TextFilter('чсчат+'),
    FromMeFilter(True)
)
async def add_chat_to_blacklist(event: SimpleUserEvent):
    chat = int(event.peer_id)
    name = (
        await event.api_ctx.messages.get_chat_preview(peer_id=chat)
    ).response.preview.title
    blacklist_chats.append(chat)
    message = (
        f'Чат {name} успешно внесен в черный список ' 
        'и больше не будет логироваться.'
    )

    toml.dump(config, open('config.toml', 'w', encoding='utf-8'))
    await send_message_to_me(
        message=message,
    )


@logger.message_handler(
    TextFilter('чсчаты'),
    FromMeFilter(True)
)
async def chats_blacklist(event: SimpleUserEvent):
    answer = 'Список чатов, в которых отключено логирование:\n'
    for chat in blacklist_chats:
        try:
            name = (await event.api_ctx.messages.get_chat_preview(
                peer_id=chat
            )).response.preview.title
            answer += f'{name} [{chat}]\n'

        except APIError:
            await send_message_to_me(
                message=f'Доступ к чату [{chat}] потерян. '
                        f'Он будет удален из черного списка.',
            )
            blacklist_chats.remove(chat)

    await send_message_to_me(
        message=answer,
    )
    toml.dump(config, open('config.toml', 'w', encoding='utf-8'))


@logger.message_handler(
    RegexFilter(r'(удаленные|редактированные) (.+) (\d+)'),
    FromMeFilter(True)
)
async def get_delete(event: SimpleUserEvent):
    delete_or_edit = event.text.split()[0]
    count = event.text.split()[2]
    user_name: List[str] = []
    user_id = await get_user_id(event)

    user_data = (await event.api_ctx.users.get(user_ids=user_id, name_case='gen')).response[0]
    user_name.extend((user_data.first_name, user_data.last_name))

    if delete_or_edit == 'удаленные':
        answer = '[❌] Удаленные сообщения от [id{user_id}|{user_data}]:\n\n'
        notes = await Message.filter(
            user_id=user_id,
            is_delete=True
        ).order_by('-id').limit(int(count)).values('text', 'attachments', 'timestamp', 'peer_id')
    else:
        answer = '[✏] Отредактированные сообщения от [id{user_id}|{user_data}]:\n\n'
        notes = await Message.filter(
            user_id=user_id,
            is_edit=True
        ).order_by('-id').limit(int(count)).values('text', 'attachments', 'timestamp', 'peer_id', 'edit_history')

    answer = answer.format(user_id=user_id, user_data=' '.join(user_name))

    for note in notes:
        text = note['text']
        attachments = note['attachments']
        edit_history = note.get('edit_history')
        peer_id = note['peer_id']

        if peer_id and (text or attachments):
            title_chat = (await event.api_ctx.messages.get_chat_preview(peer_id=peer_id)).response.preview.title
            answer += f'[📨] Чат: {title_chat}'
        if text:
            answer += f'\n[💬] Сообщение: {text}\n[⏰] Дата: {note["timestamp"]}'
        if attachments:
            answer += f'\n[📸] Вложения: {attachments}'
        if edit_history:
            answer += f'\n[🗒] История редактирования: {edit_history}'

        answer += '\n\n'

    await send_message_to_me(
        message=answer
    )


@logger.handler(
    EventTypeFilter((2, 5)),
    ~PeerIdFilter(blacklist_chats)
)
async def delete_message(event: SimpleUserEvent):
    time.sleep(1)
    message_id = event.object.object.message_id
    peer_id = event.object.object.peer_id
    find_message: Dict[str, Union[int, str, None]] = await Message.get_or_none(  # type: ignore
        message_id=message_id
    ).values('text', 'attachments', 'user_id')
    if find_message:
        attachments_from_delete_message: str = find_message['attachments']
        user_id = find_message['user_id']
        text = find_message['text']
        user_data = (await event.api_ctx.users.get(
            user_ids=find_message["user_id"]
        )).response[0]

        from_what = 'из личного диалога'
        delete_or_edit = []
        attachments: List[str] = []

        if attachments_from_delete_message:
            attachments = [
                attachment
                for attachment in attachments_from_delete_message.split('\n')
            ]

        if event.object.object.event_id == 5:
            edit_history = (
                await Message.get(message_id=message_id).values('edit_history')
            )['edit_history']
                # type: ignore
            if edit_history:
                edit_history += f' -> {event.text}'
            else:
                edit_history = f'{text} -> {event.text}'

            await Message.filter(message_id=message_id).update(is_edit=True, edit_history=edit_history)
            if edit_notify:
                delete_or_edit = ['✏', 'отредактировал']
                text = edit_history

        if event.object.object.event_id == 2:
            await Message.filter(message_id=message_id).update(is_delete=True)
            if del_notify:
                delete_or_edit = ['❌', 'удалил']

        if peer_id >= 2e9:
            chat = (
                await event.api_ctx.messages.get_chat_preview(peer_id=peer_id)
            ).response.preview.title
            from_what = f'из чата «{chat}»'

        if delete_or_edit:
            await send_message_to_me(
                message=f'[{delete_or_edit[0]}] [id{user_id}|'
                        f'{user_data.first_name} {user_data.last_name}] '
                        f'{delete_or_edit[1]} сообщение {from_what}:\n{text}',
                attachment=await uploader.get_attachments_from_links(
                    peer_id=565694749,
                    links=attachments
                )
            )
        delete_or_edit.clear()


@logger.handler(
    EventTypeFilter(4),
    FromGroupFilter(),
    ~PeerIdFilter(blacklist_chats),
    FromMeFilter(False),
    StickerFilter(False)
)
async def logging(event: SimpleUserEvent):
    attachments: List[str] = []
    text = event.text
    user_id = event.peer_id
    message_id = event.object.object.message_id
    timestamp = event.object.object.timestamp
    if user_id > 2e9:
        user_id = event.object.object.message_data.from_id

    extra_message_data = event.object.object.extra_message_data
    has_attach = 'attach1_type' in extra_message_data
    has_photo = extra_message_data.get("attach1_type") == 'photo'
    if has_attach and has_photo:
        pictures = (await event.api_ctx.messages.get_by_id(
            message_ids=message_id
        )).response.items[0].attachments
        for pic in pictures:
            if pic.photo:
                '''
                Поскольку вк возвращает ссылку на фотографию в нескольких
                разрешениях, нужно сортировать список с ссылками
                '''
                sizes = pic.photo.sizes
                pic = max(sizes, key=lambda photo_sizes: photo_sizes.height)
                attachments.append(pic.url)

    if text or attachments:
        await Message.create(
            message_id=message_id,
            user_id=user_id,
            attachments='\n'.join(attachments),
            text=text,
            timestamp=datetime.fromtimestamp(timestamp).strftime('%d.%m.%y %H:%M'),
            peer_id=event.peer_id if event.peer_id >= 2e9 else None,
            is_delete=False,
            is_edit=False,
            edit_history=''
        )
        await asyncio.sleep(86400)
        await Message.filter(message_id=message_id).delete()
