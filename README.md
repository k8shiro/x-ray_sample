# x-ray_sample

AWS X-Ray のサンプルコード

# ECS でのサンプルアプリケーションのデプロイ

必要になる変数を設定

```
# 環境変数設定
REGION=********* # 使用するリージョン
AWS_ACCOUNT_ID=********* # AWSアカウントID
SUBNET_ID=subnet-********* # サブネットID
SECURITY_GROUP_ID=sg-********* # セキュリティグループID

```

ECR リポジトリを作成し、Docker イメージをビルドして ECR にプッシュする

```
# ECRリポジトリを作成
aws ecr create-repository  --region ${REGION} --repository-name flask-xray-app

# Dockerイメージをビルド
docker build -t flask-xray-app ./flask-xray-app

# イメージにECRタグを付ける
docker tag flask-xray-app:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/flask-xray-app:latest

# AWS CLIを使ってログインし、ECRにプッシュ
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/flask-xray-app:latest
```

ECS クラスターを作成
ECS のタスク定義ファイルとして flask-xray-task.json.sample をベースに`<aws_account_id>`と`<region>`を置換して flask-xray-task.json を作成後、以下を実行

```
# ECSクラスターの作成
aws ecs create-cluster --region ${REGION} --cluster-name flask-xray-cluster

# ECSタスク定義の作成
aws ecs register-task-definition \
    --region ${REGION} \
    --cli-input-json file://flask-xray-task.json

# ECSロググループの作成
aws logs create-log-group --log-group-name "/ecs/flask-xray"

# ECSサービスの作成
aws ecs create-service \
  --region ${REGION} \
  --cluster flask-xray-cluster \
  --service-name flask-xray-service \
  --task-definition flask-xray-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_ID}],securityGroups=[${SECURITY_GROUP_ID}],assignPublicIp=ENABLED}"
```

```
# サービスを更新
aws ecs update-service --cluster flask-xray-cluster --service flask-xray-service --task-definition flask-xray-task
```
