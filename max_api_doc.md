## op codes
| code | action | description |
|---|---|---|
| 1 | [heartbeat](#heartbeat) | Keep connection alive (send every ~5-10 seconds) |
| 6 | [handshake](#handshake) | Initiate connection; send as first message |
| 19 | [authenticate](#authenticate) | User login; send as second message |
| 32 | [get contact details](#get_contact_details) | Retrieve user contact info by ID |
| 49 | [get history](#get_history) | Fetch chat history |
| 50 | [mark as read](#mark_as_read) | Mark messages as read |
| 64 | [send message](#send_message) | Send a new chat message |
| 75 | [subscribe to chat](#subscribe_to_chat) | Subscribe to chat updates |
| 83 | [get video](#get_video) | Get link to a video |
| 88 | [get file](#get_file) | Get link to a file |

---

### heartbeat
Keeps the connection alive. Send approximately every 5-10 seconds.

#### Input
```json
{
  "interactive": false
}
```

#### Return
```json
null
```

---

### handshake
Initial connection; must be sent first.

#### Input
```json
{
  "userAgent": {
    "deviceType": "WEB"
  }
}
```

#### Return
```json
null
```

---

### authenticate
Authenticate user; should be sent as second message.

#### Input
```json
{
  "interactive": true,
  "token": "TOKEN",
  "chatsSync": 0,
  "contactsSync": 0,
  "presenceSync": 0,
  "draftsSync": 0,
  "chatsCount": 40
}
```

#### Return
```json
{
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
      "options": ["TT", "ONEME"],
      "photoId": 11549759,
      "updateTime": 1754132721403,
      "id": 13446207,
      "baseRawUrl": "https://i.oneme.ru/i?r=BTE2sh_eZW7g8kugOdIm2Not2iYTW6GNe8IqlUN66AbY8T_9cY73tz0ujRAFtR8MPmY"
    }
  },
  "drafts": {
    "chats": { "saved": {}, "discarded": {} },
    "users": { "saved": {}, "discarded": {} }
  },
  "token": "TOKEN",
  "videoChatHistory": false,
  "calls": [],
  "chats": [ /* chat list with details */ ],
  "presence": { "13446207": { "seen": 1754258509, "on": "ON" } },
  "config": { /* configuration settings */ }
}
```

---

### get_contact_details
Retrieve user contact info by their user ID.

#### Input
```json
{}
```

#### Return
```json
null