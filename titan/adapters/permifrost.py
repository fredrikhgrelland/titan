import yaml

from titan.enums import ResourceType
from titan.identifiers import FQN
from titan.parse import parse_identifier
from titan.privs import DatabasePriv, SchemaPriv, WarehousePriv
from titan.resources import FutureGrant, Grant, RoleGrant
from titan.resources.resource import ResourcePointer


DATABASE_READ_PRIVS = [DatabasePriv.USAGE]
DATABASE_WRITE_PRIVS = [DatabasePriv.USAGE, DatabasePriv.MONITOR, DatabasePriv.CREATE_SCHEMA]
SCHEMA_READ_PRIVS = [SchemaPriv.USAGE]
SCHEMA_WRITE_PRIVS = [
    SchemaPriv.USAGE,
    SchemaPriv.MONITOR,
    SchemaPriv.CREATE_ALERT,
    SchemaPriv.CREATE_DYNAMIC_TABLE,
    SchemaPriv.CREATE_EXTERNAL_TABLE,
    SchemaPriv.CREATE_FILE_FORMAT,
    SchemaPriv.CREATE_FUNCTION,
    SchemaPriv.CREATE_MASKING_POLICY,
    SchemaPriv.CREATE_MATERIALIZED_VIEW,
    SchemaPriv.CREATE_NETWORK_RULE,
    SchemaPriv.CREATE_PACKAGES_POLICY,
    SchemaPriv.CREATE_PASSWORD_POLICY,
    SchemaPriv.CREATE_PIPE,
    SchemaPriv.CREATE_PROCEDURE,
    SchemaPriv.CREATE_ROW_ACCESS_POLICY,
    SchemaPriv.CREATE_SECRET,
    SchemaPriv.CREATE_SEQUENCE,
    SchemaPriv.CREATE_SESSION_POLICY,
    SchemaPriv.CREATE_SNOWFLAKE_ML_ANOMALY_DETECTION,
    SchemaPriv.CREATE_SNOWFLAKE_ML_FORECAST,
    SchemaPriv.CREATE_STAGE,
    SchemaPriv.CREATE_STREAM,
    SchemaPriv.CREATE_TABLE,
    SchemaPriv.CREATE_TAG,
    SchemaPriv.CREATE_TASK,
    SchemaPriv.CREATE_VIEW,
]

WAREHOUSE_PRIVS = [WarehousePriv.USAGE, WarehousePriv.OPERATE, WarehousePriv.MONITOR]


def _parse_permifrost_identifier(identifier: str, is_db_scoped: bool = False):
    """
    Parse a permifrost identifier into a database and schema.

    Args:
        identifier (str): The identifier to parse.
        is_db_scoped (bool): Whether the identifier is scoped to a database.

    Returns:
        tuple: A tuple containing the database and schema.
    """
    parts = identifier.split(".")
    if is_db_scoped:
        return FQN(database=parts[0], name=parts[1])
    return FQN(database=parts[0], schema=parts[1], name=parts[2])


def read_permifrost_config(file_path):
    """
    Read the permifrost config file and return the config as a dictionary.

    Args:
        file_path (str): The path to the permifrost config file.

    Returns:
        dict: The permifrost config as a dictionary.
    """
    # return resources.read_yaml(file_path)
    config = {}
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)

    version = config.pop("version", None)
    databases = config.pop("databases", [])
    roles = config.pop("roles", [])
    users = config.pop("users", [])
    warehouses = config.pop("warehouses", [])
    integrations = config.pop("integrations", [])

    return [
        # *databases,
        *_get_role_resources(roles),
        *_get_user_resources(users),
        # warehouses,
        # integrations,
    ]


def _get_role_resources(roles: list):
    resources = []
    for permifrost_role in roles:
        role_name, config = permifrost_role.popitem()
        role = ResourcePointer(name=role_name, resource_type=ResourceType.ROLE)
        resources.append(role)

        warehouses = config.get("warehouses", [])
        for wh in warehouses:
            resources.append(ResourcePointer(name=wh, resource_type=ResourceType.WAREHOUSE))
            for priv in WAREHOUSE_PRIVS:
                resources.append(Grant(priv=priv, on_warehouse=wh, to=role))

        member_of = config.get("member_of", [])
        for parent_role in member_of:
            resources.append(RoleGrant(role=role, to_role=parent_role))

        database_read = config.get("privileges", {}).get("databases", {}).get("read", [])
        database_write = config.get("privileges", {}).get("databases", {}).get("write", [])

        def _add_database_grants(resources, databases, privs, role):
            for db in databases:
                resources.append(ResourcePointer(name=db, resource_type=ResourceType.DATABASE))
                for priv in privs:
                    resources.append(Grant(priv=priv, on_database=db, to=role))

        _add_database_grants(resources, database_read, DATABASE_READ_PRIVS, role)
        _add_database_grants(resources, database_write, DATABASE_WRITE_PRIVS, role)

        schema_read = config.get("privileges", {}).get("schemas", {}).get("read", [])
        schema_write = config.get("privileges", {}).get("schemas", {}).get("write", [])

        def _add_schema_grants(resources, schema_identifier, privs, role):
            if schema_identifier.endswith(".*"):
                database = _parse_permifrost_identifier(schema_identifier, is_db_scoped=True).database
                for priv in privs:
                    resources.append(FutureGrant(priv=priv, on_future_schemas_in_database=database, to=role))
            else:
                resources.append(ResourcePointer(name=schema_identifier, resource_type=ResourceType.SCHEMA))
                for priv in privs:
                    resources.append(Grant(priv=priv, on_schema=schema_identifier, to=role))

        for schema in schema_read:
            _add_schema_grants(resources, schema, SCHEMA_READ_PRIVS, role)
        for schema in schema_write:
            _add_schema_grants(resources, schema, SCHEMA_WRITE_PRIVS, role)

        # TODO: tables
        # TODO: owns

    return resources


def _get_user_resources(users: list):
    resources = []
    for permifrost_user in users:
        user, config = permifrost_user.popitem()
        resources.append(ResourcePointer(name=user, resource_type=ResourceType.USER))

        member_of = config.get("member_of", [])
        for role in member_of:
            resources.append(RoleGrant(role=role, to_user=user))

    return resources