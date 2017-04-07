from schema_collector.app import collect_schemas
from venom.rpc.reflect.stubs import OpenAPISchema, InfoMessage, \
    OperationMessage, SchemaMessage


def test_collect_schema():
    current_schema = OpenAPISchema(
        info=InfoMessage(
            title='API',
            version='3.1.4',
        ),
    )
    schema1 = OpenAPISchema(
        swagger='2.0',
        consumes=['application/json'],
        produces=['application/json'],
        info=InfoMessage(
            title='First',
            version='1.1.1',
        ),
        paths={
            'a': {'get': OperationMessage()},
            'b': {'post': OperationMessage()},
        },
        definitions={
            'm': SchemaMessage(),
            'n': SchemaMessage(),
        }
    )
    schema2 = OpenAPISchema(
        swagger='2.0',
        consumes=['application/json'],
        produces=['application/json'],
        info=InfoMessage(
            title='Second',
            version='2.2.2',
        ),
        paths={
            'b': {'get': OperationMessage()},
            'c': {'post': OperationMessage()},
        },
        definitions={
            'l': SchemaMessage(),
            's': SchemaMessage(),
        }
    )
    schema = collect_schemas(current_schema, schema1, schema2)
    assert schema.info.description == \
           'Collected from: First: 1.1.1, Second: 2.2.2'
    assert set(schema.paths.keys()) == {'a', 'b', 'c'}
    assert set(schema.paths['b'].keys()) == {'get'}
    assert set(schema.definitions.keys()) == {'m', 'n', 'l', 's'}
