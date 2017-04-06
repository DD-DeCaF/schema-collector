from venom.rpc.reflect.stubs import OpenAPISchema
from schema_collector.app import collect_schemas


def test_collect_schema():
    schema = OpenAPISchema(
        swagger='2.0',
        consumes=['application/json'],
        produces=['application/json'],
    )
    assert collect_schemas([]) == schema