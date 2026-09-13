"""
🖥️ DEMO WEB UI — So sánh 4 chế độ AI:
   1) Chatbot Base (Offline, không Tool)
   2) Chatbot API (LLM thật, không Tool)
   3) MCP ReAct Agent (Offline Mock)
   4) MCP ReAct Agent (LLM thật)

Chạy: python src/web_app.py   rồi mở http://127.0.0.1:5000
"""

import os
import sys

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import load_test_cases, run_react_agent
from mcp_server import MCPAcademicServer
from prompts import CHATBOT_BASELINE_PROMPT
from providers import MockOfflineProvider, get_llm_provider

load_dotenv()

app = Flask(__name__)
mcp_server = MCPAcademicServer()

MODES = {
    "base": "Chatbot Base (Offline, không Tool)",
    "api_chat": "Chatbot API (LLM thật, không Tool)",
    "mcp_mock": "MCP ReAct Agent (Offline Mock)",
    "mcp_api": "MCP ReAct Agent (LLM thật)",
}


def _final_answer(trace: list) -> str:
    for step in reversed(trace):
        if step.get("action_type") == "FINAL_ANSWER":
            return step.get("output", "")
    return "(Không có câu trả lời cuối cùng)"


def run_mode(mode: str, message: str) -> dict:
    """Chạy 1 câu hỏi qua đúng 1 trong 4 chế độ AI và trả về kết quả đồng nhất."""
    if mode == "base":
        answer = MockOfflineProvider().generate(message, system_prompt=CHATBOT_BASELINE_PROMPT)
        trace = []
    elif mode == "api_chat":
        answer = get_llm_provider().generate(message, system_prompt=CHATBOT_BASELINE_PROMPT)
        trace = []
    elif mode == "mcp_mock":
        trace = run_react_agent(message, MockOfflineProvider(), mcp_server)
        answer = _final_answer(trace)
    elif mode == "mcp_api":
        trace = run_react_agent(message, get_llm_provider(), mcp_server)
        answer = _final_answer(trace)
    else:
        raise ValueError(f"Mode không hợp lệ: {mode}")

    total_latency_ms = round(sum(step.get("latency_ms", 0) for step in trace), 2)
    return {
        "mode": mode,
        "label": MODES[mode],
        "answer": answer,
        "trace": trace,
        "total_latency_ms": total_latency_ms,
    }


@app.route("/")
def index():
    return render_template("index.html", modes=MODES)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    mode = data.get("mode") or "mcp_api"

    if not message:
        return jsonify({"error": "Vui lòng nhập câu hỏi."}), 400
    if mode not in MODES:
        return jsonify({"error": f"Mode không hợp lệ: {mode}"}), 400

    return jsonify(run_mode(mode, message))


@app.route("/api/samples")
def api_samples():
    """Câu hỏi mẫu lấy từ config/test_cases.json để demo nhanh, khỏi phải gõ tay."""
    samples = [
        {"id": tc["id"], "question": tc["question"]}
        for tc in load_test_cases()
        if not tc["question"].strip().startswith("TODO")
    ]
    return jsonify({"samples": samples})


@app.route("/api/compare", methods=["POST"])
def api_compare():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Vui lòng nhập câu hỏi."}), 400

    results = [run_mode(mode, message) for mode in MODES]
    return jsonify({"results": results})


if __name__ == "__main__":
    print("==========================================================")
    print("🖥️  DEMO WEB UI — Chatbot vs ReAct Agent (MCP)")
    print("==========================================================")
    print(f"🔌 Provider cho các chế độ 'LLM thật': {get_llm_provider().__class__.__name__}")
    print("🌐 Mở trình duyệt tại: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
