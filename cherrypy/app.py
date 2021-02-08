#!/usr/bin/python

__requires__ = ['cherrypy', 'social-auth-core', 'pacifica-auth']

import os
from sys import argv as sys_argv
import uuid
import configparser
import functools
import requests
import cherrypy
from sqlalchemy.engine import create_engine
from social_core.actions import do_auth, do_complete
from social_cherrypy.utils import load_backend, load_strategy, setting_name, module_member
from pacifica.auth import auth_session, error_page_default, quickstart
from pacifica.auth.user_model import User, Base

def local_auth_session(backend=None, redirect_uri=None):
	def do_login(backend, user, social_user):
		backend.strategy.session_set('user_id', user.id)
	def decorator(func):
		"""Authenticate the method."""
		@functools.wraps(func)
		def wrapper(self, *args, **kwargs):
			"""Internal wrapper method."""
			if not getattr(cherrypy.request, 'user', None):
				strategy = load_strategy()
				objbackend = load_backend(strategy, backend, redirect_uri)
				if 'authorization' in cherrypy.request.headers:
					return do_complete(objbackend, do_login, *args, **kwargs)
					"""
					resp = requests.get(
						self.config.get('social_settings', '{}_userinfo_url'.format(backend)),
						headers={
							'Authorization': cherrypy.request.headers.get('authorization'),
							'Accept': 'application/json',
						}
					)
					print(resp.status_code)
					print(resp.headers)
					print(resp.content)
					jwt_obj = objbackend.get_user_details(objbackend.user_data(resp.content))
				
					print(jwt_obj)
					print(strategy.get_user(**jwt_obj))
					#objbackend.strategy.session_set('user_id', strategy.get_user(**jwt_obj))
					"""
				return do_auth(objbackend)
			return func(self, *args, **kwargs)
		return wrapper
	return decorator

class ExampleApi:
	exposed = True

	def __init__(self, config):
		self.config = config

	@cherrypy.tools.json_out()
	@local_auth_session('keycloak', '/')
	def GET(self):
		return { "uuid": str(uuid.uuid4()) }

	def OPTIONS(self):
		pass

@cherrypy.tools.register('before_finalize', priority=60)
def secureheaders():
    headers = cherrypy.response.headers
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Headers'] = 'Authorization,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type'

class Server:
	@staticmethod
	def run():
		quickstart(
			sys_argv[1:],
			'Run the example server.',
			User,
			'pacifica.auth.user_model.User',
			os.path.dirname(__file__),
			_mount_config
		)


def _mount_config(config: configparser.ConfigParser):
    engine = create_engine(config.get('database', 'db_url'))
    Base.metadata.create_all(engine)
    cherrypy.config.update({
        'SOCIAL_AUTH_USER_MODEL': 'pacifica.auth.user_model.User',
		'SOCIAL_AUTH_REDIRECT_IS_HTTPS': True,
    })
    # this needs to be imported after cherrypy settings are applied.
    # pylint: disable=import-outside-toplevel
    from social_cherrypy.models import SocialBase
    SocialBase.metadata.create_all(engine)
    common_config = {
        '/': {
			'tools.secureheaders.on': True,
            'error_page.default': error_page_default,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
		'/swagger.yaml': {
			'tools.secureheaders.on': True,
			'tools.staticfile.on': True,
			'tools.staticfile.filename': '/app/swagger.yaml',
		},
		'/root.crt': {
			'tools.secureheaders.on': True,
			'tools.staticfile.on': True,
			'tools.staticfile.filename': '/certdata/pacifica_root_ca.io.crt',
		}

    }
    cherrypy.tree.mount(ExampleApi(config), '/v1', config=common_config)

__name__ == '__main__' and Server.run()
