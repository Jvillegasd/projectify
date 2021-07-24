import jwt
import datetime
from environs import Env
from flask import request, Blueprint, jsonify, abort
from middlewares.schemas import parameters
from modules.users.serializers import CreateUserSchema, AuthTokenSchema
from modules.users.models import User

env = Env()
env.read_env()
JWT_KEY = env("SECRET_KEY")

user_blueprint = Blueprint('User controller', __name__)

@user_blueprint.route('/', methods=['POST'])
@parameters(schema=CreateUserSchema())
def create():
  new_user = User(**request.get_json())
  new_user.save()
  return jsonify({ 'message': 'user created' }), 200

@user_blueprint.route('/token', methods=['POST'])
@parameters(schema=AuthTokenSchema())
def get_token():
  body = request.get_json()

  db_user = User.objects.get(username=body['username'])
  if db_user and db_user.check_password(body['password']):
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)
    auth_token = jwt.encode({
      'sub': db_user.username,
      'exp': expiration_date,
      'iat': datetime.datetime.now(),
    }, JWT_KEY)

    return jsonify({ 'token': f'Bearer {auth_token}' }), 200
  else:
    abort(400, 'bad credentials')
