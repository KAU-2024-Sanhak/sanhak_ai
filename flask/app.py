# 웹 애플리케이션 프레임워크
from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api, reqparse, abort

# 파이썬 표준 및 유틸리티 라이브러리
import json, os, random, signal, socket, sys
from time import time
from textwrap import dedent
from uuid import uuid4


# 네트워크 요청 처리
import requests
from requests_toolbelt import MultipartEncoder

# 데이터 처리
import ast
import copy

# 데이터 인코딩
import base64

app = Flask(__name__)


@app.route('/api/test1', methods=['GET'])
def test1():
    return 'test1'

@app.route('/api/test2', methods=['POST'])
def test2():
    values=request.get_json()
    val2=requests.get('http://localhost:8080'+'/api/test1')
    
    return jsonify({
        'msg_header' : 'this is sample'+values,
        'msg-body' : 'this is sample'+val2
    })


if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5000  # 기본 포트 번호
    
    app.run(host="0.0.0.0", port=port)