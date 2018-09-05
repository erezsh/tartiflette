from typing import Optional, Union

from tartiflette.types.type import GraphQLType


class GraphQLList(GraphQLType):
    """
    List Container
    A GraphQLList is a container, wrapping type that points at another type.
    The type contained will be returned as a list instead of a single item.
    """

    def __init__(
        self,
        gql_type: Union[str, GraphQLType],
        description: Optional[str] = None,
    ):
        super().__init__(name=None, description=description, is_list=True)
        self.gql_type = gql_type

    @property
    def is_enum_value(self) -> bool:
        ret = False

        try:
            ret = self.gql_type.is_enum_value
        except AttributeError:
            pass

        return ret

    @property
    def is_not_null(self) -> bool:
        ret = False

        try:
            ret = self.gql_type.is_not_null
        except AttributeError:
            pass

        return ret

    def __repr__(self) -> str:
        return "{}(gql_type={!r}, description={!r})".format(
            self.__class__.__name__, self.gql_type, self.description
        )

    def __str__(self):
        return "[{!s}]".format(self.gql_type)

    def __eq__(self, other):
        return super().__eq__(other) and self.gql_type == other.gql_type
