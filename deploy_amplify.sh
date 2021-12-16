#!/bin/bash
set -e
IFS='|'

# npm install -g @aws-amplify/cli  
# npm install --save aws-amplify @aws-amplify/ui-react@1.2.24
# npm install --save react-router-dom@5.2.0
# npm install --save axios

# yes "" | amplify delete
# yes "" | amplify init

# Ref AWS Amplify-Cli Github Repo
# https://github.com/aws-amplify/amplify-cli
AUTHCONFIG="{\
\"version\": 1,\
\"resourceName\": \"nciattendance\",\
\"serviceConfiguration\": {\
\"serviceName\": \"Cognito\",\
\"userPoolConfiguration\": {\
\"signinMethod\": \"EMAIL\",\
\"requiredSignupAttributes\": [\"EMAIL\"],\
\"passwordRecovery\": {\
\"deliveryMethod\": \"EMAIL\",\
\"emailMessage\": \"Your verification code is {####}.\",\
\"emailSubject\": \"NCI Attendance App Verification Code\"\
}\
},\
\"includeIdentityPool\": false\
}\
}"

echo $AUTHCONFIG | amplify add auth --headless 

# amplify push --yes

# To Push the NCI Connect WebApp to the Cloud
# yes "" | amplify add hosting

# yes "" | amplify publish

# npm start
