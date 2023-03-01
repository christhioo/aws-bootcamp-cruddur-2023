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
7. Append the following files to `backend-flask / requirements.txt`. <br />
   (Reference: https://docs.honeycomb.io/getting-data-in/opentelemetry/python/)
   
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

### Configure custom logger to send to CloudWatch Logs

### Integrate Rollbar and capture and error
