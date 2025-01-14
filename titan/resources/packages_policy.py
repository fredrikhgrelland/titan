from dataclasses import dataclass

from .resource import Resource, ResourceSpec
from ..enums import ResourceType, Language
from ..scope import SchemaScope
from ..props import (
    EnumProp,
    Props,
    StringListProp,
    StringProp,
)


@dataclass
class _PackagesPolicy(ResourceSpec):
    name: str
    language: Language = Language.PYTHON
    allowlist: list[str] = None
    blocklist: list[str] = None
    additional_creation_blocklist: list[str] = None
    comment: str = None
    owner: str = "SYSADMIN"

    def __post_init__(self):
        super().__post_init__()
        if self.language != Language.PYTHON:
            raise ValueError("Language must be PYTHON")


class PackagesPolicy(Resource):
    """
    A Packages Policy defines a set of rules for allowed and blocked packages.

    CREATE [ OR REPLACE ] PACKAGES POLICY [ IF NOT EXISTS ] <name>
      LANGUAGE PYTHON
      [ ALLOWLIST = ( [ '<packageSpec>' ] [ , '<packageSpec>' ... ] ) ]
      [ BLOCKLIST = ( [ '<packageSpec>' ] [ , '<packageSpec>' ... ] ) ]
      [ ADDITIONAL_CREATION_BLOCKLIST = ( [ '<packageSpec>' ] [ , '<packageSpec>' ... ] ) ]
      [ COMMENT = '<string_literal>' ]
    """

    resource_type = ResourceType.PACKAGES_POLICY
    props = Props(
        language=EnumProp("language", Language, eq=False),
        allowlist=StringListProp("allowlist", parens=True),
        blocklist=StringListProp("blocklist", parens=True),
        additional_creation_blocklist=StringListProp("additional_creation_blocklist", parens=True),
        comment=StringProp("comment"),
    )
    scope = SchemaScope()
    spec = _PackagesPolicy

    def __init__(
        self,
        name: str,
        language: Language = Language.PYTHON,
        allowlist: list[str] = None,
        blocklist: list[str] = None,
        additional_creation_blocklist: list[str] = None,
        comment: str = None,
        owner: str = "SYSADMIN",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._data: _PackagesPolicy = _PackagesPolicy(
            name=name,
            language=language,
            allowlist=allowlist,
            blocklist=blocklist,
            additional_creation_blocklist=additional_creation_blocklist,
            comment=comment,
            owner=owner,
        )
