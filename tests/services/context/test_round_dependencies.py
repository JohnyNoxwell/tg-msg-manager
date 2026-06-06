import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from tg_msg_manager.services.context.engine import DeepModeEngine
from tg_msg_manager.services.context.round_dependencies import ContextRoundDependencies


def test_engine_wires_round_runner_to_explicit_dependencies():
    engine = DeepModeEngine(MagicMock(), MagicMock())

    assert engine.round_runner.dependencies is engine.round_dependencies
    assert not hasattr(engine.round_runner, "engine")


def test_round_dependencies_build_explicit_requests_and_preserve_scan_policy():
    async def run():
        parent_resolver = SimpleNamespace(
            fetch_parent_messages=AsyncMock(return_value={})
        )
        candidate_resolver = SimpleNamespace(
            fetch_candidate_pool=AsyncMock(return_value=[])
        )
        dependencies = ContextRoundDependencies(
            storage=MagicMock(),
            cluster_assembler=MagicMock(),
            parent_reply_resolver=parent_resolver,
            candidate_pool_resolver=candidate_resolver,
            time_fallback_resolver=MagicMock(),
        )

        await dependencies.fetch_parent_messages(
            entity="entity",
            chat_id=7,
            anchors_by_cluster={"cluster": []},
        )
        await dependencies.fetch_candidate_pool(
            entity="entity",
            chat_id=7,
            anchor_ids=[10],
            scan_before=8,
            scan_after=60,
        )

        parent_request = parent_resolver.fetch_parent_messages.await_args.kwargs[
            "request"
        ]
        candidate_request = candidate_resolver.fetch_candidate_pool.await_args.kwargs[
            "request"
        ]
        assert parent_request.chat_id == 7
        assert parent_request.anchors_by_cluster == {"cluster": []}
        assert candidate_request.anchor_ids == [10]
        assert dependencies.scan_before_ids(1, 3) == 9
        assert dependencies.scan_after_ids(1, 3, 20) == 120

    asyncio.run(run())
