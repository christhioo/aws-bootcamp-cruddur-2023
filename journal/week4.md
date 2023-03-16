# Week 4 — Postgres and RDS

## Create RDS Postgres Instance (via CLI)

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

## Bash scripting for common database actions

We need to create a new directory to store all the common bash scripts called `bin`.  
The directory will be under `aws-bootcamp-cruddur-2023/backend-flask/`.

   ```sh
   mkdir /workspace/aws-bootcamp-cruddur-2023/backend-flask/bin
   ```

### Shell Script to Connect to DB

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
   export CONNECTION_URL="postgresql://postgres:pssword@127.0.0.1:5432/cruddur"
   gp env CONNECTION_URL="postgresql://postgres:pssword@127.0.0.1:5432/cruddur"
   
   export PROD_CONNECTION_URL="postgresql://cruddurroot:password@cruddur-db-instance.cwbipomqhh0x.us-east-1.rds.amazonaws.com:5432/cruddur"
   gp env PROD_CONNECTION_URL="postgresql://cruddurroot:password@cruddur-db-instance.cwbipomqhh0x.us-east-1.rds.amazonaws.com:5432/cruddur"
   ```
3. Make the bash script executable.

   ```sh
   chmod u+x bin/db-connect
   ```
4. Execute the script.

   ```sh
   ./bin/db-connect
   ```
   
### Shell Script to Drop the Database

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
3. Execute the script.

   ```sh
   ./bin/db-drop
   ```

### Shell Script to Create the Database

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
3. Execute the script.

   ```sh
   ./bin/db-create
   ```

### Shell Script to Load the Schema

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
3. Create a new bash script `bin/db-schema-load`.

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
3. Make the bash script executable.

   ```sh
   chmod u+x bin/db-schema-load
   ```
4. Execute the script.

   ```sh
   ./bin/db-schema-load
   ```

### Shell Script to Load the Seed Data

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
4. Execute the script.

   ```sh
   ./bin/db-seed
   ```

### Shell Script to Setup Everything

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
3. Execute the script.

   ```sh
   ./bin/db-setup
   ```

### Make Prints Nicer

Reference: https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"
```
