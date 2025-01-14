from dataclasses import dataclass

from .resource import Resource, ResourceSpec
from ..enums import DataType, ResourceType
from ..props import FlagProp, Props, StringProp
from ..parse import _parse_column, _parse_props
from ..scope import TableScope


@dataclass
class _Column(ResourceSpec):
    name: str
    data_type: str
    collate: str = None
    comment: str = None
    not_null: bool = None
    constraint: str = None


class Column(Resource):
    """
    <col_name> <col_type>
      [ COLLATE '<collation_specification>' ]
      [ COMMENT '<string_literal>' ]
      [ { DEFAULT <expr>
        | { AUTOINCREMENT | IDENTITY } [ { ( <start_num> , <step_num> ) | START <num> INCREMENT <num> } ] } ]
      [ NOT NULL ]
      [ [ WITH ] MASKING POLICY <policy_name> [ USING ( <col_name> , <cond_col1> , ... ) ] ]
      [ [ WITH ] TAG ( <tag_name> = '<tag_value>' [ , <tag_name> = '<tag_value>' , ... ] ) ]
      [ inlineConstraint ]

    inlineConstraint ::=
      [ CONSTRAINT <constraint_name> ]
      { UNIQUE | PRIMARY KEY | { [ FOREIGN KEY ] REFERENCES <ref_table_name> [ ( <ref_col_name> ) ] } }
      [ <constraint_properties> ]
    """

    resource_type = ResourceType.COLUMN
    props = Props(
        collate=StringProp("collate", eq=False),
        comment=StringProp("comment", eq=False),
        not_null=FlagProp("not null"),
    )
    scope = TableScope()
    spec = _Column

    def __init__(
        self,
        name: str,
        data_type: DataType,
        collate: str = None,
        comment: str = None,
        not_null: bool = None,
        constraint: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._data: _Column = _Column(
            name,
            data_type,
            collate=collate,
            comment=comment,
            not_null=not_null,
            constraint=constraint,
        )

    @classmethod
    def from_sql(cls, sql):
        parse_results = _parse_column(sql)
        remainder = parse_results.pop("remainder", "")
        props = _parse_props(cls.props, remainder)
        return cls(**parse_results, **props)

    def serialize(self):
        return {"name": self._data.name, "data_type": self._data.data_type}
