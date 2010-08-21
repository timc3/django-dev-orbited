"""
Run Django in a twisted proxy environment,
starts Orbited on /tcp and also the MorbidQ stomp
server.

Useful for development with other systems.

NOT FOR PRODUCTION USE.

Change "djangoproject." to the path of your django project.

twistd -ny server.py
"""

from twisted.web import static, resource, server
from twisted.application import internet, service

from morbid import StompFactory

# Config
from orbited import logging, config
logging.setup(config.map)
INTERFACE = "localhost"

config.map["[access]"]={(INTERFACE, 61613):"*"}
PORT = 8000
STOMP_PORT = 61613

from orbited import cometsession
from orbited import proxy

#WSGI for DjangoProject
from djangoproject.twisted_wsgi import get_root_resource

#Twisted Application setup:
application = service.Application('portal')
serviceCollection = service.IServiceCollection(application)

# Django and static file server:
root_resource = get_root_resource()
root_resource.putChild("static", static.File("static"))
http_factory = server.Site(root_resource, logPath="http.log")
internet.TCPServer(PORT, http_factory, interface=INTERFACE).setServiceParent(serviceCollection)

# Orbited server -served from /tcp:
proxy_factory = proxy.ProxyFactory()
internet.GenericServer(cometsession.Port, factory=proxy_factory, resource=root_resource, childName="tcp", interface=INTERFACE).setServiceParent(serviceCollection)

# Stomp server:
internet.TCPServer(STOMP_PORT, StompFactory(), interface=INTERFACE).setServiceParent(serviceCollection)

