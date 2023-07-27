from typing import List, Union

from pydantic import BaseModel, Field, ConfigDict, SerializeAsAny, field_serializer

# _ = titan.Policy(
#     acls=[
#         titan.ACL(
#             privs=["READ"],
#             roles=[f"role:ANALYTICS", titan.Role.all["DATAENG"]],
#             resources=[f"tag:group=analytics"],
#         )
#     ],
#     roles={
#         f"role:CLIENT_{client_id}": [client_admin.username],
#     },
# )


# What are all the objects that user X can access?

from .resource import Resource
from .resources import Role, Grant
from .parseable_enum import ParseableEnum


class SuperPriv(ParseableEnum):
    READ = "READ"
    # CREATE = "CREATE"
    # DELETE = "DELETE"


class ACL(BaseModel):
    privs: List[SuperPriv]
    roles: List[Union[str, Role]]
    resources: List[Resource]

    def __init__(self, privs, roles, resources):
        self.privs = privs
        self.roles = roles
        self.resources = resources

    def grants(self):
        """Return a list of grants that this ACL represents."""
        return [
            Grant(priv=priv, role=role, resource=resource)
            for priv in self.privs
            for role in self.roles
            for resource in self.resources
        ]
