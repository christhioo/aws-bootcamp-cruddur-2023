# Week 0 — Billing and Architecture

## Required Homework/Tasks

### Create an Admin User
Navigate to IAM to create new admin user. 
![Add Users](assets/iam-add-users.png)

Then I created new "Admin" group with AdministratorAccess role.
![Create new user](assets/iam-add-user-to-group.png)

After creating the account, Console sign-in details will be displayed.
![IAM User Creation](assets/iam-user-creation.png)

I copied the console password and used the console sign-in URL to login as new user.
Once I login with the temporary password, I updated with new password by using auto-generated password from https://passwordsgenerator.net/.

As Account ID is difficult to remember, I login as root user to create my account alias.
![IAM Account Alias](assets/iam-account-alias.png)

![IAM Account Alias Successful](assets/iam-account-alias2.png)


### Use CloudShell
As CloudShell isn't available in Asia Pacific (Singapore) region, I switched to US East (N. Virginia) / us-east-1 to launch CloudShell.
I couldn't start AWS CloudShell environment as shown in the screenshot below.

![CloudShell Error](assets/aws-cloudshell-error.png)

After searching on the internet, I found one article that best describes my issue.
https://docs.aws.amazon.com/cloudshell/latest/userguide/troubleshooting.html
From the article, it might be because I haven't updated my Edge browser.
Once I updated it to the latest version and cleared browsing data, it works successfully.

In addition, CloudShell will use Bash shell by default. 
We can change to different shell following the command on https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-cloudshell.html#using-shells

![CloudShell](assets/aws-cloudshell.png)

### Generate AWS Credentials
Navigate to Security Credentials under top right menu.

![Security Credentials](assets/security-credentials.png)

Click Create Access Key and choose AWS CLI access.
![Access Key](assets/access-key.png)

Finally, click download .csv file.

### Install AWS CLI
To install AWS CLI on gitpod, I followed the steps found on https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html.
```
cd /workspace
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

The reason of unzipping on workspace directory is because we don't want to commit it on GitHub.
To test if the AWS CLI is working on GitPod, we can use command 'aws' like in the screenshot below.

![Gitpod](assets/gitpod-aws-cli.png)

To let gitpod run above commands automatically instead of entering it every time it launches workspace, I added below task into .gitpod.yml config file.
```
tasks:
  - name: aws-cli
    env:
      AWS_CLI_AUTO_PROMPT: on-partial
    init: |
      cd /workspace
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
      unzip awscliv2.zip
      sudo ./aws/install
      cd $THEIA_WORKSPACE_ROOT
```

Next is setting up the environment variable for *current bash terminal*.
```
export AWS_ACCESS_KEY_ID="AKIAXUORKPYQQBKE7M6V"
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION=us-east-1
```
To check whether it's working, I used the following command.
```
aws sts get-caller-identity
```
And the result is as follows.

![AWS Identity](assets/gitpod-aws-identity.png)

To tell Gitpod to remember environment variable without re-inputting every single time.
```
gp env AWS_ACCESS_KEY_ID="AKIAXUORKPYQQBKE7M6V"
gp env AWS_SECRET_ACCESS_KEY=""
gp env AWS_DEFAULT_REGION=us-east-1
```

### Create a Billing Alarm

Amazon CloudWatch uses Amazon SNS to send email. First, create and subscribe to an SNS topic. When you create a CloudWatch alarm, you can add this SNS topic to send an email notification when the alarm changes state.

#### Setting up Amazon SNS notifications
Reference: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/US_SetupSNS.html

1. Create an SNS Topic
   ```
   aws sns create-topic --name myFirstBillingSNS
   ```
2. Subscribe email address to SNS Topic
   ```
   aws sns subscribe --topic-arn arn:aws:sns:us-east-1:524961873441:myFirstBillingSNS --protocol email --notification-endpoint christhio@duck.com
   ```
3. Confirm subscription from email

![Amazon SNS Notification](assets/aws-sns.png)

#### Create Alarm
Create alarm_config.json file and then run the following command.
```
aws cloudwatch put-metric-alarm --cli-input-json file://aws/json/alarm_config.json
```

![CloudWatch Alarm](assets/aws-cloudwatch.png)

### Create a Budget
I created a budget from AWS Billing so that an email notification will be sent to me once I have exceeded AWS Free Tier.
The threshold I set is $0.01.

![Budget Alarm](assets/Budget-alarm.png)

### Recreate Logical Architectual Diagram in Lucid Charts

![Cruddur Logical Architectual Diagram](assets/Cruddur-Logical-Diagram.jpeg)
Source: https://lucid.app/lucidchart/404a4f0b-7139-48d6-a904-41df001ea359/edit?viewport_loc=-110%2C326%2C2464%2C1470%2C0_0&invitationId=inv_313b302a-820c-4730-8ea5-ba04a3c8edd4
