from aiohttp import web
import os
import asyncio
from venom import Empty
from venom.rpc import Service, Venom, Stub
from venom.rpc.comms.aiohttp import create_app, Client
from venom.rpc.method import http
from venom.rpc.reflect.openapi import make_openapi_schema
from venom.rpc.reflect.service import ReflectService
from venom.rpc.reflect.stubs import OpenAPISchema, InfoMessage, \
    OperationMessage, ResponseMessage, ResponsesMessage, \
    ParameterMessage, SchemaMessage, ReflectStub

schema1 = OpenAPISchema(swagger='2.0', consumes=['application/json'], produces=['application/json'], info=InfoMessage(version='1.0.0', title='API'), paths={'/pets/pet': {'post': OperationMessage(responses=ResponsesMessage(default=ResponseMessage(description='Post the pet with body params', schema=SchemaMessage(ref='#/definitions/Pet'))), parameters=[ParameterMessage(is_in='body', name='Pet', schema=SchemaMessage(ref='#/definitions/Pet'))]), 'get': OperationMessage(responses=ResponsesMessage(default=ResponseMessage(description='Get the pet with query arguments', schema=SchemaMessage(ref='#/definitions/Pet'))), parameters=[ParameterMessage(is_in='query', name='tag', type='string'), ParameterMessage(is_in='query', name='name', type='string'), ParameterMessage(is_in='query', name='id', type='integer')])}, '/pets/pet/{id}': {'get': OperationMessage(responses=ResponsesMessage(default=ResponseMessage(description='Get the pet', schema=SchemaMessage(ref='#/definitions/Pet'))), parameters=[ParameterMessage(is_in='path', required=True, name='id', type='integer'), ParameterMessage(is_in='query', name='tag', type='string'), ParameterMessage(is_in='query', name='name', type='string')]), 'post': OperationMessage(responses=ResponsesMessage(default=ResponseMessage(description='Post the pet with path id', schema=SchemaMessage(ref='#/definitions/Pet'))), parameters=[ParameterMessage(is_in='body', name='create_pet_body', schema=SchemaMessage(type='object', properties={'tag': SchemaMessage(type='string'), 'name': SchemaMessage(type='string')})), ParameterMessage(is_in='path', required=True, name='id', type='integer')])}}, definitions={'Pet': SchemaMessage(type='object', properties={'id': SchemaMessage(type='integer'), 'name': SchemaMessage(type='string'), 'tag': SchemaMessage(type='string')})})

schema2 = OpenAPISchema(swagger='2.0', consumes=['application/json'], produces=['application/json'], info=InfoMessage(version='1.0.0', title='API'), paths={'/petservice/pet/{id}': {'get': OperationMessage(responses=ResponsesMessage(default=ResponseMessage(schema=SchemaMessage(ref='#/definitions/PetSimple'))), parameters=[ParameterMessage(is_in='path', required=True, name='id', type='integer')])}, '/petservice/pet': {'post': OperationMessage(responses=ResponsesMessage(default=ResponseMessage(schema=SchemaMessage(ref='#/definitions/PetSimple'))), parameters=[ParameterMessage(is_in='body', name='PetSimple', schema=SchemaMessage(ref='#/definitions/PetSimple'))])}}, definitions={'PetSimple': SchemaMessage(type='object', properties={'id': SchemaMessage(type='integer')})})


def collect_schemas(current, *schemas):
    return OpenAPISchema(
        swagger='2.0',
        consumes=['application/json'],
        produces=['application/json'],
        info=InfoMessage(
            version=current.info.version,
            title=current.info.title,
            description='Collected from: ' + ', '.join([
                f'{s.info.title}: {s.info.version}' for s in schemas
            ])
        ),
        paths={k: v for s in schemas for k, v in s.paths.items()},
        definitions={k: v for s in schemas for k, v in s.definitions.items()},
    )

class SchemaCollectorStub(Stub):

    @http.GET('/openapi.json')
    def get_openapi_schema(self) -> OpenAPISchema:
        raise NotImplementedError()


async def fetch_schema(url):
    client = Client(ReflectStub, url)
    return await client.invoke(ReflectStub.get_openapi_schema, Empty())

class SchemaCollectorService(Service):
    class Meta:
        name = 'schema'
        stub = SchemaCollectorStub

    @http.GET('./openapi.json')
    async def get_openapi_schema(self) -> OpenAPISchema:
        current = make_openapi_schema(venom.get_instance(ReflectService).reflect)
        schemas = await asyncio.gather(*[fetch_schema(url) for url in os.environ['TO_COLLECT'].split(',')])
        return collect_schemas(current, *schemas)


venom = Venom()
venom.add(SchemaCollectorService)
venom.add(ReflectService)

app = create_app(venom)

if __name__ == '__main__':
    web.run_app(app)
