# Week 4 — Postgres and RDS

[Required Homework/Tasks](#required-homeworktasks)
- [Create RDS Postgres Instance (via CLI)](#create-rds-postgres-instance-via-cli)
- [Create Schema for Postgres](#create-schema-for-postgres)
- [Bash scripting for common database actions](#bash-scripting-for-common-database-actions)
  - [Shell Script to Connect to DB](#shell-script-to-connect-to-db)
  - [Shell Script to Drop the Database](#shell-script-to-drop-the-database)
  - [Shell Script to Create the Database](#shell-script-to-create-the-database)
  - [Shell Script to Load the Schema](#shell-script-to-load-the-schema)
  - [Shell Script to Load the Seed Data](#shell-script-to-load-the-seed-data)
  - [Shell Script to Setup Everything](#shell-script-to-setup-everything)
  - [Make Prints Nicer](#make-prints-nicer)
- [Install Postgres Driver in Backend Application](#install-postgres-driver-in-backend-application)
- [Connect Gitpod to RDS Instance](#connect-gitpod-to-rds-instance)
- [Create Cognito Trigger to Insert User into Database](#create-cognito-trigger-to-insert-user-into-database)
- [Create New Activities with a Database Insert](#create-new-activities-with-a-database-insert)

## Required Homework/Tasks

### Create RDS Postgres Instance (via CLI)

1. To create RDS Postgres Instance, we can run the following commands via CLI on gitpod.

   ```sh
   aws rds create-db-instance \
    --db-instance-identifier cruddur-db-instance \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version  14.6 \
    --master-username cruddurroot \
    --master-user-password xxxxxx \
    --allocated-storage 20 \
    --availability-zone us-east-1a \
    --backup-retention-period 0 \
    --port 5432 \
    --no-multi-az \
    --db-name cruddur \
    --storage-type gp2 \
    --publicly-accessible \
    --storage-encrypted \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --no-deletion-protection
   ```
2. After running the above command, gitpod terminal should return the following screenshot.

   ![Gitpod Terminal](assets2/week-4/rds-instance-cli.png)
3. Verify the result by navigating to Amazon RDS Console.
   
   ![Amazon RDS Database](assets2/week-4/rds-aws-console.png)
4. To connect to the DB instance in AWS, use the following format.

   ```sh
   psql \
     --host=<DB instance endpoint> \
     --port=<port> \
     --username=<master username> \
     --password \
     --dbname=<database name>
   ```
   ```sh
   psql \
     --host=cruddur-db-instance.cwbipomqhh0x.us-east-1.rds.amazonaws.com \
     --port=5432 \
     --username=cruddurroot \
     --password \
     --dbname=cruddur
   ```
   
   > `DB instance endpoint` can be obtained from Amazon RDS Console. 
   > Reference: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToPostgreSQLInstance.html
   
   ![RDS Endpoint](assets2/week-4/rds-aws-endpoint.png)
5. If it's a connection timed out, make sure that network inbound rules accept all IP addresses (0.0.0.0/0) or your own IP address to connect, set from AWS Console.

   ![Security Group](assets2/week-4/security-group-inbound-rules.png)
6. You can test the successful connection by running `\l` command.

   ![Postgres Gitpod Terminal](assets2/week-4/rds-aws-gitpod-terminal.png)

### Create Schema for Postgres

1. Create a new file called `schema.sql` under `aws-bootcamp-cruddur-2023/backend-flask/db`.

   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   DROP TABLE IF EXISTS public.users;
   DROP TABLE IF EXISTS public.activities;


   CREATE TABLE public.users (
     uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
     display_name text NOT NULL,
     handle text NOT NULL,
     email text NOT NULL,
     cognito_user_id text NOT NULL,
     created_at TIMESTAMP default current_timestamp NOT NULL
   );

   CREATE TABLE public.activities (
     uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
     user_uuid UUID NOT NULL,
     message text NOT NULL,
     replies_count integer DEFAULT 0,
     reposts_count integer DEFAULT 0,
     likes_count integer DEFAULT 0,
     reply_to_activity_uuid integer,
     expires_at TIMESTAMP,
     created_at TIMESTAMP default current_timestamp NOT NULL
   );
   ```

### Bash Scripting for Common Database Actions

We need to create a new directory to store all the common bash scripts called `bin`.  
The directory will be under `aws-bootcamp-cruddur-2023/backend-flask/`.

   ```sh
   mkdir /workspace/aws-bootcamp-cruddur-2023/backend-flask/bin
   ```

#### Shell Script to Connect to DB

1. Create a new bash script `bin/db-connect`. 

   ```sh
   #! /usr/bin/bash
   
   if [ "$1" = "prod" ]; then
     echo "Running in production mode"
     URL=$PROD_CONNECTION_URL
   else
     URL=$CONNECTION_URL
   fi

   psql $URL
   ```
2. Set the CONNECTION_URL and PROD_CONNECTION_URL environment variable.

   ```sh
   export CONNECTION_URL="postgresql://postgres:password@127.0.0.1:5432/cruddur"
   gp env CONNECTION_URL="postgresql://postgres:password@127.0.0.1:5432/cruddur"
   
   export PROD_CONNECTION_URL="postgresql://cruddurroot:password@cruddur-db-instance.cwbipomqhh0x.us-east-1.rds.amazonaws.com:5432/cruddur"
   gp env PROD_CONNECTION_URL="postgresql://cruddurroot:password@cruddur-db-instance.cwbipomqhh0x.us-east-1.rds.amazonaws.com:5432/cruddur"
   ```
3. Make the bash script executable.

   ```sh
   chmod u+x bin/db-connect
   ```
4. Execute the script (run from `/backend-flask` directory).

   ```sh
   ./bin/db-connect
   ```
   
   ![db-connect script](assets2/week-4/db-connect.png)
   
#### Shell Script to Drop the Database

1. Create a new bash script `bin/db-drop`.

   ```sh
   #! /usr/bin/bash

   NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
   psql $NO_DB_CONNECTION_URL -c "drop database cruddur;"
   ```
   > Reference for sed: https://askubuntu.com/questions/595269/use-sed-on-a-string-variable-rather-than-a-file
2. Make the bash script executable.

   ```sh
   chmod u+x bin/db-drop
   ```
3. Execute the script (run from `/backend-flask` directory).

   ```sh
   ./bin/db-drop
   ```
   
   ![db-drop script](assets2/week-4/db-drop.png)

#### Shell Script to Create the Database

1. Create a new bash script `bin/db-create`.

   ```sh
   #! /usr/bin/bash

   NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
   psql $NO_DB_CONNECTION_URL -c "create database cruddur;"
   ```
   > Reference for sed: https://askubuntu.com/questions/595269/use-sed-on-a-string-variable-rather-than-a-file
2. Make the bash script executable.

   ```sh
   chmod u+x bin/db-create
   ```
3. Execute the script (run from `/backend-flask` directory).

   ```sh
   ./bin/db-create
   ```
   
   ![db-create script](assets2/week-4/db-create.png)

#### Shell Script to Load the Schema

1. Create a new bash script `bin/db-schema-load`.

   ```sh
   #! /usr/bin/bash

   schema_path="$(realpath .)/db/schema.sql"
   echo $schema_path

   if [ "$1" = "prod" ]; then
     echo "Running in production mode"
     URL=$PROD_CONNECTION_URL
   else
     URL=$CONNECTION_URL
   fi

   psql $URL cruddur < $schema_path
   ```
2. Make the bash script executable.

   ```sh
   chmod u+x bin/db-schema-load
   ```
3. Execute the script (run from `/backend-flask` directory).

   ```sh
   ./bin/db-schema-load
   ```
   
   ![db-schema-load script](assets2/week-4/db-schema-load.png)

#### Shell Script to Load the Seed Data

1. Create a new file called `seed.sql` under `aws-bootcamp-cruddur-2023/backend-flask/db`.

   ```sql
   INSERT INTO public.users (display_name, handle, cognito_user_id)
   VALUES
     ('Christhio Brown', 'christhio' ,'MOCK'),
     ('Chris Bayko', 'bayko' ,'MOCK');

   INSERT INTO public.activities (user_uuid, message, expires_at)
   VALUES
     (
       (SELECT uuid from public.users WHERE users.handle = 'christhio' LIMIT 1),
       'This was imported as seed data!',
       current_timestamp + interval '10 day'
     )
   ```
2. Create a new bash script `bin/db-seed`.

   ```sh
   #! /usr/bin/bash

   seed_path="$(realpath .)/db/seed.sql"
   echo $seed_path

   if [ "$1" = "prod" ]; then
     echo "Running in production mode"
     URL=$PROD_CONNECTION_URL
   else
     URL=$CONNECTION_URL
   fi

   psql $URL cruddur < $seed_path
   ```
3. Make the bash script executable.

   ```sh
   chmod u+x bin/db-seed
   ```
4. Execute the script (run from `/backend-flask` directory).

   ```sh
   ./bin/db-seed
   ```
   
   ![db-seed script](assets2/week-4/db-seed.png)

#### Shell Script to Setup Everything

1. Create a new bash script `bin/db-setup`.

   ```sh
   #! /usr/bin/bash

   bin_path="$(realpath .)/bin"

   source "$bin_path/db-drop"
   source "$bin_path/db-create"
   source "$bin_path/db-schema-load"
   source "$bin_path/db-seed"
   ```
2. Make the bash script executable.

   ```sh
   chmod u+x bin/db-setup
   ```
3. Execute the script (run from `/backend-flask` directory).

   ```sh
   ./bin/db-setup
   ```
   
   ![db-setup script](assets2/week-4/db-setup.png)

#### Make Prints Nicer

Reference: https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"
```

### Install Postgres Driver in Backend Application

1. Create a new file under `backend-flask/lib/db.py` and add the following code.

   ```py
   from psycopg_pool import ConnectionPool
   import os

   def query_wrap_object(template):
     sql = f"""
     (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
     {template}
     ) object_row);
     """
     return sql

   def query_wrap_array(template):
     sql = f"""
     (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
     {template}
     ) array_row);
     """
     return sql

   connection_url = os.getenv("CONNECTION_URL")
   pool = ConnectionPool(connection_url)
   ```
2. Add `psycopg` into `requirements.txt`.

   ```sh
   psycopg[binary]
   psycopg[pool]
   ```
3. Run pip install.

   ```sh
   pip install -r requirements.txt
   ```
4. Set an environment variable in `docker-compose.yml`.

   ```yml
   backend-flask:
      environment:
         CONNECTION_URL: "postgresql://postgres:password@db:5432/cruddur"
   ```
5. Replace mock data with real API call in `home_activities.py`.

   ```py
   from lib.db import pool, query_wrap_array

      sql = query_wrap_array("""
      SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
      """)
      print(sql)
      with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchone()
      results = json[0]
      return results
   ```
6. Run docker compose up.
7. Hit the homepage. It should display the seed data.

   ![Homepage](assets2/week-4/localhost-homepage.png)

### Connect Gitpod to RDS Instance

1. Run the shell script to connect to DB (run from `/backend-flask` directory).

   ```sh
   ./bin/db-connect prod
   ```
   > This is a continuation of [Create RDS Postgres Instance (via CLI)](#create-rds-postgres-instance-via-cli).
2. If it's not successful, the issue might be because of inbound security group rules.
3. Check from Amazon RDS Console the instance's security group rules.

   ![Amazon RDS Console Security Group Rules](assets2/week-4/rds-aws-console-security-group.png)
4. As per screenshot, current security group rules allow all IP addresses to connect to RDS instance. We want to change it so that only specific IP address can connect to it. Click on the security group link.
5. Click Edit inbound rules and copy security group ID.

   ![Security Group Rules](assets2/week-4/security-group-inbound-rules-list.png)
6. Copy the security group rule ID from the row where all IP addresses can connect to this instance (0.0.0.0/0).

   ![Edit Inbound Rules](assets2/week-4/security-group-inbound-rules2.png)
7. Set the security group ID and security group rule ID environment variable.

   ```sh
   export DB_SG_ID="sg-0961a06858a56c988"
   gp env DB_SG_ID="sg-0961a06858a56c988"
   export DB_SG_RULE_ID="sgr-01b6e226615e3c743"
   gp env DB_SG_RULE_ID="sgr-01b6e226615e3c743"
   ```
8. Gitpod IP address can be obtained from the following command.

   ```sh
   GITPOD_IP=$(curl ifconfig.me)
   ```
9. Add the following commands under postgres in `gitpod.yml` so that every time it launches new workspace, the security group rule will be updated.

   ```yml
   name: postgres
   command: |
     export GITPOD_IP=$(curl ifconfig.me)
     source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
   ```
10. Create a new shell script called `rds-update-sg-rule` under `/backend-flask/bin` to modify inbound IP address on security group rules, as new workspace in Gitpod will produce different IP address.

    ```sh
    #! /usr/bin/bash
   
    aws ec2 modify-security-group-rules \
      --group-id $DB_SG_ID \
      --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
    ```
11. Make the bash script executable.

     ```sh
     chmod u+x bin/rds-update-sg-rule
     ```
12. Execute the script from `backend-flask` directory.

    ```sh
    ./bin/rds-update-sg-rule
    ```
13. Check the Amazon RDS Console instance's security group rules. It should be updated with the specific address.

    ![Edit Inbound Rules](assets2/week-4/security-group-inbound-rules3.png)
14. Test the connection by executing the script on step (1).

    ![db-connect aws rds](assets2/week-4/db-connect-aws-rds.png)
    
### Create Cognito Trigger to Insert User into Database

1. Navigate to AWS Lambda console.
2. Create a new function called `cruddur-post-confirmation`.
3. Fill in the form like the screenshot below.

   ![Lambda Create Function Form](assets2/week-4/lambda-create-function.png)
4. Replace the code source with the following code.

   ```py
   import json
   import psycopg2
   import os

   def lambda_handler(event, context):
       user = event['request']['userAttributes']
       print('userAttributes')
       print(user)

       user_display_name  = user['name']
       user_email         = user['email']
       user_handle        = user['preferred_username']
       user_cognito_id    = user['sub']
       try:
         print('entered-try')
         sql = f"""
            INSERT INTO public.users (
             display_name, 
             email,
             handle, 
             cognito_user_id
             ) 
            VALUES(%s,%s,%s,%s)
         """
         print('SQL Statement ----')
         print(sql)
         conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
         cur = conn.cursor()
         params = [
            user_display_name,
            user_email,
            user_handle,
            user_cognito_id
         ]
         cur.execute(sql, *params)
         conn.commit() 

       except (Exception, psycopg2.DatabaseError) as error:
         print(error)
       finally:
         if conn is not None:
             cur.close()
             conn.close()
             print('Database connection closed.')
       return event
   ```
5. Click Deploy.

   ![Lambda Code Source](assets2/week-4/lambda-code-source.png)
6. Add a new environment variable under `Configuration` tab.

   ```
   Key: CONNECTION_URL
   Value: postgresql://cruddurroot:PASSWORD@cruddur-db-instance.cwbipomqhh0x.us-east-1.rds.amazonaws.com:5432/cruddur
   ```

   ![Lambda Environment Variable](assets2/week-4/lambda-env-variable.png)
7. Add a new layer into the lambda function with the following ARN for postgres driver installation.

   ```
   arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:2
   ```
   
   ![Lambda Add Layer](assets2/week-4/lambda-add-layer.png)
8. Connect lambda to the VPC (Virtual Private Cloud) under `Configuration` tab.

   ![Lambda VPC](assets2/week-4/lambda-vpc.png)
9. Edit the VPC with at least two subnets and default security group.

   ![Lambda Edit VPC](assets2/week-4/lambda-edit-vpc-err.png)
10. Notice in the screenshot above, there's an error "The provided execution role does not have permissions to call CreateNetworkInterface on EC2".  
    To solve this issue, we need to attach new policy to the lambda.  
    Navigate to Permissions under `Execution role` tab.
    
    ![Lambda Execution Role](assets2/week-4/lambda-execution-role.png)
11. Create a new policy under Policies.

    ![IAM Policies](assets2/week-4/iam-policies.png)

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeNetworkInterfaces",
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeInstances",
                "ec2:AttachNetworkInterface"
            ],
            "Resource": "*"
        }]
    }
    ```

    ![IAM Create Policy](assets2/week-4/iam-create-policy.png)
12. Review the policy and create policy.

    ![IAM Review Policy](assets2/week-4/iam-review-policy.png)
13. Attach the newly created policy into the `cruddur-post-confirmation's role`.

    ![Role's Policies](assets2/week-4/lambda-role-add-permission.png)
    
    ![Role's Policies (After)](assets2/week-4/lambda-role-post-add-permission.png)
14. Add lambda trigger in Cognito for `cruddur-user-pool` under `User pool properties` tab.

    ![Lambda Trigger](assets2/week-4/cognito-lambda-trigger.png)

    ![Add Lambda Trigger](assets2/week-4/cognito-add-lambda-trigger.png)
15. Test the newly created lambda function by sign up on cruddur.
16. After filling in confirmation code and confirm email, the lambda function will be triggered and the log can be checked from CloudWatch's Log groups.

    ![Log Events](assets2/week-4/log-events.png)
17. Connect to AWS DB instance from terminal, and list all values from `public.users` table.

    ![List Users' Table](assets2/week-4/db-search-users.png)

### Create New Activities with a Database Insert

1. Create a new SQL file called `create.sql` under `backend-flask/db/sql/activities` directory.

   ```sql
   INSERT INTO public.activities (
      user_uuid,
      message,
      expires_at
   )
   VALUES (
      (SELECT uuid 
        FROM public.users 
        WHERE users.handle = %(handle)s
        LIMIT 1
      ),
      %(message)s,
      %(expires_at)s
   ) RETURNING uuid;
   ```
2. Create a new SQL file called `home.sql` under `backend-flask/db/sql/activities`.

   ```sql
   SELECT
    activities.uuid,
    users.display_name,
    users.handle,
    activities.message,
    activities.replies_count,
    activities.reposts_count,
    activities.likes_count,
    activities.reply_to_activity_uuid,
    activities.expires_at,
    activities.created_at
   FROM public.activities
   LEFT JOIN public.users ON users.uuid = activities.user_uuid
   ORDER BY activities.created_at DESC
   ```
3. Create a new SQL file called `object.sql` under `backend-flask/db/sql/activities`.

   ```sql
   SELECT
     activities.uuid,
     users.display_name,
     users.handle,
     activities.message,
     activities.created_at,
     activities.expires_at
   FROM public.activities
   INNER JOIN public.users 
   ON users.uuid = activities.user_uuid 
   WHERE 
     activities.uuid = %(uuid)s
   ```
4. Replace `backend-flask/lib/db.py` file to be the following codes.

   ```py
    from psycopg_pool import ConnectionPool
    import os
    import re
    import sys
    from flask import current_app as app

    class Db:
      def __init__(self):
        self.init_pool()

      def init_pool(self):
        connection_url = os.getenv("CONNECTION_URL")
        self.pool = ConnectionPool(connection_url)

      def template(self,*args):
        pathing = list((app.root_path,'db','sql',) + args)
        pathing[-1] = pathing[-1] + ".sql"

        template_path = os.path.join(*pathing)

        green = '\033[92m'
        no_color = '\033[0m'
        print("\n")
        print(f'{green} Load SQL Template: {template_path} {no_color}')

        with open(template_path, 'r') as f:
          template_content = f.read()
        return template_content

      def print_params(self,params):
        blue = '\033[94m'
        no_color = '\033[0m'
        print(f'{blue} SQL Params:{no_color}')
        for key, value in params.items():
          print(key, ":", value)

      def print_sql(self,title,sql):
        cyan = '\033[96m'
        no_color = '\033[0m'
        print(f'{cyan} SQL STATEMENT-[{title}]------{no_color}')
        print(sql)

      def query_commit(self,sql,params={}):
        self.print_sql('commit with returning',sql)

        pattern = r"\bRETURNING\b"
        is_returning_id = re.search(pattern, sql)

        try:
          with self.pool.connection() as conn:
            cur =  conn.cursor()
            cur.execute(sql,params)
            if is_returning_id:
              returning_id = cur.fetchone()[0]
            conn.commit() 
            if is_returning_id:
              return returning_id
        except Exception as err:
          self.print_sql_err(err)

      # when we want to return a json object
      def query_array_json(self,sql,params={}):
        self.print_sql('array',sql)

        wrapped_sql = self.query_wrap_array(sql)
        with self.pool.connection() as conn:
          with conn.cursor() as cur:
            cur.execute(wrapped_sql,params)
            json = cur.fetchone()
            return json[0]

      # When we want to return an array of json objects
      def query_object_json(self,sql,params={}):
        self.print_sql('json',sql)
        self.print_params(params)

        wrapped_sql = self.query_wrap_object(sql)
        with self.pool.connection() as conn:
          with conn.cursor() as cur:
            cur.execute(wrapped_sql,params)
            json = cur.fetchone()
            if json == None:
              "{}"
            else:
              return json[0]

      def query_wrap_object(self,template):
        sql = f"""
        (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
        {template}
        ) object_row);
        """
        return sql

      def query_wrap_array(self,template):
        sql = f"""
        (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
        {template}
        ) array_row);
        """
        return sql

      def print_sql_err(self,err):
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno

        # print the connect() error
        print ("\npsycopg ERROR:", err, "on line number:", line_num)
        print ("psycopg traceback:", traceback, "-- type:", err_type)

    db = Db()
   ```
5. Update `backend-flask/services/create_activity.py` file.

   ```py
   from lib.db import db
   
        else:
      #  model['data'] = {
      #    'uuid': uuid.uuid4(),
      #    'display_name': 'Andrew Brown',
      #    'handle':  user_handle,
      #    'message': message,
      #    'created_at': now.isoformat(),
      #    'expires_at': (now + ttl_offset).isoformat()
      #  }
      #return model
        expires_at = (now + ttl_offset)
        uuid = CreateActivity.create_activity(user_handle,message,expires_at)

        object_json = CreateActivity.query_object_activity(uuid)
        model['data'] = object_json
      return model

    def create_activity(handle, message, expires_at):
      sql = db.template('activities','create')
      uuid = db.query_commit(sql,{
        'handle': handle,
        'message': message,
        'expires_at': expires_at
      })
      return uuid

    def query_object_activity(uuid):
      sql = db.template('activities','object')
      return db.query_object_json(sql,{
        'uuid': uuid
      })
   ```
6. Replace `backend-flask/services/home_activities.py` to be the following codes.

   ```py
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
          span.set_attribute("app.result_length", len(results))
          return results
   ```
7. Update the environment variable in `docker-compose.yml`.

   ```yml
   CONNECTION_URL: "${PROD_CONNECTION_URL}"
   #CONNECTION_URL: "postgresql://postgres:password@db:5432/cruddur"
   ```
8. Update the hard coded value of `user_handle` in `app.py`.

   ```py
   @app.route("/api/activities", methods=['POST','OPTIONS'])
   @cross_origin()
   def data_activities():
      user_handle = 'christhio'
   ```
9. Test the changes by adding new crud post. The newly added post should be reflected immediately.

   ![Cruddur Homepage](assets2/week-4/cruddur-homepage.png)
