
from typing import Any, Dict, List
from uuid import uuid4

from tartiflette.executors.field_executors import FieldExecutor
from tartiflette.executors.types import ExecutionContext, Info
from tartiflette.schema import GraphQLSchema
from tartiflette.types.exceptions.tartiflette import GraphQLError
from tartiflette.types.location import Location

from .node import Node


class NodeField(Node):
    def __init__(
        self,
        name: str,
        schema: GraphQLSchema,
        field_executor: FieldExecutor,
        location: Location,
        path: List[str],
        type_condition: str,
        node_registry,
        marshalled: dict = None,
        raw=None,
    ):
        super().__init__(path, "Field", location, name)
        # Execution
        self.schema = schema
        self.field_executor = field_executor
        self.arguments = {}
        self.type_condition = type_condition
        self.raw = raw
        self.coerced = None
        self.marshalled = marshalled if marshalled is not None else {}
        # Meta
        self.in_introspection = field_executor.schema_field.name in [
            "__type",
            "__schema",
            "__typename",
        ]

        self.node_registry = node_registry
        self.uuid = str(uuid4())

    def cancel_children(self):
        for child in self.children:
            child.cancel_children()
            self.node_registry.remove_node(child)

    async def __call__(
        self, exec_ctx: ExecutionContext, request_ctx: Dict[str, Any]
    ) -> Any:

        # TODO understand why I need this
        if self.parent and not self.parent.raw:
            return

        self.raw, self.coerced = await self.field_executor(
            self.parent.raw if self.parent else None,
            self.arguments,
            request_ctx,
            Info(
                query_field=self,
                schema_field=self.field_executor.schema_field,
                schema=self.schema,
                path=self.path,
                location=self.location,
                execution_ctx=exec_ctx,
            ),
        )

        if self.parent:
            self.parent.marshalled[self.name] = self.coerced

        if isinstance(self.raw, Exception):
            gql_error = GraphQLError(str(self.raw), self.path, [self.location])
            self.cancel_children()
            if self.field_executor.schema_field.gql_type.is_not_null:
                gql_error.user_message = (
                    "%s - %s can't be none, it is dropped"
                    % (gql_error.message, self.name)
                )
                if self.parent:
                    del self.parent.marshalled[self.name]
            exec_ctx.add_error(gql_error)
        else:
            if self.children and self.field_executor.shall_produce_list:
                self._multiply()

        self.marshalled = self.coerced

    def clone(self, raw=None, marshalled=None, clone_children=True, level=0):
        a_clone = NodeField(
            name=self.name,
            schema=self.schema,
            field_executor=self.field_executor,
            location=self.location,
            path=self.path,
            type_condition=self.type_condition,
            node_registry=self.node_registry,
            marshalled=marshalled,
            raw=raw,
        )

        if clone_children:
            for child in self.children:
                another_clone = child.clone(level=level + 1)
                another_clone.parent = a_clone
                self.node_registry.add_node(level, another_clone)
                a_clone.children.append(another_clone)

        return a_clone

    def _multiply(self):
        self.cancel_children()
        for index, coerced in enumerate(self.coerced):
            parent = self.clone(
                raw=self.raw[index], marshalled=coerced, clone_children=False
            )

            for child in self.children:
                node = child.clone(level=self.node_registry.current_level + 1)
                node.parent = parent
                parent.children.append(node)
                self.node_registry.add_next_level_node(node)

        self.raw = self.raw[0]
        self.coerced = self.coerced[0]

    def __eq__(self, other):
        return self.uuid == other.uuid
