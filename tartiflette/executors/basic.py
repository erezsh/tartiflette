import asyncio

from tartiflette.executors.helpers import visualize_gql_tree_and_data
from tartiflette.executors.types import ExecutionContext


async def _level_execute(resolvers, exec_ctx, request_ctx):
    coroutines = [
        resolver(exec_ctx, request_ctx)
        for resolver in resolvers
        if not resolver.type_condition
        or (
            resolver.type_condition
            and resolver.parent
            and resolver.type_condition
            == resolver.parent.results.__class__.__name__
        )
        # TODO base __class__.__name__ on sdl parsing result
    ]

    return await asyncio.gather(*coroutines, return_exceptions=True)


async def execute(node_registry, request_ctx):
    results = {"data": {}, "errors": []}
    exec_ctx = ExecutionContext()
    gql_nodes = node_registry.nodes

    while node_registry.has_next():
        nodes = node_registry.next_level()
        level = node_registry.current_level
        await _level_execute(nodes, exec_ctx, request_ctx)
        visualize_gql_tree_and_data(gql_nodes, level, value="raw")
        visualize_gql_tree_and_data(gql_nodes, level)
        visualize_gql_tree_and_data(gql_nodes, level, value="marshalled")

    results["errors"] += [err.coerce_value() for err in exec_ctx.errors if err]

    for node in node_registry.root_nodes:
        results["data"][node.name] = node.marshalled

    if not results["errors"]:
        del results["errors"]

    return results
