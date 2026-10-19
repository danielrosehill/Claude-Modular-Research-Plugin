# Config

One JSON file, machine-local, never committed:
`~/.claude-plugins/research-briefing/config.json` (override with
`$RESEARCH_BRIEFING_CONFIG`). A full example is `config.example.json` at the plugin
root. Every field is optional; the defaults are shown.

```json
{
  "plugin_clone": null,
  "workspace": {
    "parent_dir": "~/repos",
    "topic_subfolders": false,
    "name_pattern": "{Topic}-{MMYY}",
    "github": { "create": true, "visibility": "private", "owner": null }
  },
  "pdf": { "toc": true, "author": "Claude" },
  "podcast": {
    "enabled": true,
    "model": "gemini-3.8-flash-tts",
    "hosts": { "ALEX": "Kore", "SAM": "Puck" },
    "target_minutes": 15,
    "api_key_op_ref": null
  },
  "drive": {
    "enabled": true,
    "method": "rclone",
    "rclone_remote": "gdrive:",
    "rclone_flags": [],
    "folder": "Research Briefings",
    "upload": ["pdf", "podcast"]
  },
  "email": {
    "enabled": true,
    "method": "gmail-mcp",
    "mcp_send_tool": null,
    "from_account": null,
    "to": null,
    "attach_pdf": true,
    "staging": null
  }
}
```

| Field | Meaning |
|---|---|
| `plugin_clone` | Absolute path of a local clone of this plugin, used when `${CLAUDE_PLUGIN_ROOT}` is unset (e.g. the skill was read from a catalogue rather than installed). |
| `workspace.parent_dir` | Where new workspace repos are created. |
| `workspace.topic_subfolders` | If true, `parent_dir` holds topic group folders; pick the most specific existing one for the subject instead of creating at `parent_dir` directly. Never create a new group folder unasked. |
| `workspace.name_pattern` | `{Topic}` = Train-Case topic, 2–5 words; `{MMYY}` = month+year of creation. |
| `workspace.github.visibility` | `private` or `public`. |
| `podcast.model` | Any Gemini TTS model. `gemini-3.x` and `gemini-2.5` take different request shapes; the script handles both. |
| `podcast.hosts` | Exactly two `LABEL: voice` pairs. Labels are what the script uses (`ALEX:`); voices are Gemini prebuilt voice names. |
| `podcast.target_minutes` | Script length target at ~150 spoken words per minute. |
| `podcast.api_key_op_ref` | 1Password reference (`op://Vault/Item/field`) for the Gemini key. Wins over `$GEMINI_API_KEY`, which is commonly stale. |
| `drive.method` | `rclone` (local, one command, recommended), `skill` (delegate to a named Drive-upload skill in `drive.skill`), or `mcp` (a Google Drive MCP that takes a file URL — needs `email.staging`-style staging). |
| `drive.rclone_remote` / `rclone_flags` | Remote plus extra flags, e.g. `["--drive-team-drive", "<shared drive id>"]` to target a Shared Drive through a My-Drive remote. |
| `drive.folder` | Folder under the remote root. Each run gets its own subfolder named after the workspace. |
| `email.method` | `gmail-mcp` (call the tool in `mcp_send_tool`), `skill` (delegate to `email.skill`), or `none`. |
| `email.from_account` | Account the Gmail MCP is bound to, when the tool takes one. |
| `email.to` | Recipient. |
| `email.attach_pdf` | Attach the PDF (needs `staging` when the mail tool fetches attachments by URL), otherwise links only. |
| `email.staging` | How to get a short-lived URL for a local file: `{ "method": "rclone-link", "remote": "<s3 remote:bucket/prefix>", "flags": [], "expire": "24h" }`. Use a bucket that exists for staging and expires its objects; never an unrelated bucket. **Never `rclone link` on a Drive remote** — that sets "anyone with the link" on the file. |

## Setup interview

Ask only what cannot be discovered. Discover first:

- `rclone listremotes` → candidate Drive remotes (`type = drive` in `rclone config show <remote>`).
- `gh auth status` → GitHub owner.
- `op whoami` → whether 1Password references are usable.
- Which Gmail send tool the session has (search deferred tools for `send_gmail_message`).

Then ask, in one message: parent directory for workspaces, Drive destination folder,
email recipient, and whether a podcast should be made by default. Write the file,
show it, and continue the run.
