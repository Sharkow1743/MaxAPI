
## op codes
| code | action | description |
|---|---|---|
| 1 | [heartbeat](#heartbeat) | Send this so connection won`t close |
| 6 | [handshake](#handshake) | Initial connection handshake. Send this as first message |
| 19 | [authenticate](#authenticate) | User authentication. Send this as second message |
| 32 | [get contact details](#get_contact_details) | Retrieve contact information |
| 49 | [get history](#get_history) | Fetch chat history |
| 50 | [mark as read](#mark_as_read) | Mark messages as read |
| 64 | [send message](#send_message)| Send a new message |
| 75 | [subscribe to chat](#subscribe_to_chat) | Subscribe to chat updates |
| 83 | [get video](#get_video) | Returns link to video |
| 88 | [get file](#get_file) | Returns link to file |
___

### heartbeat
Send this every ~5-10 so connection won`t close
#### input
``` json
interactive: false
```

#### return
``` json
null
```
___

### handshake
Send this as first message
#### input
``` json
"userAgent":{
	"deviceType":"WEB"
}
```

#### return
``` json
null
```

___

### authenticate
Send this as second message
#### input
``` json
"interactive": true,
"token": "TOKEN",
"chatsSync": 0,
"contactsSync": 0,
"presenceSync": 0,
"draftsSync": 0,
"chatsCount": 40
```

#### return
``` json
"profile": {
      "profileOptions": [],
      "contact": {
        "accountStatus": 0,
        "baseUrl": "https://i.oneme.ru/i?r=BUGhUou04b028GIQiF8sPj1EMoEg2OSnHLBfb-SHaZ9Ay-Ag1jAVh2Bw-LDi7511o7RRkJxj_ZGNkDUfe8dvEb24",
        "names": [
          {
            "name": "TransferBot",
            "firstName": "TransferBot",
            "lastName": "",
            "type": "ONEME"
          }
        ],
        "phone": 79965433117,
        "options": [
          "TT",
          "ONEME"
        ],
        "photoId": 11549759,
        "updateTime": 1754132721403,
        "id": 13446207,
        "baseRawUrl": "https://i.oneme.ru/i?r=BTE2sh_eZW7g8kugOdIm2Not2iYTW6GNe8IqlUN66AbY8T_9cY73tz0ujRAFtR8MPmY"
      }
    },
    "drafts": {
      "chats": {
        "saved": {},
        "discarded": {}
      },
      "users": {
        "saved": {},
        "discarded": {}
      }
    },
    "token": "TOKEN",
    "videoChatHistory": false,
    "calls": [],
    "chats": [
      {
        "owner": 13446207,
        "participantsCount": 1,
        "access": "PRIVATE",
        "joinTime": 1754255179813,
        "created": 1754255179813,
        "lastMessage": {
          "sender": 13446207,
          "id": "114966868141288691",
          "time": 1754255190144,
          "text": "",
          "type": "USER",
          "cid": 1754255188210,
          "attaches": [
            {
              "_type": "FILE",
              "name": "CatWebCompiler-main.zip",
              "size": 8880,
              "fileId": 1255973,
              "token": "f9LHodD0cOKrnLaObGwzZprWg_5pbm9_yV7mH2fuvXofNjmgdHTbmW5V1bKQZqgaUtZDekwlfzcQBXgL3-oD"
            }
          ]
        },
        "type": "CHAT",
        "title": "a",
        "lastFireDelayedErrorTime": 0,
        "lastDelayedUpdateTime": 0,
        "options": {
          "SIGN_ADMIN": false,
          "OFFICIAL": false,
          "MESSAGE_COPY_NOT_ALLOWED": false,
          "ONLY_OWNER_CAN_CHANGE_ICON_TITLE": false,
          "ONLY_ADMIN_CAN_ADD_MEMBER": false,
          "ONLY_ADMIN_CAN_CALL": false,
          "SENT_BY_PHONE": false,
          "ALL_CAN_PIN_MESSAGE": true
        },
        "modified": 1754255179807,
        "lastEventTime": 1754255190144,
        "id": -68104154993983,
        "messagesCount": 1,
        "adminParticipants": {
          "13446207": {
            "permissions": 2047,
            "id": 13446207
          }
        },
        "admins": [
          13446207
        ],
        "status": "ACTIVE",
        "participants": {
          "13446207": 1754255190472
        },
        "cid": 1754255178469
      },
      {
        "owner": 13446207,
        "participantsCount": 1,
        "access": "PRIVATE",
        "joinTime": 1754132677185,
        "created": 1754132677185,
        "lastMessage": {
          "sender": 13446207,
          "id": "114966847810317555",
          "time": 1754254879918,
          "text": "",
          "type": "USER",
          "cid": 1754254877591,
          "attaches": [
            {
              "_type": "FILE",
              "name": "vd526.okcdn.ru__Archive [25-08-02 02-54-11](2).txt",
              "size": 709840,
              "fileId": 1220042,
              "token": "f9LHodD0cOKnhiKYFqYO_qifhuT2TN2Fbea-W1m97v-hsziIIZPosBXb523fTREtjq6hDx91IUb0e8m0yeef"
            }
          ]
        },
        "type": "CHAT",
        "title": "asd",
        "lastFireDelayedErrorTime": 0,
        "lastDelayedUpdateTime": 0,
        "options": {
          "SIGN_ADMIN": false,
          "OFFICIAL": false,
          "MESSAGE_COPY_NOT_ALLOWED": false,
          "ONLY_OWNER_CAN_CHANGE_ICON_TITLE": false,
          "ONLY_ADMIN_CAN_ADD_MEMBER": false,
          "ONLY_ADMIN_CAN_CALL": false,
          "SENT_BY_PHONE": false,
          "ALL_CAN_PIN_MESSAGE": true
        },
        "modified": 1754132677179,
        "lastEventTime": 1754254879918,
        "id": -68102894998847,
        "messagesCount": 9,
        "adminParticipants": {
          "13446207": {
            "permissions": 2047,
            "id": 13446207
          }
        },
        "admins": [
          13446207
        ],
        "status": "ACTIVE",
        "participants": {
          "13446207": 1754254880213
        },
        "cid": 1754132676634
      },
      {
        "owner": 13446207,
        "participantsCount": 1,
        "access": "PRIVATE",
        "invitedBy": 13446207,
        "joinTime": 1754132807635,
        "created": 1754132807635,
        "lastMessage": {
          "sender": 13446207,
          "id": "114958848557198579",
          "time": 1754132821002,
          "text": "",
          "type": "USER",
          "attaches": [
            {
              "duration": 0,
              "conversationId": "33ff7394-a3e0-48f1-8240-91b8eca88f5c",
              "hangupType": "HUNGUP",
              "_type": "CALL",
              "joinLink": "3OO_9q3OCvyg6hWMfTWgimYcC7APTV4TFPcprVZrELo",
              "callType": "AUDIO"
            }
          ]
        },
        "type": "CHAT",
        "title": "Групповой звонок 02 августа",
        "lastFireDelayedErrorTime": 0,
        "lastDelayedUpdateTime": 0,
        "videoConversation": {
          "previewParticipantIds": [],
          "conversationId": "33ff7394-a3e0-48f1-8240-91b8eca88f5c",
          "joinLink": "3OO_9q3OCvyg6hWMfTWgimYcC7APTV4TFPcprVZrELo"
        },
        "options": {
          "SIGN_ADMIN": false,
          "OFFICIAL": false,
          "MESSAGE_COPY_NOT_ALLOWED": false,
          "ONLY_OWNER_CAN_CHANGE_ICON_TITLE": false,
          "ONLY_ADMIN_CAN_ADD_MEMBER": false,
          "ONLY_ADMIN_CAN_CALL": false,
          "SENT_BY_PHONE": false,
          "ALL_CAN_PIN_MESSAGE": true
        },
        "modified": 1754132821021,
        "lastEventTime": 1754132821002,
        "id": -68102896244031,
        "messagesCount": 1,
        "adminParticipants": {
          "13446207": {
            "permissions": 2047,
            "id": 13446207
          }
        },
        "admins": [
          13446207
        ],
        "status": "HIDDEN",
        "participants": {
          "13446207": 1754132807647
        }
      },
      {
        "owner": 13446207,
        "participantsCount": 1,
        "access": "PRIVATE",
        "invitedBy": 13446207,
        "joinTime": 1754131823080,
        "created": 1754131823080,
        "lastMessage": {
          "sender": 13446207,
          "id": "114958783831682291",
          "time": 1754131833369,
          "text": "",
          "type": "USER",
          "attaches": [
            {
              "duration": 0,
              "conversationId": "7a650671-1348-4454-8b3f-fca9fe138b3f",
              "hangupType": "HUNGUP",
              "_type": "CALL",
              "joinLink": "zCNA-YlHycPDkMjCfDyv3HCK_ixWLNhQb5edJJrhGM0",
              "callType": "AUDIO"
            }
          ]
        },
        "type": "CHAT",
        "title": "Групповой звонок 02 августа",
        "lastFireDelayedErrorTime": 0,
        "lastDelayedUpdateTime": 0,
        "videoConversation": {
          "previewParticipantIds": [],
          "conversationId": "7a650671-1348-4454-8b3f-fca9fe138b3f",
          "joinLink": "zCNA-YlHycPDkMjCfDyv3HCK_ixWLNhQb5edJJrhGM0"
        },
        "options": {
          "SIGN_ADMIN": false,
          "OFFICIAL": false,
          "MESSAGE_COPY_NOT_ALLOWED": false,
          "ONLY_OWNER_CAN_CHANGE_ICON_TITLE": false,
          "ONLY_ADMIN_CAN_ADD_MEMBER": false,
          "ONLY_ADMIN_CAN_CALL": false,
          "SENT_BY_PHONE": false,
          "ALL_CAN_PIN_MESSAGE": true
        },
        "modified": 1754131833389,
        "lastEventTime": 1754131833369,
        "id": -68102870553919,
        "messagesCount": 1,
        "adminParticipants": {
          "13446207": {
            "permissions": 2047,
            "id": 13446207
          }
        },
        "admins": [
          13446207
        ],
        "status": "HIDDEN",
        "participants": {
          "13446207": 1754131823092
        }
      },
      {
        "owner": 13446207,
        "hasBots": true,
        "joinTime": 1,
        "created": 1,
        "lastMessage": {
          "sender": 543835,
          "elements": [
            {
              "type": "STRONG",
              "length": 46
            },
            {
              "length": 18,
              "from": 347,
              "attributes": {
                "url": "https://download.max.ru/"
              },
              "type": "LINK"
            }
          ],
          "id": "114931754389099012",
          "time": 1753719396806,
          "text": "⭐️ Избранное — быстрый доступ к самому важному\n\n📑 Теперь в MAX можно сохранить нужные сообщения, фото, видео или документы, чтобы они не терялись в чатах. В Избранном легко вести списки дел, хранить голосовые заметки или переписки, к которым хочется вернуться позже\n\n🔍 Всё, что добавлено, легко найти через поиск прямо в Избранном\n\nУже доступно в новой версии MAX ✨",
          "type": "USER",
          "attaches": [
            {
              "previewData": "data:image/webp;base64,UklGRrQBAABXRUJQVlA4IKgBAABwCACdASoyADIAPl0ki0WjoiEc/sQAOAXEoAyjOlBwRRsBKLKwSREU/Iv8bCqaHbynZMkj2q12ftLvAlA5E7cMnLfiGM0su0c0CXXAAP7D+f1guMxKyZPg98/XtlJg71V/+3rm277uPIV53+6P/anpX/y45hsdf/00j/7Up/+NIxztfeO91ubi3SCqCjHj+DmXjoVVH+UWp2I3yYSc5Q16vpqh8oYtfD+nM7YnNlAwP0tU57mtobx360KOllGPhyq8KgGoQAulFs56G60A1Hdj7qynfEotslfyV+6NrOPVdiqv8PHcMWUYLFk8J+I1Hdony8aygdYkV/lhys9BexqLsFpN54+qJzC7v1dZG5PCV0PRQaTNugs7jCc+nzzZupOyZJLg6flTDNzCdkY1UCM2yGLi+FNo62KP91251DgxSrFyQjoSrL1klXTkZKfof0pHwt1skmFBjs753gsP7eRdsXSitU+QHPFZhveZsObusmnzIXkK/g6ASjfNYAeWkGaLpNVHOBRoDx7Noikdnp1+Wf99wfckA1Xb8FKH+T/A+wxJgIZIAAAA",
              "duration": 26683,
              "thumbnail": "https://pimg.mycdn.me/getImage?disableStub=true&type=PREPARE&url=https%3A%2F%2Fi.okcdn.ru%2FvideoPreview%3Fid%3D8590624950794%26type%3D39%26idx%3D12%26tkn%3Dfnp-5PB9D8pVfDlyCnRd96DsADw&signatureToken=A3ps53leo5FCy6LrXvHfZQ",
              "videoType": 0,
              "_type": "VIDEO",
              "width": 1440,
              "videoId": 9420407594818,
              "token": "f9LHodD0cOJ66hY8yK7s7jGB5-zkCEcX0XyL8ak3z-omzdbrViowtDcIKfhz7a58vIczseNX5pIqCscKOkOO",
              "height": 1440
            }
          ]
        },
        "type": "DIALOG",
        "lastFireDelayedErrorTime": 0,
        "lastDelayedUpdateTime": 0,
        "prevMessageId": "114892820641563675",
        "options": {
          "SERVICE_CHAT": true
        },
        "modified": 1753719396806,
        "lastEventTime": 1753719396806,
        "id": 12935268,
        "status": "ACTIVE",
        "participants": {
          "543835": 1753125314921,
          "13446207": 1753959986162
        },
        "cid": 12935268
      },
      {
        "owner": 13446207,
        "hasBots": true,
        "joinTime": 1,
        "created": 1,
        "lastMessage": {
          "sender": 452,
          "elements": [
            {
              "length": 20,
              "from": 834,
              "attributes": {
                "url": "https://dev.max.ru/docs/legal/requirements"
              },
              "type": "LINK"
            },
            {
              "length": 19,
              "from": 857,
              "attributes": {
                "url": "https://dev.max.ru/docs/legal/rules"
              },
              "type": "LINK"
            }
          ],
          "options": 1,
          "id": "114924059908074985",
          "time": 1753601988343,
          "text": "Доступные команды:\n\n/create – Создает нового бота\n/delete – Удаляет бота\n/list – Показывает список созданных вами ботов\n/set_name – Устанавливает имя бота\n/set_description – Добавляет описание для бота\n/set_picture – Устанавливает фото профиля для бота\n/get_token – Получить токен для бота\n/refresh_token – Сгенерировать новый токен для бота\n/transfer_bot - Передает права на бота новому владельцу\n/set_app - Добавляет мини-приложение\n/delete_app - Удаляет мини-приложение\n\nУправление командами:\n/get_commands – Получить список команд бота\n/set_commands – Установить команды для бота\n/delete_commands – Очистить список\n\nУправление подписками:\n/get_webhooks – Показать текущие WebHook-подписки\n/set_webhook – Добавить WebHook-подписку\n/remove_webhook – Удалить WebHook-подписку\n\nСоздавая чат-бот или мини-приложение, вы соглашаетесь с правилами размещения и правилами платформы.",
          "type": "USER",
          "attaches": []
        },
        "type": "DIALOG",
        "lastFireDelayedErrorTime": 0,
        "lastDelayedUpdateTime": 0,
        "prevMessageId": "114924059898042521",
        "modified": 1753601988343,
        "lastEventTime": 1753601988343,
        "id": 13446651,
        "status": "ACTIVE",
        "participants": {
          "452": 0,
          "13446207": 1753601988752
        },
        "cid": 13446651
      },
      {
        "owner": 13446207,
        "hasBots": true,
        "joinTime": 1,
        "created": 1,
        "lastMessage": {
          "sender": 2165956,
          "options": 1,
          "id": "114892820632965860",
          "time": 1753125314834,
          "text": "Вот что я умею:\n🏞 Создавать изображения: от аватарки до открытки на день рождения\n\n📝 Писать тексты: помогу поздравить друга с днем рождения или придумать ответ на любое сообщение\n\n📢 Расшифровывать аудиосообщения: превращу пересланное в этот чат голосовое сообщение в текст и предложу подходящий ответ\n\n🔗 Кратко пересказывать видео и статьи: выделю главное из текста или ролика по ссылке\n\n🔎 Отвечать на повседневные вопросы: подскажу прогноз погоды, адрес нужной организации или курс валют",
          "type": "USER",
          "attaches": [
            {
              "previewData": "data:image/webp;base64,UklGRg4CAABXRUJQVlA4IAICAADwCgCdASoyADIAPl0kjEWjoiEc/1wAOAXEoAyMtyDAYWH4AjUFWLf7H8m/oZCv3HJDYOwSNOkIYQGHlXKGT3uoJ2UFaxjyA+Ny1nYXFCd1cd99uKmvwQTT6RjwF78GnAAA/vitt9mGMvf/aPy//H0VX/4P9SNSahtGCGMhmF+ZTAl9fzX2MeKQpb1z4//8BTk1unRWGweGOwrF0p+YeKP630ctQCa8EdBuC0xf9pMr1mJFObV04k8vljzEXjYV7Dj7wNoT+2dK79pNBqzTKiEEzbhORFj/yT5Y52RRpeevebEmerm25G1+ED5zrN9MJeLZ3Aw8JCYdkDLG2gwXFiIjZ0IqMM4AI0Da0vPvu/siF2689FLv8hE+8uRAJSaMU+WUiD58D4jQta1aenblL+C9QzNRq2Sj7N5vSjDiq+6drR3XSjgOJMiisbGkcDeagcubNyMbpmESeRcOapJtlix2n3lVtrD7bIfk793+frZr7wU8mbKfkKZc1a8K8Qacvzg4QTF9LaU12Z5XVHn3KCbf+aAVzu+ib7eUP70LLVQV3CCr7w1AS8ngizYkVISUUkEDj4lEogEIOUwfg+SzlzIMAgOcaxnOhUAgEWrAun5bVlkOsrRGod+x/tlogHR18WwgPY8mNDDJTkH9GA1CAVw78SJo0KD8nhMHhKjfhNh//AAA",
              "duration": 27517,
              "thumbnail": "https://pimg.mycdn.me/getImage?disableStub=true&type=PREPARE&url=https%3A%2F%2Fi.okcdn.ru%2FvideoPreview%3Fid%3D7935734712928%26type%3D39%26idx%3D14%26tkn%3DMkLygPzOW6MGTiSQ7bu0d7UfzpI&signatureToken=jyIw1hQhTQAA4oncJTe0pA",
              "videoType": 0,
              "_type": "VIDEO",
              "width": 1440,
              "videoId": 8884810899296,
              "token": "f9LHodD0cOJHUK1MEK_XIGlb-uBs71qGpj2xPkAtmZu4bcZEhxIQjDng5Te73l7sX_Ru2RkMh2V4QEwYXFqv",
              "height": 1440
            }
          ]
        },
        "type": "DIALOG",
        "lastFireDelayedErrorTime": 0,
        "lastDelayedUpdateTime": 0,
        "prevMessageId": "114892820631004779",
        "modified": 1753125314834,
        "lastEventTime": 1753125314834,
        "id": 15474939,
        "status": "ACTIVE",
        "participants": {
          "2165956": 1753125314804,
          "13446207": 1753601131518
        },
        "cid": 15474939
      }
    ],
    "chatMarker": 0,
    "messages": {},
    "time": 1754258509945,
    "presence": {
      "13446207": {
        "seen": 1754258509,
        "on": "ON"
      }
    },
    "config": {
      "server": {
        "invite-short": "Я пользуюсь мессенджером Max. Присоединяйся! https://max.ru/u/f9LHodD0cOJrki_-CV1BJuiTjuRIws3j01Lp5W_pCFXjexz8qyiDkcKLGh8",
        "money-transfer-botid": 1134691,
        "set-unread-timeout": 31536000,
        "sse": true,
        "account-removal-enabled": false,
        "gce": true,
        "image-size": 40000000,
        "gsse": true,
        "min-image-side-size": 64,
        "account-nickname-enabled": false,
        "max-video-duration-download": 0,
        "max-msg-length": 4000,
        "markdown-menu": 0,
        "nick-min-length": 7,
        "stub": "stub2",
        "file-upload-enabled": true,
        "image-width": 1920,
        "invite-link": "https://max.ru/u/f9LHodD0cOJ_S5PpP_3Y4NERK4MSAkjsbD_ue_RdI1E7s33CjD61DSnliBY",
        "calls-endpoint": "https://calls.okcdn.ru/",
        "send-location-enabled": true,
        "drafts-sync-enabled": false,
        "max-theme-length": 200,
        "video-preview": "480x270",
        "lgce": true,
        "transfer-botid": 1134691,
        "mentions_entity_names_limit": 3,
        "reactions-enabled": true,
        "scheduled-messages-enabled": false,
        "file-upload-unsupported-types": [
          "exe"
        ],
        "msg-get-reactions-page-size": 40,
        "nick-max-length": 60,
        "max-favorite-chats": 5,
        "js-download-delegate": false,
        "wud": false,
        "video-msg-enabled": false,
        "author-visibility-forward-enabled": true,
        "has-phone": true,
        "saved-messages-enabled": true,
        "grse": false,
        "edit-timeout": 604800,
        "react-permission": 2,
        "reactions-max": 8,
        "typing-enabled-FILE": true,
        "update-version-mac": "25.7.9",
        "max-readmarks": 100,
        "sticker-suggestion": [
          "RECENT",
          "NEW",
          "TOP"
        ],
        "max-participants": 20000,
        "audio-transcription-locales": [],
        "welcome-sticker-ids": [
          272821,
          295349,
          13571,
          546741,
          476341
        ],
        "chats-preload-period": 15,
        "file-preview": true,
        "new-admin-permissions": true,
        "music-files-enabled": true,
        "invite-long": "Я пользуюсь мессенджером Max. Присоединяйся! https://max.ru/u/f9LHodD0cOLjdRyUHwOMEZp1O9xGWdqvzbVVBreN1IZ4b_kRLXVGZ1M4aCs",
        "max-favorite-sticker-sets": 100,
        "max-favorite-stickers": 100,
        "update-version-win": "25.7.9",
        "file-upload-max-size": 4294967296,
        "max-description-length": 400,
        "chats-folder-enabled": true,
        "chats-page-size": 50,
        "markdown-enabled": false,
        "max-cname-length": 200,
        "reactions-menu": [
          "👍",
          "❤️",
          "🤣",
          "🔥",
          "😭",
          "💯",
          "💩",
          "😡"
        ],
        "cfs": false,
        "mentions-enabled": true,
        "sticker-sections": [
          "TOP",
          "NEW"
        ],
        "double-tap-reaction": "👍",
        "calls-sdk-mapping": {
          "off": true
        },
        "image-quality": 0.8,
        "stat-session-background-threshold": 60000,
        "image-height": 1920,
        "search-webapps-showcase": {
          "items": [
            {
              "icon": "https://st.max.ru/icons/icon_channel_squircle.webp",
              "title": "Каналы",
              "id": 4479862
            }
          ]
        },
        "max-audio-length": 3600,
        "saved-messages-aliases": [
          "избранное",
          "saved",
          "favourite",
          "favorite",
          "личное",
          "моё",
          "мои",
          "мой",
          "моя",
          "любимое",
          "сохраненные",
          "сохраненное",
          "заметки",
          "закладки"
        ],
        "safe-mode-enabled": true,
        "esia-verify-botId": 6733341
      },
      "chatFolders": {
        "FOLDERS": [
          {
            "favorites": null,
            "include": null,
            "emoji": null,
            "id": "1EAOZ583x9sPcc6koq27J",
            "filters": [
              "UNREAD"
            ],
            "hideEmpty": false,
            "title": "Новые"
          }
        ],
        "ALL_FILTER_EXCLUDE": []
      },
      "user": {
        "SEARCH_BY_PHONE": "ALL",
        "INCOMING_CALL": "ALL",
        "DOUBLE_TAP_REACTION_DISABLED": false,
        "SAFE_MODE_NO_PIN": false,
        "CHATS_PUSH_NOTIFICATION": "ON",
        "CHATS_PUSH_SOUND": "oki.aiff",
        "DOUBLE_TAP_REACTION_VALUE": null,
        "PUSH_DETAILS": true,
        "HIDDEN": false,
        "PUSH_SOUND": "oki.aiff",
        "CHATS_INVITE": "ALL",
        "PUSH_NEW_CONTACTS": true,
        "INACTIVE_TTL": "6M",
        "DONT_DISTURB_UNTIL": 0,
        "SHOW_READ_MARK": true,
        "ALT_KEYBOARD": false,
        "STICKERS_SUGGEST": "ON",
        "SAFE_MODE": false,
        "M_CALL_PUSH_NOTIFICATION": "ON",
        "AUDIO_TRANSCRIPTION_ENABLED": true
      },
      "hash": "497c7ac3-0000000000000000-80000000-0000000000000001-0000000000000000-2-0000019860dbac57"
    },
    "contacts": []
```

___

### get_contact_details
Get users details by their id
#### input
``` json

```

#### return
``` json
null
```