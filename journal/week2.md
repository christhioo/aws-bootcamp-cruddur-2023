# Week 2 — Distributed Tracing

## Required Homework/Tasks

### Instrument Honeycomb with OTEL

1. Create an account on honeycomb.io.
2. Launch a new workspace on gitpod.io.
3. Add the following env variables to `backend-flask` services/environment in `docker-compose.yml`.

   ```yml
   OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
   OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
   OTEL_SERVICE_NAME: "backend-flask"
   ```
4. Go to honeycomb account and create a new environment. In the screenshot below, I create a new environment called "AWS Bootcamp".
   ![Honeycomb Environment](assets2/week-2/honeycomb-env.png)
   
5. Once it's created, go to the Settings and find its API keys.
   ![Honeycomb API Keys](assets2/week-2/honeycomb-api-keys.png)
  
6. Add the API keys to gitpod environment with the following commands.

   ```sh
   export HONEYCOMB_API_KEY=""
   export HONEYCOMB_SERVICE_NAME="Cruddur"
   gp env HONEYCOMB_API_KEY=""
   gp env HONEYCOMB_SERVICE_NAME="Cruddur"
   ```
7. Append the following files to `backend-flask / requirements.txt`.  
   *(Reference: https://docs.honeycomb.io/getting-data-in/opentelemetry/python/)*
   
   ```sh
   opentelemetry-api 
   opentelemetry-sdk 
   opentelemetry-exporter-otlp-proto-http 
   opentelemetry-instrumentation-flask 
   opentelemetry-instrumentation-requests
   ```
8. Install the dependencies.
   
   ```sh
   pip install -r requirements.txt
   ```
9. Initiliase a tracer and Flask instrumentation to send data to Honeycomb in `app.py`.
   
   ```py
   from opentelemetry import trace
   from opentelemetry.instrumentation.flask import FlaskInstrumentor
   from opentelemetry.instrumentation.requests import RequestsInstrumentor
   from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import BatchSpanProcessor
   ```
   
   ```py
   # HoneyComb -------------
   # Initialize tracing and an exporter that can send data to Honeycomb
   provider = TracerProvider()
   processor = BatchSpanProcessor(OTLPSpanExporter())
   provider.add_span_processor(processor)
   trace.set_tracer_provider(provider)
   tracer = trace.get_tracer(__name__)
   ```
   
   ```py
   # HoneyComb -------------
   # Initialize automatic instrumentation with Flask
   FlaskInstrumentor().instrument_app(app)
   RequestsInstrumentor().instrument()
   ```
   
   ![app.py](assets2/week-2/app-py.png)
10. As tracer has been configured, we can create spans to describe what is happening in your application.
    Add the following lines in `home_activities.py`.
    
    ```py
    from opentelemetry import trace
    
    tracer = trace.get_tracer("home.activities")
    class HomeActivities:
    def run():
      with tracer.start_as_current_span("home-activities-mock-data"):
        span = trace.get_current_span()
        now = datetime.now(timezone.utc).astimezone()
        span.set_attribute("app.now", now.isoformat())
        ...
        span.set_attribute("app.result_length", len(results))
        return results
    ```
11. Run docker compose up.
12. Open backend-flask from gitpod.io and hit `/api/activities/home`.

    ![backend-flask](assets2/week-2/backend-result.png)
13. Once it has returned json data, navigate to honeycomb.io and click on the recent trace.

    ![Honeycomb Recent Traces](assets2/week-2/honeycomb-recent-traces.png)
14. The attributes should be reflected on the right side bar.
    
    ![Honeycomb Trace Details](assets2/week-2/honeycomb-trace-details.png)

### Instrument AWS X-Ray

1. Add AWS X-Ray SDK for Python to `backend-flask/requirements.txt`.  
   *(Reference: https://github.com/aws/aws-xray-sdk-python)*
   
   ```txt
   aws-xray-sdk
   ```
2. Install python dependencies.

   ```sh
   pip install -r requirements.txt
   ```
3. Import the library to the `app.py`.

   ```py
   from aws_xray_sdk.core import xray_recorder
   from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

   xray_url = os.getenv("AWS_XRAY_URL")
   xray_recorder.configure(service='Cruddur', dynamic_naming=xray_url)
   
   app = Flask(__name__)
   
   XRayMiddleware(app, xray_recorder)
   ```
4. Add Daemon Service to `docker-compose.yml`.

   ```yml
   xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "us-east-1"
    command:
      - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
   ```
5. Add these two environment variables to backend-flask in `docker-compose.yml` file.

   ```yml
   AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*"
   AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
   ```
6. Create a new X-Ray group.
   
   ```sh
   aws xray create-group \
      --group-name "Cruddur" \
      --filter-expression "service(\"backend-flask\")"
   ```
   
   ![X-Ray Group](assets2/week-2/x-ray-group.png)
7. Create a new sampling rule file in `aws/json/xray.json`.

   ```json
   {
     "SamplingRule": {
         "RuleName": "Cruddur",
         "ResourceARN": "*",
         "Priority": 9000,
         "FixedRate": 0.1,
         "ReservoirSize": 5,
         "ServiceName": "Cruddur",
         "ServiceType": "*",
         "Host": "*",
         "HTTPMethod": "*",
         "URLPath": "*",
         "Version": 1
     }
   }
   ```
8. Create a new sampling rule for AWS X-Ray traces.

   ```sh
   aws xray create-sampling-rule --cli-input-json file://aws/json/xray.json
   ```
   
   ![X-Ray Sampling Rule](assets2/week-2/x-ray-sampling-rules.png)
9. Run docker compose up.
10. Hit `/api/activities/home`.
11. The trace should be reflected on AWS X-Ray traces.

    ![X-Ray Traces](assets2/week-2/x-ray-trace.png)
    
    ![X-Ray Trace Timeline](assets2/week-2/x-ray-segments-timeline.png)
12. Add subsegment into `message_groups.py`.

    ```py
    subsegment = xray_recorder.begin_subsegment('first_mock_subsegment')
    
    ...
    
    dict = {
      "now": now.isoformat(),
      "size": len(model['data'])
    }
    subsegment.put_metadata('key', dict, 'namespace')
    xray_recorder.end_subsegment()
    ```
13. Hit `/api/message_groups`.
14. Check AWS X-Ray traces.

    ![X-Ray Subsegment](assets2/week-2/x-ray-subsegment-metadata.png)  

### Configure custom logger to send to CloudWatch Logs

1. Add Watchtower for Python to `backend-flask/requirements.txt`.  
   *(Reference: https://pypi.org/project/watchtower/)*
   
   ```txt
   watchtower
   ```
2. Install python dependencies.

   ```sh
   pip install -r requirements.txt
   ```
3. Add the following commands into `app.py`.

   ```py
   import watchtower
   import logging
   from time import strftime
   ```
   
   ```py
   # Configuring Logger to Use CloudWatch
   LOGGER = logging.getLogger(__name__)
   LOGGER.setLevel(logging.DEBUG)
   console_handler = logging.StreamHandler()
   cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
   LOGGER.addHandler(console_handler)
   LOGGER.addHandler(cw_handler)
   LOGGER.info("test message christhio")
   ```
   
   ```py
   @app.after_request
   def after_request(response):
       timestamp = strftime('[%Y-%b-%d %H:%M]')
       LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
       return response
   ```
4. Add the parameter to `/api/activities/home` in `app.py`.

   ```py
   @app.route("/api/activities/home", methods=['GET'])
   def data_home():
     data = HomeActivities.run(logger=LOGGER)
   ```
5. Add the parameter `logger` to `home_activities.py`.

   ```py
   class HomeActivities:
     def run(logger):
         logger.info('Hello Cloudwatch! Christhio from /api/activities/home')
   ```
6. Set these three environment variables to backend-flask in `docker-compose.yml` file.

   ```yml
   AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
   AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
   AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
   ```
7. Run docker compose up.
8. Hit `/api/activities/home`.
9. Check CloudWatch's log groups.

   ![CloudWatch Log Groups](assets2/week-2/cloudwatch-log-group.png)
10. Check CloudWatch's log streams.

    ![CloudWatch Log Streams](assets2/week-2/cloudwatch-log-streams.png)
11. Check CloudWatch's log events.

    ![CloudWatch Log Events](assets2/week-2/cloudwatch-log-events.png)

### Integrate Rollbar and capture and error

1. Create a new Rollbar account.
2. Create a new project called Cruddur.
3. Select 'Flask' as the SDK.

   ![Rollbar Select SDK](assets2/week-2/rollbar-select-sdk.png)
4. Copy access token from code snippet into notepad.

   ![Rollbar Access Token](assets2/week-2/rollbar-access-token.png)
5. Add blinker and rollbar to `backend-flask/requirements.txt`.

   ```txt
   blinker
   rollbar
   ```
6. Install python dependencies.

   ```sh
   pip install -r requirements.txt
   ```
7. Set access token from step (4).

   ```sh
   export ROLLBAR_ACCESS_TOKEN=""
   gp env ROLLBAR_ACCESS_TOKEN=""
   ```
8. Set the following environment variable to backend-flask in `docker-compose.yml` file.

   ```yml
   ROLLBAR_ACCESS_TOKEN: "${ROLLBAR_ACCESS_TOKEN}"
   ```
9. Add the following commands into `app.py`.

   ```py
   import rollbar
   import rollbar.contrib.flask
   from flask import got_request_exception
   ```
   
   ```py
   rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
   @app.before_first_request
   def init_rollbar():
       """init rollbar module"""
       rollbar.init(
           # access token
           rollbar_access_token,
           # environment name
           'production',
           # server root directory, makes tracebacks prettier
           root=os.path.dirname(os.path.realpath(__file__)),
           # flask already sets up logging
           allow_logging_basic_config=False)

       # send exceptions from `app` to rollbar, using flask's signal system.
       got_request_exception.connect(rollbar.contrib.flask.report_exception, app)
   ```
10. Create a new endpoint to test rollbar in `app.py`.
    
    ```py
    @app.route('/rollbar/test')
    def rollbar_test():
       rollbar.report_message('Hello World Christhio!', 'warning')
       return "Hello World!"
    ```
11. Run docker compose up.
12. Hit `/rollbar/test`.
13. Check Rollbar's dashboard.

      ![Rollbar Dashboard](assets2/week-2/rollbar-dashboard.png)
14. Delete return statement in `home_activities.py`.  
15. Hit `/api/activities/home`.  
16. Check Rollbar's dashboard.
     ![Rollbar Error](assets2/week-2/rollbar-error.png)
17. Error message should be displayed.
     ![Rollbar Error Details](assets2/week-2/rollbar-error-details.png)
    
