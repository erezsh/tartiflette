from typing import Any


class FieldExecutor:
    def __init__(self, func, coercer, schema_field):
        self._func = func or self._default_resolver
        self._coercer = coercer
        self._schema_field = schema_field

    async def __call__(
        self, parent_result, arguments: dict, req_ctx: dict, info
    ) -> (Any, Any):
        try:
            res = await self._func(parent_result, arguments, req_ctx, info)
            return res, self._coercer(res)
        except Exception as e:  # pylint: disable=broad-except
            return e, None

    @property
    def schema_field(self):
        return self._schema_field

    @property
    def shall_produce_list(self):
        ret = False
        try:
            ret = self._schema_field.gql_type.is_list
        except AttributeError:
            pass
        return ret

    async def _default_resolver(
        self, parent_result, _arguments: dict, _request_ctx: dict, info
    ) -> Any:
        try:
            return getattr(parent_result, info.schema_field.name)
        except AttributeError:
            pass

        try:
            return parent_result[info.schema_field.name]
        except (KeyError, TypeError):
            pass

        return None
