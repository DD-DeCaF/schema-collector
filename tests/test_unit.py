# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability, DTU.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
