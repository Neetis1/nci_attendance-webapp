# apt-get update && apt-get install -y gnupg software-properties-common curl
# curl -sL https://deb.nodesource.com/setup_12.x | bash -
# apt-get install -y nodejs
# npm install -g serverless
# npm install serverless-aws-documentation
# npm i serverless-plugin-aws-alerts
# curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -
# apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
# apt-get update && apt-get install terraform


cd terraform

terraform init

terraform apply --auto-approve

cd ..

serverless deploy | tee logoutput.txt

result=$(cat deploy.out | grep -Eo "(POST - https)://[a-zA-Z0-9./?=_%:-]*" | sort -u)

arrIN=(${result//-/ })

printf '{"api": "%s-api.us-east-1.amazonaws.com/dev/attendance/"}' ${arrIN[1]}   > ../nci-attendance-webapp/src/apiUrl.json