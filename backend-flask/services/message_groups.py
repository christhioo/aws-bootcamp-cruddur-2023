from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder

class MessageGroups:
  def run(user_handle):
    model = {
      'errors': None,
      'data': None
    }

    # X-Ray -------
    subsegment = xray_recorder.begin_subsegment('first_mock_subsegment')
    
    now = datetime.now(timezone.utc).astimezone()
    results = [
      {
        'uuid': '24b95582-9e7b-4e0a-9ad1-639773ab7552',
        'display_name': 'Andrew Brown',
        'handle':  'andrewbrown',
        'created_at': now.isoformat()
      },
      {
        'uuid': '417c360e-c4e6-4fce-873b-d2d71469b4ac',
        'display_name': 'Worf',
        'handle':  'worf',
        'created_at': now.isoformat()
    }]
    
    model['data'] = results

    # X-Ray -------
    dict = {
      "now": now.isoformat(),
      "size": len(model['data'])
    }
    subsegment.put_metadata('key', dict, 'namespace')
    xray_recorder.end_subsegment()

    return model