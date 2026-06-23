# ROBOTERA Knowledge Sources

This file indexes cached references bundled with the `robotera-ops` skill.
It intentionally does not store private document URLs, wiki tokens, docx tokens,
or temporary media download links. When a cached source may be stale, ask the
user for the current source document URL and fetch it with `lark-doc`.

## Cached References

| Title | Cached file | Last synced locally | Notes |
|-|-|-|-|
| ROBOTERA 机器人操作手册 2.0 | [robotera-manual-2.0.md](robotera-manual-2.0.md) | 2026-06-16 | Operational commands, safety notes, ROS2 services/topics, startup flows, robot maintenance, and internal-only sections. |
| SDK log 日志分析释义 | [fault-sdk-log-analysis.md](fault-sdk-log-analysis.md) | 2026-06-16 | SDK log terms, error interpretation, diagnostics, and troubleshooting knowledge. |
| 本地 SDK 部署及注意事项 | [deployment-local-sdk.md](deployment-local-sdk.md) | 2026-06-16 | Local SDK deployment workflow, deployment prerequisites, warnings, and troubleshooting notes. |
| SDK 2.0使用说明 | [sdk-2.0-usage-guide.md](sdk-2.0-usage-guide.md) | 2026-06-23 | SDK 2.0 architecture overview, startup flow context, ROS_DOMAIN_ID ranges, new-machine setup sequence, maintenance config directories, and common SDK 2.0 error summaries. |
| RoboteraStudio 使用手册 | [robotera-studio-user-guide.md](robotera-studio-user-guide.md) | 2026-06-18 | RoboteraStudio desktop and cloud web usage guide for testers, including login, test workflow, expected software configuration, cloud data views, and troubleshooting. |

## Adding Future Documents

For each new document:

1. Add title, cached filename, sync date, and short notes.
2. Fetch the document as Markdown with `lark-cli docs +fetch --api-version v2 --doc "<url>" --doc-format markdown --as user --format json`.
3. Store the fetched Markdown in `references/<category>-<short-topic>.md`.
4. Remove private source URLs, wiki/doc tokens, temporary media links, and credentials before committing.
5. Use a category prefix when helpful: `manual-`, `fault-`, `test-`, `hardware-`, `architecture-`, `deployment-`, `faq-`, `data-`.
6. Update `SKILL.md` only if the new document changes trigger scope, safety behavior, or high-frequency workflows.
