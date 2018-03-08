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

from aiohttp import web
import os
import asyncio
import aiohttp_cors
from venom import Empty
from venom.rpc import Service, Venom, Stub
from venom.rpc.comms.aiohttp import create_app, Client
from venom.rpc.method import http
from venom.rpc.reflect.openapi import make_openapi_schema
from venom.rpc.reflect.service import ReflectService
from venom.rpc.reflect.stubs import OpenAPISchema, InfoMessage, ReflectStub, \
    TagMessage

from .middleware import raven_middleware


def collect_schemas(current, *schemas):
    return OpenAPISchema(
        swagger='2.0',
        consumes=['application/json'],
        produces=['application/json'],
        schemes=['https'],
        host=os.environ.get('HOST'),
        base_path=os.environ.get('BASE_URL'),
        tags=[t for s in schemas for t in s.tags] +
             [TagMessage(
                 name=f'{s.info.title}-{s.info.version}',
                 description=f'{s.info.description}'
             ) for s in schemas],
        info=InfoMessage(
            version=current.info.version,
            title=current.info.title,
            description='Collected from: ' + ', '.join([
                f'{s.info.title}: {s.info.version}' for s in schemas
            ])
        ),
        paths=tag_paths(schemas),
        definitions={k: v for s in schemas for k, v in s.definitions.items()},
    )


def tag_paths(schemas):
    for s in schemas:
        for url, value in s.paths.items():
            for method, m in value.items():
                if url == '/openapi.json':
                    m.tags.append('OpenAPI')
                else:
                    m.tags.append(f'{s.info.title}-{s.info.version}')
    return {k: v for s in schemas for k, v in s.paths.items()}


class SchemaCollectorStub(Stub):
    @http.GET('/openapi.json')
    def get_openapi_schema(self) -> OpenAPISchema:
        raise NotImplementedError()


async def fetch_schema(url):
    client = Client(ReflectStub, url)
    return await client.get_openapi_schema(Empty())


class SchemaCollectorService(Service):
    class Meta:
        name = 'schema'
        stub = SchemaCollectorStub

    @http.GET('/openapi.json')
    async def get_openapi_schema(self) -> OpenAPISchema:
        current = make_openapi_schema(
            venom.get_instance(ReflectService).reflect
        )
        schemas = await asyncio.gather(
            *[fetch_schema(url) for url in os.environ['TO_COLLECT'].split(',')]
        )
        return collect_schemas(current, *schemas)


venom = Venom()
venom.add(SchemaCollectorService)
venom.add(ReflectService)

app = create_app(venom, web.Application(middlewares=[raven_middleware]))

# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

# Configure CORS on all routes.
for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    web.run_app(app)
