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
