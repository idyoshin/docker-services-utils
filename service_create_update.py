import asyncio
from aiohttp import web
from subprocess import call
import base64
import uuid
import os
import socket
import sys

import docker


docker_client = docker.DockerClient(base_url='unix:///var/run/docker.sock')

def create_service(service_request):
    print('creating service using ', service_request, file=sys.stderr)
    
    docker_client.services.create(image=service_request['image'],
                          name=service_request['name'],
                          hostname=service_request['hostname'],
                          mounts=service_request['mounts'],
                          networks=service_request['networks'])

    print('finished creating service', file=sys.stderr)
    return {'status': 'created'}


def update_service(service, service_request):
    print('updating service', file=sys.stderr)
    print(service, file=sys.stderr)
    print('updating service ', service_request, file=sys.stderr)

    service.update(image=service_request['image'],
                   name=service_request['name'],
                   hostname=service_request['hostname'],
                   mounts=service_request['mounts'],
                   networks=service_request['networks'])

    print('finished updating service', file=sys.stderr)
    return {'status': 'updated'}




async def handle_service(request):
    print('got request in handle_service', request, file=sys.stderr)
    service_request = await request.json()
    print('performing update or create of the services ', service_request, file=sys.stderr)
    services = docker_client.services.list(filters={'name': service_request['name']})
    if services :
        return web.json_response(update_service(services[0], service_request))
    else:
        return web.json_response(create_service(service_request))



loop = asyncio.get_event_loop()

port = 6000

app = web.Application()
app.router.add_post("/service", handle_service)

if __name__ == '__main__':
    handler = app.make_handler()
    srv = loop.run_until_complete(loop.create_server(handler, '0.0.0.0', port))
    loop.run_forever()
