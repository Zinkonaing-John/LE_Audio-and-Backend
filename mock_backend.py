#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_file, abort
import io, wave, os, time, base64
app = Flask(__name__)

@app.route("/stt/restart", methods=["POST"])
def stt_restart():
    return jsonify({"status":"recording_started"})

@app.route("/stt/stop", methods=["POST"])
def stt_stop():
    f = request.files.get("file")
    if not f:
        return jsonify({"error":"no file uploaded"}), 400
    transcript = "안녕하세요, 이것은 모의 전사입니다."
    translations = {
        "en": "Hello, this is a mock transcript.",
        "ja": "こんにちは、これはモックの文字起こしです。",
        "zh-cn": "你好，这是一个模拟转录。",
        "vi": "Xin chào, đây là bản ghi giả lập."
    }
    return jsonify({"transcript": transcript, "translations": translations})

@app.route("/translate", methods=["POST"])
def translate():
    j = request.get_json(force=True)
    text = j.get("text","")
    translations = {
        "en": "Hello, this is a mock transcript." if text else "",
        "ja": "こんにちは、これはモックの文字起こしです。" if text else "",
        "zh-cn": "你好，这是一个模拟转录。" if text else "",
        "vi": "Xin chào, đây là bản ghi giả lập." if text else ""
    }
    return jsonify({"translations": translations})

@app.route("/tts/speak", methods=["POST"])
def tts_speak():
    sample_path = os.path.join(os.path.dirname(__file__), "sample.wav")
    if os.path.exists(sample_path):
        return send_file(sample_path, mimetype="audio/wav", as_attachment=False)
    return abort(404)

@app.route("/llm/chat", methods=["POST"])
def llm_chat():
    j = request.get_json(force=True)
    msg = j.get("message", "")
    response = "Mock LLM response to: " + (msg[:200])
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
