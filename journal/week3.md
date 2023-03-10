# Week 3 — Decentralized Authentication

## Required Homework/Tasks

### Setup Cognito User Pool

1. Navigate to AWS Cognito > User pools.

   ![User Pools](assets2/week-3/cognito-user-pools.png)
2. Create user pool.
3. For sign-in experience configuration step, follow the screenshot below.

   ![Configure sign-in experience](assets2/week-3/cognito-sign-in-experience2.png)
4. For security requirements configuration step, follow the screenshots below.
   For this bootcamp, 8 characters password length is sufficient.
   In addition, we use e-mail as a user account recovery method instead of SMS as we don't want incur extra cost for the bootcamp.

   ![Password policy](assets2/week-3/cognito-security-requirements1.png)
   
   ![MFA and User Account Recovery](assets2/week-3/cognito-security-requirements2.png)
5. For sign-up experience configuration step, follow the screenshots below.

   ![Configure sign-up experience (1)](assets2/week-3/cognito-sign-up-experience1.png)
   
   ![Configure sign-up experience (2)](assets2/week-3/cognito-sign-up-experience2-1.png)
6. For message delivery configuration step, follow the screenshot below.

   ![Configure message delivery](assets2/week-3/cognito-message-delivery.png)
7. For integrate your app step, follow the screenshots below.

   ![Integrate your app (1)](assets2/week-3/cognito-integrate-your-app.png)
   
   ![Integrate your app (2)](assets2/week-3/cognito-integrate-your-app2.png)
8. Review the configuration and click 'Create user pool'.

   ![User Pools](assets2/week-3/cognito-user-pools-list.png)

### Implement Custom Signin Page

1. Install AWS Amplify.
   
   ```sh
   npm i aws-amplify --save
   ```
2. Add environment variables to `frontend-react-js's environment` in `docker-compose.yml`.

   ```yml
   REACT_APP_AWS_PROJECT_REGION: "${AWS_DEFAULT_REGION}"
   REACT_APP_AWS_COGNITO_REGION: "${AWS_DEFAULT_REGION}"
   REACT_APP_AWS_USER_POOLS_ID: "us-east-1_nNyvfnegi"
   REACT_APP_CLIENT_ID: "5mhavv9qbf2k41d1fc15ge4587"
   ```
   Note that REACT_APP_AWS_USER_POOLS_ID can be found user pools table list, while REACT_APP_CLIENT_ID can be found inside user pool's App Integration.
   
   ![User Pool Id](assets2/week-3/cognito-user-pool-id.png)
   
   ![User Pool's Client Id](assets2/week-3/cognito-app-client-id.png)
3. Configure AWS Amplify in `App.js` under frontend-react-js.

   ```js
   import { Amplify } from 'aws-amplify';

   Amplify.configure({
     "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
     "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
     "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
     "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
     "oauth": {},
     Auth: {
       // We are not using an Identity Pool
       // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
       region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
       userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
       userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
     }
   });
   ```
4. Set whether we are authenticated when we load page by replacing the existing code with the following code in `HomeFeedPage.js`.

   ```js
   import { Auth } from 'aws-amplify';

   // set a state
   const [user, setUser] = React.useState(null);

   // check if we are authenicated
   const checkAuth = async () => {
     Auth.currentAuthenticatedUser({
       // Optional, By default is false. 
       // If set to true, this call will send a 
       // request to Cognito to get the latest user data
       bypassCache: false 
     })
     .then((user) => {
       console.log('user',user);
       return Auth.currentAuthenticatedUser()
     }).then((cognito_user) => {
         setUser({
           display_name: cognito_user.attributes.name,
           handle: cognito_user.attributes.preferred_username
         })
     })
     .catch((err) => console.log(err));
   };

   // check when the page loads if we are authenicated
   React.useEffect(()=>{
     //prevents double call
     if (dataFetchedRef.current) return;
     dataFetchedRef.current = true;
     
     loadData();
     checkAuth();
   }, [])
   ```
5. Replace the function of `signOut` to the following code in `ProfileInfo.js`.

   ```js
   import { Auth } from 'aws-amplify';

   const signOut = async () => {
     try {
         await Auth.signOut({ global: true });
         window.location.href = "/"
     } catch (error) {
         console.log('error signing out: ', error);
     }
   }
   ```
6. Replace the function of `onsubmit` to the following code in `SigninPage.js`.

   ```js
   import { Auth } from 'aws-amplify';
   
   const [errors, setErrors] = React.useState('');

   const onsubmit = async (event) => {
     setErrors('')
     event.preventDefault();
     Auth.signIn(email, password)
      .then(user => {
        localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
        window.location.href = "/"
      })
     .catch(error => {
       if (error.code == 'UserNotConfirmedException') {
         window.location.href = "/confirm"
       }
       setErrors(error.message)
     });
     return false
   }

   let el_errors;
   if (errors){
      el_errors = <div className='errors'>{errors}</div>;
   }
   ```
7. Create a user from the user pool on AWS Console.

   ![Create new user](assets2/week-3/cognito-create-user.png)
   
   ![Create new user details](assets2/week-3/cognito-create-user-details.png)
8. As the user's confirmation status is *Force change password*, and there's no way to change password from the AWS Console, we could use AWS CLI as found on https://stackoverflow.com/questions/40287012/how-to-change-user-status-force-change-password.

   ![User Information](assets2/week-3/cognito-force-change-password.png)

   ```sh
   aws cognito-idp admin-set-user-password \
   --user-pool-id us-east-1_nNyvfnegi \
   --username christhio \
   --password Testing123! \
   --permanent
   ```
   
   ![User Information](assets2/week-3/cognito-user-confirmed.png)
9. Run docker compose up and hit the frontend website.
10. Sign in with above credentials. The handle name and preferred name should be displayed.

    ![User Homepage](assets2/week-3/cognito-sign-in-christhio.png)

### Implement Custom Signup Page

1. Delete the user created in **Implement Custom Signin Page** section.
2. Replace `onsubmit` function with the following code in `SignupPage.js`.

   ```js
   import { Auth } from 'aws-amplify';
   
   const [errors, setErrors] = React.useState('');
   
   const onsubmit = async (event) => {
      event.preventDefault();
      setErrors('')
      try {
         const { user } = await Auth.signUp({
           username: email,
           password: password,
           attributes: {
               name: name,
               email: email,
               preferred_username: username,
           },
           autoSignIn: { // optional - enables auto sign in after user is confirmed
               enabled: true,
           }
         });
         console.log(user);
         window.location.href = `/confirm?email=${email}`
      } catch (error) {
         console.log(error);
         setErrors(error.message)
      }
      return false
   }

   let el_errors;
   if (errors){
      el_errors = <div className='errors'>{errors}</div>;
   }
   ```
3. Run docker compose up.
4. Fill in the sign up details.

   ![Sign Up Page](assets2/week-3/cruddur-sign-up-page.png)
5. If it's successful, you should be redirected to confirmation page like in the screenshot below.

   ![Confirmation Page](assets2/week-3/cruddur-confirmation-page.png)

### Implement Custom Confirmation Page

1. Replace `resend_code` and `onsubmit` function with the following code in `ConfirmationPage.js`.

   ```js
   import { Auth } from 'aws-amplify';
   
   const resend_code = async (event) => {
      setErrors('')
      try {
         await Auth.resendSignUp(email);
         console.log('code resent successfully');
         setCodeSent(true)
      } catch (err) {
         // does not return a code
         // does cognito always return english
         // for this to be an okay match?
         console.log(err)
         if (err.message == 'Username cannot be empty'){
           setErrors("You need to provide an email in order to send Resend Activiation Code")   
         } else if (err.message == "Username/client id combination not found."){
           setErrors("Email is invalid or cannot be found.")   
         }
      }
   }

   const onsubmit = async (event) => {
      event.preventDefault();
      setErrors('')
      try {
         await Auth.confirmSignUp(email, code);
         window.location.href = "/"
      } catch (error) {
         setErrors(error.message)
      }
      return false
   }
   ```
2. After filling in sign up details, the confirmation form will be shown.
3. Check email and fill in the confirmation code.

   ![Confirmation Page](assets2/week-3/cruddur-confirmation-page-filled.png)
4. After successfully confirming the account, you should be redirected to homepage.

### Implement Custom Recovery Page

1. Replace `onsubmit_send_code` and `onsubmit_confirm_code` function with the following code in `RecoverPage.js`.

   ```js
   import { Auth } from 'aws-amplify';

   const onsubmit_send_code = async (event) => {
      event.preventDefault();
      setErrors('')
      Auth.forgotPassword(username)
      .then((data) => setFormState('confirm_code') )
      .catch((err) => setErrors(err.message) );
      return false
   }

   const onsubmit_confirm_code = async (event) => {
      event.preventDefault();
      setErrors('')
      if (password == passwordAgain){
         Auth.forgotPasswordSubmit(username, code, password)
         .then((data) => setFormState('success'))
         .catch((err) => setErrors(err.message) );
      } else {
          setErrors('Passwords do not match')
      }
      return false
   }
   ```
2. Run docker compose up.
3. Hit homepage and click Sign In and then Forgot Password?.
4. Fill in the email address to retrieve the reset password code.
   
   ![Recover Password Page](assets2/week-3/cruddur-password-recovery.png)
   
   ![Recover Password Page](assets2/week-3/cruddur-password-recovery2.png)
5. The final result should be "Your password has been successfully reset!".

   ![Recover Password Page](assets2/week-3/cruddur-password-recovery3.png)

### Watch about different approaches to verifying JWTs
