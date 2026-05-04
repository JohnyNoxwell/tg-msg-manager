from datetime import datetime
from typing import Any, List, Optional

from ....core.models.reporting import (
    ReportDatabaseSummary,
    ReportRetrySummary,
    ReportTargetSummary,
)
from ..records import RetryTaskRecord
from .common import SQLiteReadCommonMixin


class SQLiteReportingReadMixin(SQLiteReadCommonMixin):
    def get_report_database_summary(self) -> ReportDatabaseSummary:
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM chats) AS chats_count,
                    (SELECT COUNT(*) FROM users) AS users_count,
                    (SELECT COUNT(*) FROM messages) AS messages_count,
                    (SELECT COUNT(*) FROM sync_targets) AS targets_count,
                    (SELECT COUNT(*) FROM sync_targets WHERE is_complete = 0) AS incomplete_targets_count,
                    (SELECT COUNT(*) FROM message_target_links) AS target_links_count,
                    (SELECT COUNT(*) FROM messages WHERE reply_to_id IS NOT NULL) AS reply_messages_count,
                    (
                        SELECT COUNT(*)
                        FROM messages m
                        WHERE m.reply_to_id IS NOT NULL
                          AND NOT EXISTS (
                              SELECT 1
                              FROM messages parent
                              WHERE parent.chat_id = m.chat_id
                                AND parent.message_id = m.reply_to_id
                          )
                    ) AS missing_parent_count,
                    (
                        SELECT COUNT(DISTINCT context_group_id)
                        FROM messages
                        WHERE COALESCE(TRIM(context_group_id), '') != ''
                    ) AS context_cluster_count
            """
            ).fetchone()
        return ReportDatabaseSummary(
            chats_count=int(row["chats_count"] or 0),
            users_count=int(row["users_count"] or 0),
            messages_count=int(row["messages_count"] or 0),
            targets_count=int(row["targets_count"] or 0),
            incomplete_targets_count=int(row["incomplete_targets_count"] or 0),
            target_links_count=int(row["target_links_count"] or 0),
            reply_messages_count=int(row["reply_messages_count"] or 0),
            missing_parent_count=int(row["missing_parent_count"] or 0),
            context_cluster_count=int(row["context_cluster_count"] or 0),
        )

    def get_report_target_summaries(self) -> List[ReportTargetSummary]:
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    t.user_id,
                    t.chat_id,
                    t.author_name,
                    c.title AS chat_title,
                    t.last_msg_id,
                    t.tail_msg_id,
                    t.is_complete,
                    t.deep_mode,
                    t.recursive_depth,
                    COALESCE(t.last_sync_at, 0) AS last_sync_at,
                    COUNT(l.message_id) AS linked_messages,
                    COALESCE(SUM(CASE WHEN m.user_id = t.user_id THEN 1 ELSE 0 END), 0) AS own_messages,
                    COALESCE(SUM(CASE WHEN m.user_id != t.user_id THEN 1 ELSE 0 END), 0) AS context_messages,
                    COALESCE(SUM(
                        CASE
                            WHEN m.reply_to_id IS NOT NULL
                             AND NOT EXISTS (
                                 SELECT 1
                                 FROM messages parent
                                 WHERE parent.chat_id = m.chat_id
                                   AND parent.message_id = m.reply_to_id
                             )
                            THEN 1
                            ELSE 0
                        END
                    ), 0) AS missing_parent_messages
                FROM sync_targets t
                LEFT JOIN chats c ON c.chat_id = t.chat_id
                LEFT JOIN message_target_links l
                    ON l.chat_id = t.chat_id AND l.target_user_id = t.user_id
                LEFT JOIN messages m
                    ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                GROUP BY
                    t.user_id,
                    t.chat_id,
                    t.author_name,
                    c.title,
                    t.last_msg_id,
                    t.tail_msg_id,
                    t.is_complete,
                    t.deep_mode,
                    t.recursive_depth,
                    t.last_sync_at
                ORDER BY COALESCE(t.author_name, ''), t.chat_id, t.user_id
            """
            ).fetchall()
        return [
            ReportTargetSummary(
                user_id=int(row["user_id"] or 0),
                chat_id=int(row["chat_id"] or 0),
                author_name=row["author_name"],
                chat_title=row["chat_title"],
                last_msg_id=int(row["last_msg_id"] or 0),
                tail_msg_id=int(row["tail_msg_id"] or 0),
                is_complete=bool(int(row["is_complete"] or 0)),
                deep_mode=bool(int(row["deep_mode"] or 0)),
                recursive_depth=int(row["recursive_depth"] or 0),
                last_sync_at=int(row["last_sync_at"] or 0),
                linked_messages=int(row["linked_messages"] or 0),
                own_messages=int(row["own_messages"] or 0),
                context_messages=int(row["context_messages"] or 0),
                missing_parent_messages=int(row["missing_parent_messages"] or 0),
            )
            for row in rows
        ]

    def get_report_retry_summary(
        self, now_ts: Optional[int] = None
    ) -> ReportRetrySummary:
        due_at = now_ts if now_ts is not None else int(datetime.now().timestamp())
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_tasks,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_tasks,
                    SUM(CASE WHEN status = 'retrying' THEN 1 ELSE 0 END) AS retrying_tasks,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_tasks,
                    SUM(
                        CASE
                            WHEN status IN ('pending', 'retrying')
                             AND next_retry_timestamp <= ?
                            THEN 1
                            ELSE 0
                        END
                    ) AS due_tasks
                FROM retry_queue
            """,
                (due_at,),
            ).fetchone()
        return ReportRetrySummary(
            total_tasks=int(row["total_tasks"] or 0),
            pending_tasks=int(row["pending_tasks"] or 0),
            retrying_tasks=int(row["retrying_tasks"] or 0),
            completed_tasks=int(row["completed_tasks"] or 0),
            failed_tasks=int(row["failed_tasks"] or 0),
            due_tasks=int(row["due_tasks"] or 0),
        )

    def get_due_retry_tasks(
        self,
        now_ts: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[RetryTaskRecord]:
        due_at = now_ts if now_ts is not None else int(datetime.now().timestamp())
        limit_clause = f" LIMIT {int(limit)}" if limit else ""
        with self._read_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM retry_queue
                WHERE status IN ('pending', 'retrying')
                  AND next_retry_timestamp <= ?
                ORDER BY next_retry_timestamp ASC, retry_count ASC, created_at ASC
                {limit_clause}
            """,
                (due_at,),
            ).fetchall()
            return [RetryTaskRecord.coerce(dict(row)) for row in rows]

    def get_retry_tasks(self) -> List[RetryTaskRecord]:
        return self.get_due_retry_tasks()

    def list_retry_tasks(
        self,
        limit: Optional[int] = None,
        include_completed: bool = True,
    ) -> List[RetryTaskRecord]:
        clauses = []
        params: list[Any] = []
        if not include_completed:
            clauses.append("status IN ('pending', 'retrying')")
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        limit_clause = f" LIMIT {int(limit)}" if limit else ""
        with self._read_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM retry_queue
                {where_clause}
                ORDER BY
                    CASE status
                        WHEN 'pending' THEN 0
                        WHEN 'retrying' THEN 1
                        WHEN 'failed' THEN 2
                        ELSE 3
                    END,
                    next_retry_timestamp ASC,
                    updated_at DESC
                {limit_clause}
            """,
                params,
            ).fetchall()
            return [RetryTaskRecord.coerce(dict(row)) for row in rows]
