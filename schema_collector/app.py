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
