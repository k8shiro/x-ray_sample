# Flaskを立ち上げるためのDockerfile

# ベースイメージの指定
FROM python:3.7

# 作業ディレクトリの指定
WORKDIR /app

# ホストのファイルをコンテナにコピー
COPY . /app

# 必要なパッケージのインストール
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Flaskのポートを指定
EXPOSE 5000

# Flaskの起動
CMD ["python", "app.py"]
