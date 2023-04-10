from werkzeug.wrappers import Request
from flask import request
from lib.cognito_jwt_token import CognitoJwtToken, extract_access_token, TokenVerifyError
import os

class JWTMiddleware:
	def __init__(self, app):
		self.app = app
		self.cognito_jwt_token = CognitoJwtToken(
			user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"), 
			user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"),
			region=os.getenv("AWS_DEFAULT_REGION")
		)

	def __call__(self, environ, start_response):
		request = Request(environ)
		try:
			access_token = extract_access_token(request.headers)			
			claims = self.cognito_jwt_token.verify(access_token)			
		except TokenVerifyError:
			self.cognito_jwt_token.claims = {'username': None, 'sub': None}

		return self.app(environ, start_response)