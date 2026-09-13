"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
"""

import json
import sys
from typing import Dict, Any, List
import uuid
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPAcademicServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    """
    def __init__(self, server_name: str = "ai-internship-assistant-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA
        
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] HỌC VIÊN HOÀN THIỆN HÀM THỰC THI TOOL TRÊN MCP SERVER
        Thực thi request gọi Tool theo chuẩn MCP JSON-RPC
        """
        request_id = str(uuid.uuid4())
        try:
            result_str = dispatch_tool_call(tool_name, arguments)

            try:
                observation = json.loads(result_str)
            except json.JSONDecodeError:
                observation = {"error": "Invalid JSON response from tool."}

            return{
                "jsonrpc": "2.0",
                "server": self.server_name,
                "id": request_id,
                "tool": tool_name,
                "result": observation
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "server": self.server_name,
                "tool": tool_name,
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": f"Tool execution error: {str(e)}"
                }
            }


        
        # Bước 1: Gọi dispatch_tool_call để thực thi tool
        # result_str = dispatch_tool_call(tool_name, arguments)

        # Bước 2: Chuyển đổi JSON string thành Dictionary
        # result = json.loads(result_str)

        # Bước 3: Đóng gói phản hồi theo chuẩn MCP JSON-RPC 2.0
        # return {
        #     "jsonrpc": "2.0",
        #     "server": self.server_name,
        #     "tool": tool_name,
        #     "result": result
        # }


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER")
    print("==========================================================")
    
    server = MCPAcademicServer()
    tools = server.list_tools()
    print(f"✅ Khởi tạo thành công MCP Server: {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố: {len(tools)}")
    
    # Kiểm tra trạng thái TODO 1.2 (Tool Schema)
    save_tool = next((t for t in tools if t.get("name") == "save_application"), None)

    if save_tool and not save_tool.get("parameters", {}).get("properties"):
        print("⏳ [TODO 1.2]: Tool 'save_tool' chưa được định nghĩa properties trong 'src/tools.py'.")
    else:
        print("✅ [TODO 1.2]: Tool 'save_tool' đã có schema đầy đủ.")

    # Kiểm tra trạng thái TODO 2.1 (call_tool)
    test_result = server.call_tool("search_tool",
        {
            "position": "AI Engineer Intern",
            "location": "Ho Chi Minh City",
            "skill": "Python"
        }
    )
    if not test_result:
        print("⏳ [TODO 2.1]: Hàm call_tool() đang trả về rỗng. Học viên hãy hoàn thiện TODO 2.1 trong 'src/mcp_server.py'!")
    else:
        print(f"✅ [TODO 2.1]: Test dispatch tool 'search_tool' thành công:")
        print(f"   Phản hồi JSON-RPC: {json.dumps(test_result, ensure_ascii=False)}")
