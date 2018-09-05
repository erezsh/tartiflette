from typing import Optional


class GraphQLType:
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_not_null: Optional[bool] = False,
        is_list: Optional[bool] = False,
        is_enum_value: Optional[bool] = False,
    ):
        self.name = name
        self.description = description
        # self.sdl_info  # TODO: Is it useful to store the SDL source AST Node ?
        self._is_list = is_list
        self._is_not_null = is_not_null
        self._is_enum_value = is_enum_value

    @property
    def is_list(self) -> bool:
        return self._is_list

    @property
    def is_not_null(self) -> bool:
        return self._is_not_null

    @property
    def is_enum_value(self) -> bool:
        return self._is_enum_value

    def __repr__(self) -> str:
        return "{}(name={!r}, description={!r})".format(
            self.__class__.__name__, self.name, self.description
        )

    def __str__(self) -> str:
        return "{!s}".format(self.name)

    def __eq__(self, other) -> bool:
        return self is other or (
            type(self) is type(other) and self.name == other.name
        )
