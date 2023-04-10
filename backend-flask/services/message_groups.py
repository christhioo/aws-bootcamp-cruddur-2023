from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder

from lib.ddb import Ddb
from lib.db import db

class MessageGroups:
  def run(cognito_user_id):
    model = {
      'errors': None,
      'data': None
    }

    # X-Ray -------
    # subsegment = xray_recorder.begin_subsegment('first_mock_subsegment')
    
    sql = db.template('users','uuid_from_cognito_user_id')
    my_user_uuid = db.query_value(sql,{
      'cognito_user_id': cognito_user_id
    })

    print(f"UUID: {my_user_uuid}")

    ddb = Ddb.client()
    data = Ddb.list_message_groups(ddb, my_user_uuid)
    print("list_message_groups:",data)

    model['data'] = data

    # X-Ray -------
    # dict = {
    #   "now": now.isoformat(),
    #   "size": len(model['data'])
    # }
    # subsegment.put_metadata('key', dict, 'namespace')
    # xray_recorder.end_subsegment()

    return model