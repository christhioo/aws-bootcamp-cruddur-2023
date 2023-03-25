from datetime import datetime, timedelta, timezone
from opentelemetry import trace
from lib.db import db

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(cognito_user_id=None):
    # logger.info('Hello Cloudwatch! Christhio from /api/activities/home')
    with tracer.start_as_current_span("home-activities-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      
      sql = db.template('activities','home')      
      results = db.query_array_json(sql)
      print("CHRISTHIO---")
      print(results)
      span.set_attribute("app.result_length", len(results))
      return results