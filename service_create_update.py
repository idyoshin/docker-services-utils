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


def remove_service(service) :
    print('removing service', service, file=sys.stderr)
    service.remove()
    print('finished removing service', file=sys.stderr)
    return {'status': 'removed'}



async def handle_service(request):
    print('got request in handle_service', request, file=sys.stderr)
    service_request = await request.json()
    if 'mounts' not in service_request : 
        service_request['mounts'] = None

    if 'networks' not in service_request :
        service_request['networks'] = None

    if 'hostname' not in service_request :
        service_request['hostname'] = None

    print('performing update or create of the services ', service_request, file=sys.stderr)
    services = docker_client.services.list(filters={'name': service_request['name']})
    if services :
        return web.json_response(update_service(services[0], service_request))
    else:
        return web.json_response(create_service(service_request))



async def handle_delete_service(request): 
    print('got remove service request', request, file=sys.stderr)
    service_request = await request.json()
    services = docker_client.services.list(filters={'name': service_request['name']})
    if services :
        return web.json_response(remove_service(services[0]))
    else:
        return web.json_response({'status': 'service not found'})





async def handle_create_network(request):
    print("creating network", request, file=sys.stderr)
    service_request = await request.json()
    networks = docker_client.networks.list(filters={'name', service_request['name']})
    if networks : 
        return web.json_response({'status': 'already present'})
    else:
        docker_client.networks.create(name = service_request['name'])
        return web.json_response({'status': 'created'})



async def handle_remove_network(request) :
    print('removing network', request, file=sys.stderr)
    service_request = await request.json()
    networks = docker_client.networks.list(filters={'name', service_request['name']})
    if networks : 
        for cont in networks[0].containers:
            networks[0].disconnect(cont)
        networks[0].remove()
        return web.json_response({'status': 'disconnected and removed'})
    else:
        return web.json_response({'status': 'not present'})
    


loop = asyncio.get_event_loop()

port = 6000

app = web.Application()
app.router.add_post("/service", handle_service)
app.router.add_post("/service/remove", handle_delete_service)

app.router.add_post("/network", handle_create_network)
app.router.add_post("/network/remove", handle_remove_network)

if __name__ == '__main__':
    handler = app.make_handler()
    srv = loop.run_until_complete(loop.create_server(handler, '0.0.0.0', port))
    loop.run_forever()
