# pozijoist-bot

Two scheduled jobs for pozijoist.com.

- `indexnow.yml` — daily at 06:17 UTC, submits the sitemap to IndexNow.
- `social.yml` — daily at 08:05 and 17:05 UTC, posts the next pending row of `queue.csv` to X and Telegram.

Secrets live in Settings > Secrets and variables > Actions. Never in the code.

To add a post, append a row to `queue.csv` with status `pending`.
