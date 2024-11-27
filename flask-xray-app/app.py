from flask import Flask, render_template, request, jsonify
import requests
from io import BytesIO
import base64
import logging
import json

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

plugins = ('ECSPlugin', )
xray_recorder.configure(
    service='FLASK-XRAY-APP',
    plugins=plugins,
)
XRayMiddleware(app, xray_recorder)

patch_all()

@app.route('/')
def cat_image():
    request_headers_dict = dict(request.headers)
    request_headers_json = json.dumps(request_headers_dict, indent=2)
    trace_id = xray_recorder.current_segment().trace_id
    app.logger.info(f"[ AWS-XRAY-TRACE-ID: {trace_id} ] Request headers: {request_headers_json}")

    segment = xray_recorder.current_segment()
    segment.put_annotation('path', '/')
    segment.put_annotation('trace_id', trace_id)
    segment.put_metadata('headers', request_headers_dict, 'Request headers')
    
    # Cataasから画像を取得
    response = requests.get("https://cataas.com/cat")
    if response.status_code == 200:
        # バイナリデータをbase64エンコード
        img_data = base64.b64encode(response.content).decode("utf-8")
        
        # テンプレートにエンコード済みの画像データを渡す
        return render_template('index.html', img_data=img_data)
    else:
        return jsonify({"error": "Could not retrieve cat image"}), 500
    

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=80,
        debug=True
    )
