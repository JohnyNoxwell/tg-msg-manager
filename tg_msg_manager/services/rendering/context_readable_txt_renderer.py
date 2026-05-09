from collections import OrderedDict
from typing import Iterable, Optional

from .models import RenderMessage, TxtRenderOptions


class ContextReadableTxtRenderer:
    def render(
        self, records: Iterable[object], options: TxtRenderOptions | None = None
    ) -> str:
        options = options or TxtRenderOptions(profile="context-readable")
        messages = sorted(
            (RenderMessage.coerce(record) for record in records),
            key=lambda message: (message.timestamp, message.message_id),
        )
        if not messages:
            return "# Telegram Export\nTXT profile: context-readable\n"

        target_user_id = options.target_user_id or self._infer_target_user_id(messages)
        target_author = options.target_author_name or self._infer_target_author(
            messages, target_user_id
        )
        chat_label = options.chat_title or self._infer_chat_label(messages, options)

        lines = [
            "# Telegram Export",
            "TXT profile: context-readable",
            f"Target: {target_author} ({target_user_id})",
            f"Chat: {chat_label}",
            "",
        ]

        for block_number, block_messages in enumerate(
            self._group_messages(messages, target_user_id), start=1
        ):
            lines.extend(
                self._render_block(
                    block_number=block_number,
                    messages=block_messages,
                    target_user_id=target_user_id,
                    target_author=target_author,
                    chat_label=chat_label,
                    options=options,
                )
            )
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _group_messages(
        self, messages: list[RenderMessage], target_user_id: Optional[int]
    ) -> list[list[RenderMessage]]:
        grouped: "OrderedDict[str, list[RenderMessage]]" = OrderedDict()
        fallback_messages: list[RenderMessage] = []

        for message in messages:
            if message.context_group_id:
                key = f"group:{message.chat_id}:{message.context_group_id}"
                grouped.setdefault(key, []).append(message)
            else:
                fallback_messages.append(message)

        groups = list(grouped.values())
        if fallback_messages:
            if target_user_id is None:
                groups.append(fallback_messages)
            elif any(
                message.user_id == target_user_id for message in fallback_messages
            ):
                groups.append(fallback_messages)
            elif not groups:
                groups.append(fallback_messages)

        if not groups and messages:
            groups.append(messages)
        return sorted(
            groups,
            key=lambda group: (
                min(message.timestamp for message in group),
                min(message.message_id for message in group),
            ),
        )

    def _render_block(
        self,
        *,
        block_number: int,
        messages: list[RenderMessage],
        target_user_id: Optional[int],
        target_author: str,
        chat_label: str,
        options: TxtRenderOptions,
    ) -> list[str]:
        target_messages = [
            message for message in messages if message.user_id == target_user_id
        ]
        if not target_messages:
            target_messages = list(messages)

        first_target = min(target_messages, key=lambda message: message.timestamp)
        context_before = [
            message
            for message in messages
            if message.user_id != target_user_id
            and (message.timestamp, message.message_id)
            < (first_target.timestamp, first_target.message_id)
        ]
        context_after = [
            message
            for message in messages
            if message.user_id != target_user_id and message not in context_before
        ]
        start_time = min(message.timestamp for message in messages)
        end_time = max(message.timestamp for message in messages)
        target_label = (
            "[TARGET MESSAGES]" if len(target_messages) > 1 else "[TARGET MESSAGE]"
        )

        lines = [
            "-" * 60,
            f"CONTEXT BLOCK #{block_number:04d} · {start_time.strftime('%Y-%m-%d')}",
            f"TARGET: {target_author} ({target_user_id})",
            f"CHAT: {chat_label}",
            f"TIME RANGE: {start_time.strftime('%H:%M:%S')}-{end_time.strftime('%H:%M:%S')}",
            f"TARGET MESSAGES: {len(target_messages)}",
            "-" * 60,
            "",
            "[REPLIED MESSAGE]",
        ]
        lookup = {message.message_id: message for message in messages}
        lines.extend(self._render_replied_message(target_messages, messages, options))
        lines.extend(["", "[CONTEXT BEFORE]"])
        lines.extend(self._render_message_list(context_before, options, lookup))
        lines.extend(["", target_label])
        lines.extend(self._render_message_list(target_messages, options, lookup))
        lines.extend(["", "[CONTEXT AFTER]"])
        lines.extend(self._render_message_list(context_after, options, lookup))
        return lines

    def _render_replied_message(
        self,
        target_messages: list[RenderMessage],
        block_messages: list[RenderMessage],
        options: TxtRenderOptions,
    ) -> list[str]:
        lookup = {message.message_id: message for message in block_messages}
        reply_refs = []
        seen: set[int] = set()
        for target in target_messages:
            if target.reply_to_id is None or target.reply_to_id in seen:
                continue
            seen.add(target.reply_to_id)
            reply_refs.append((target, lookup.get(target.reply_to_id)))

        if not reply_refs:
            return ["None"]
        if len(reply_refs) == 1:
            target, replied = reply_refs[0]
            if replied is None:
                return [f"↪ missing reply #{target.reply_to_id}"]
            return self._render_single_message(replied, options, include_reply=False)

        lines = ["Multiple replied messages:"]
        for target, replied in reply_refs:
            if replied is None:
                lines.append(
                    f"- target #{target.message_id} -> missing reply #{target.reply_to_id}"
                )
            else:
                excerpt = self._excerpt(replied.text, options.max_reply_excerpt_chars)
                lines.append(
                    f"- target #{target.message_id} -> {self._author(replied)} · "
                    f'{replied.timestamp.strftime("%H:%M:%S")} · "{excerpt}"'
                )
        return lines

    def _render_message_list(
        self,
        messages: list[RenderMessage],
        options: TxtRenderOptions,
        lookup: dict[int, RenderMessage],
    ) -> list[str]:
        if not messages:
            return ["None"]
        lines: list[str] = []
        for index, message in enumerate(messages):
            if index:
                lines.append("")
            lines.extend(self._render_single_message(message, options, lookup=lookup))
        return lines

    def _render_single_message(
        self,
        message: RenderMessage,
        options: TxtRenderOptions,
        *,
        include_reply: bool = True,
        lookup: Optional[dict[int, RenderMessage]] = None,
    ) -> list[str]:
        lines = [
            f"{message.timestamp.strftime('%H:%M:%S')} · {self._author(message)} ({message.user_id})"
        ]
        if include_reply and message.reply_to_id is not None:
            replied = (lookup or {}).get(message.reply_to_id)
            if replied is None:
                lines.append(f"↪ missing reply #{message.reply_to_id}")
            else:
                excerpt = self._excerpt(replied.text, options.max_reply_excerpt_chars)
                lines.append(
                    f"↪ replies to {self._author(replied)} · "
                    f'{replied.timestamp.strftime("%H:%M:%S")} · "{excerpt}"'
                )
        text = (
            message.text if message.text and message.text.strip() else "(empty message)"
        )
        lines.extend(text.splitlines())
        return lines

    def _infer_target_user_id(self, messages: list[RenderMessage]) -> int:
        return messages[0].user_id

    def _infer_target_author(
        self, messages: list[RenderMessage], target_user_id: Optional[int]
    ) -> str:
        for message in messages:
            if message.user_id == target_user_id and message.author_name:
                return message.author_name
        return f"User_{target_user_id}"

    def _infer_chat_label(
        self, messages: list[RenderMessage], options: TxtRenderOptions
    ) -> str:
        if options.chat_id is not None:
            return str(options.chat_id)
        chat_ids = sorted({message.chat_id for message in messages})
        if len(chat_ids) == 1:
            return str(chat_ids[0])
        return "multiple chats"

    def _author(self, message: RenderMessage) -> str:
        return message.author_name or f"User_{message.user_id}"

    def _excerpt(self, text: Optional[str], max_chars: int) -> str:
        clean = (text or "").replace("\n", " ").strip()
        if len(clean) <= max_chars:
            return clean
        return clean[: max(0, max_chars - 3)].rstrip() + "..."
