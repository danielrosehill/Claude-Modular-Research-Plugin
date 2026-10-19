# Delivery

Before the first upload, say in one line that the PDF (and MP3) are being sent to
Google Drive and the email provider.

## Drive

Destination: `<drive.folder>/<Name>/` — one subfolder per run.

### `method: rclone` (recommended)

```bash
R="<drive.rclone_remote>"; F=(<drive.rclone_flags>)
rclone copyto "${F[@]}" outputs/<Name>.pdf "$R<drive.folder>/<Name>/<Name>.pdf"
rclone copyto "${F[@]}" outputs/<Name>-podcast.mp3 "$R<drive.folder>/<Name>/<Name>-podcast.mp3"
rclone lsjson "${F[@]}" "$R<drive.folder>/<Name>/"     # → each file's ID
```

Links are `https://drive.google.com/file/d/<ID>/view` — private to the owner, which
is what you want. **Do not use `rclone link` on a Drive remote: it makes the file
public ("anyone with the link").**

`rclone copyto` creates missing folders. Check the folder name against
`rclone lsd` first: Drive folder names can carry trailing spaces, and a near-miss
silently creates a second folder.

### `method: skill`

Invoke the skill named in `drive.skill` with the file path and destination, once
per file. Take the returned link.

### `method: mcp`

A Drive MCP whose upload tool takes a URL (not a local path) needs the file staged
first — same staging step as the email attachment below.

## Email

Plain, short, English. Subject: `Research briefing: <title>`.

```
<The abstract, 3–5 sentences.>

Key findings
- <one line each, 3–6 of them>

Open questions
- <one line each, if any>

PDF: <Drive link>
Podcast (<N> min): <Drive link>
Repo: <GitHub URL>
```

Send it with `email.method`:

- `gmail-mcp`: call `email.mcp_send_tool` with `to`, `subject`, `body`, and the
  account parameter set to `email.from_account` when the tool has one. Attachment,
  when `email.attach_pdf` is true: stage the PDF (`email.staging`), pass
  `attachments: [{filename, mime_type: "application/pdf", url}]`.
  **Check the staging upload's exit status, not just that a URL came back** —
  presigning is offline and signs URLs for files that do not exist.
- `skill`: invoke `email.skill` with the recipient, subject, body and links.

Staging with `rclone-link`:

```bash
rclone copyto <staging.flags> outputs/<Name>.pdf "<staging.remote>/<Name>.pdf" && \
rclone link <staging.flags> --expire <staging.expire> "<staging.remote>/<Name>.pdf"
```

If an email body is not in English and the language is right-to-left, use an RTL
email route if one exists; do not send RTL text as plain text.

## Verify and record

- Drive: `rclone lsjson` shows both files with non-zero size.
- Email: search the sent folder for the subject (e.g. Gmail search
  `in:sent subject:"Research briefing: <title>"`) and confirm one hit.

Write `delivery.json` at the workspace root:

```json
{
  "delivered_at": "2026-10-19T14:02:00+03:00",
  "repo": "https://github.com/<owner>/<Name>",
  "drive": {
    "folder": "<drive.folder>/<Name>",
    "pdf":     { "id": "…", "url": "https://drive.google.com/file/d/…/view" },
    "podcast": { "id": "…", "url": "https://drive.google.com/file/d/…/view", "duration_seconds": 912 }
  },
  "email": { "to": "…", "subject": "…", "message_id": "…", "sent_at": "…", "pdf_attached": true }
}
```

Update `README.md` with the Drive links, commit `Delivered`, push.
