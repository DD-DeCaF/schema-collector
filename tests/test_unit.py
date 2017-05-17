from schema_collector.app import collect_schemas
from venom.rpc.reflect.stubs import OpenAPISchema, InfoMessage, \
    OperationMessage, SchemaMessage, TagMessage

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
    tags=[TagMessage(name='pet')],
    info=InfoMessage(
        title='Second',
        version='2.2.2',
    ),
    paths={
        'b': {'get': OperationMessage(tags=['pet'])},
        'c': {'post': OperationMessage()},
    },
    definitions={
        'l': SchemaMessage(),
        's': SchemaMessage(),
    }
)


def test_collect_schema():
    schema = collect_schemas(current_schema, schema1, schema2)
    assert schema.info.description == \
           'Collected from: First: 1.1.1, Second: 2.2.2'
    assert set(schema.paths.keys()) == {'a', 'b', 'c'}
    assert set(schema.paths['b'].keys()) == {'get'}
    assert set(schema.definitions.keys()) == {'m', 'n', 'l', 's'}
    assert list(schema.tags) == [
        TagMessage(name='pet'),
        TagMessage(name='First-1.1.1', description=''),
        TagMessage(name='Second-2.2.2', description='')
    ]
    assert list(schema.paths['a']['get'].tags) == ['First-1.1.1']
    assert list(schema.paths['b']['get'].tags) == ['pet', 'Second-2.2.2']
