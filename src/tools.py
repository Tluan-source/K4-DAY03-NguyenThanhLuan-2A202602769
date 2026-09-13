"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
import unicodedata
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    {
        "name": "academic_query",
        "description": "Tra cứu hồ sơ và thông tin học vụ của sinh viên VinUni bằng mã sinh viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần tra cứu (ví dụ: 'SV2026001')"
                }
            },
            "required": ["student_id"]
        }
    },
    
    # Tool 2: Đặt lịch hẹn tư vấn học vụ (hoàn thành TASK 1.2)
    {
        "name": "schedule_appointment",
        "description": (
            "Đặt lịch hẹn tư vấn học vụ giữa sinh viên và Cố vấn học tập VinUni. "
            "Dùng khi sinh viên muốn gặp, hẹn gặp hoặc xin tư vấn trực tiếp với cố vấn."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian hẹn theo định dạng 'HH:MM DD/MM/YYYY' (ví dụ: '14:00 15/09/2026')"
                },
                "advisor_name": {
                    "type": "string",
                    "description": "Tên cố vấn học tập phụ trách sinh viên (ví dụ: 'PGS.TS Nguyễn Văn A')"
                }
            },
            "required": ["student_id", "datetime_str"]
        }
    },

    # Tool 3: Tìm kiếm vị trí thực tập
    {
        "name": "search_tool",
        "description": "Tìm kiếm các vị trí thực tập phù hợp với tiêu chí",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Tên hoặc lĩnh vực vị trí thực tập"
                },
                "position": {
                    "type": "string",
                    "description": "Vị trí mong muốn"
                },
                "location": {
                    "type": "string",
                    "description": "Địa điểm mong muốn"
                },
                "salary_range": {
                    "type": "string",
                    "description": "Khoảng lương"
                },
                "skill": {
                "type": "string",
                "description": "Kỹ năng chính của ứng viên"
                },
                "JD_summary": {
                    "type": "string",
                    "description": "Tóm tắt JD của vị trí việc làm"
                }
            },
            "required": ["position", "location"]
        }
    },
    {
        "name": "save_application",
        "description": "Lưu một vị trí thực tập vào danh sách ứng tuyển của sinh viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string"
                },
                "student_id": {
                    "type": "string"
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "saved",
                        "planning_to_apply",
                        "applied"
                    ]
                }
            },
            "required": [
                "job_id",
                "student_id",
                "status"
            ]
        }
    },
    {
        "name": "Evaluate_CV_and_JD",
        "description": "Đánh giá CV của sinh viên so với JD của vị trí thực tập và đưa ra nhận xét, điểm số, và đề xuất cải thiện.",
        "parameters": {
            "type": "object",
            "properties": {
                "cv_text": {
                    "type": "string",
                    "description": "Nội dung CV của sinh viên"
                },
                "jd_text": {
                    "type": "string",
                    "description": "Nội dung JD của vị trí thực tập"
                }
            },
            "required": ["cv_text", "jd_text"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "SV2026001": {
        "full_name": "Nguyễn Văn An",
        "class": "AI-K4",
        "gpa": 3.85,
        "email": "an.nv@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "PGS.TS Nguyễn Văn A"
    },
    "SV2026002": {
        "full_name": "Trần Thị Bình",
        "class": "AI-K4",
        "gpa": 3.60,
        "email": "binh.tt@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "TS. Lê Thị B"
    }
}
MOCK_INTERNSHIP_DATABASE = [

    {
        "job_id": "JOB001",
        "company": "TechVision AI",
        "position": "AI Engineer Intern",
        "location": "Ho Chi Minh City",
        "skills": [
            "Python",
            "PyTorch",
            "Computer Vision"
        ],
        "salary_range": "5-7 million VND",
        "jd_summary": (
            "Develop and evaluate Computer Vision models "
            "for image classification and object detection."
        )
    },

    {
        "job_id": "JOB002",
        "company": "NLP Labs",
        "position": "NLP Engineer Intern",
        "location": "Ho Chi Minh City",
        "skills": [
            "Python",
            "Transformers",
            "NLP"
        ],
        "salary_range": "4-6 million VND",
        "jd_summary": (
            "Develop NLP applications using Transformer models "
            "and Large Language Models."
        )
    },

    {
        "job_id": "JOB003",
        "company": "VisionNext",
        "position": "Computer Vision Intern",
        "location": "Hanoi",
        "skills": [
            "Python",
            "OpenCV",
            "Deep Learning"
        ],
        "salary_range": "5-8 million VND",
        "jd_summary": (
            "Research and implement Computer Vision solutions "
            "for intelligent camera systems."
        )
    },

    {
        "job_id": "JOB004",
        "company": "Agentic Tech",
        "position": "AI Research Intern",
        "location": "Remote",
        "skills": [
            "Python",
            "LLM",
            "RAG",
            "AI Agent"
        ],
        "salary_range": "6-8 million VND",
        "jd_summary": (
            "Research LLM, RAG and Agentic AI systems "
            "and develop experimental prototypes."
        )
    }
]
SAVED_APPLICATIONS = []

def execute_academic_query(student_id: str) -> str:
    """Thực thi tra cứu học vụ theo mã sinh viên"""
    student = MOCK_DATABASE.get(student_id.strip().upper())
    if student:
        return json.dumps({
            "status": "SUCCESS",
            "student_id": student_id,
            "data": student
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu sinh viên có mã '{student_id}'"
        }, ensure_ascii=False)

# ------------------------------------------------------------------------------
# Tiện ích chuẩn hoá chuỗi: cho phép so khớp giữa tiếng Việt có dấu (câu hỏi của
# sinh viên) và dữ liệu không dấu trong MOCK_INTERNSHIP_DATABASE.
# ------------------------------------------------------------------------------

# Một số cách gọi địa điểm khác nhau cùng trỏ về một thành phố
LOCATION_ALIASES = {
    "tphcm": "hochiminhcity",
    "hcm": "hochiminhcity",
    "saigon": "hochiminhcity",
    "hn": "hanoi",
}


def _strip_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt và chuyển về chữ thường: 'Hà Nội' -> 'ha noi'"""
    text = unicodedata.normalize("NFD", str(text or ""))
    return "".join(c for c in text if unicodedata.category(c) != "Mn").lower()


def _squash(text: str) -> str:
    """Bỏ dấu, bỏ khoảng trắng và ký tự đặc biệt: 'Hà Nội' -> 'hanoi'"""
    return "".join(c for c in _strip_accents(text) if c.isalnum())


def _tokens(text: str) -> list:
    """Tách thành danh sách từ đã bỏ dấu: 'AI Intern' -> ['ai', 'intern']"""
    cleaned = "".join(c if c.isalnum() else " " for c in _strip_accents(text))
    return [t for t in cleaned.split() if t]


def execute_search_internship(keyword: str = "", position: str = "", location: str = "",
                              salary_range: str = "", skill: str = "", JD_summary: str = "") -> str:
    """Thực thi tìm kiếm vị trí thực tập theo tiêu chí.

    Quy tắc so khớp:
      - 'position' và 'keyword' cùng mô tả "muốn làm công việc gì" nên chỉ cần
        khớp MỘT trong hai là đủ (quan hệ HOẶC).
      - 'location' và 'skill' là bộ lọc bắt buộc: nếu sinh viên có nêu thì job
        phải thoả mãn (quan hệ VÀ).
    """
    want_tokens = _tokens(position) + _tokens(keyword)

    location_key = _squash(location)
    location_key = LOCATION_ALIASES.get(location_key, location_key)
    skill_key = _strip_accents(skill).strip()

    results = []
    for job in MOCK_INTERNSHIP_DATABASE:
        # Gom toàn bộ phần mô tả của job thành một chuỗi để dò từ khoá
        haystack = _strip_accents(
            job["position"] + " " + job["company"] + " "
            + job["jd_summary"] + " " + " ".join(job["skills"])
        )
        job_location = _squash(job["location"])
        job_skills = _strip_accents(" ".join(job["skills"]))

        what_match = any(tok in haystack for tok in want_tokens) if want_tokens else True
        location_match = location_key in job_location if location_key else True
        skill_match = skill_key in job_skills if skill_key else True

        if what_match and location_match and skill_match:
            results.append(job)

    # Chỉ trả kết quả SAU KHI đã duyệt hết database.
    # (Lỗi cũ: hai lệnh return bị thụt vào trong vòng for nên hàm thoát ngay ở
    #  job đầu tiên và không bao giờ xét JOB002 - JOB004.)
    if not results:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": "Không tìm thấy vị trí thực tập phù hợp với tiêu chí."
        }, ensure_ascii=False)

    return json.dumps({
        "status": "SUCCESS",
        "message": f"Tìm thấy {len(results)} vị trí thực tập phù hợp.",
        "results": results
    }, ensure_ascii=False)

def execute_schedule_appointment(student_id: str, datetime_str: str, advisor_name: str = "PGS.TS Nguyễn Văn A") -> str:
    """Thực thi đặt lịch hẹn tư vấn học vụ"""
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"BK-{student_id}-99",
        "student_id": student_id,
        "datetime": datetime_str,
        "advisor": advisor_name,
        "message": f"Đặt lịch thành công cho sinh viên {student_id} với {advisor_name} vào lúc {datetime_str}."
    }, ensure_ascii=False)

def execute_save_application(job_id: str, student_id: str, status: str) -> str:
    job = next((job for job in MOCK_INTERNSHIP_DATABASE if job["job_id"] == job_id), None)
    if job is None:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy vị trí thực tập với job_id '{job_id}'"
        }, ensure_ascii=False)

    allowed_statuses = ["saved", "planning_to_apply", "applied"]
    if status not in allowed_statuses:
        return json.dumps({
            "status": "INVALID_STATUS",
            "message": f"Trạng thái '{status}' không hợp lệ. Vui lòng sử dụng một trong các trạng thái: {allowed_statuses}"
        }, ensure_ascii=False)

    application = {
        "application_id": (f"APP-{student_id}-{job_id}"),
        "student_id": student_id,
        "job_id": job_id,
        "company": job["company"],
        "position": job["position"],
        "status": status
    }

    existing_application = next((
        app for app in SAVED_APPLICATIONS 
                if app["student_id"] == student_id and app["job_id"] == job_id), 
                    None
        )

    if existing_application:
        existing_application["status"] = status
        return json.dumps({
            "status": "SUCCESS",
            "message": f"Cập nhật trạng thái ứng tuyển thành công cho sinh viên {student_id} với vị trí {job_id}.",
            "application": existing_application
        }, ensure_ascii=False)

    SAVED_APPLICATIONS.append(application)

    return json.dumps({
        "status": "SUCCESS",
        "message": f"Lưu ứng tuyển thành công cho sinh viên {student_id} với vị trí {job_id} tại công ty {job['company']}.",
        "application": application
    }, ensure_ascii=False)

# Từ điển kỹ năng dùng để đối chiếu CV với JD: lấy từ chính database thực tập
# rồi bổ sung thêm một số kỹ năng phổ biến khác.
SKILL_VOCABULARY = sorted(
    {skill for job in MOCK_INTERNSHIP_DATABASE for skill in job["skills"]}
    | {"Machine Learning", "Deep Learning", "TensorFlow", "SQL", "Git",
       "Docker", "Pandas", "NumPy", "English"}
)


def execute_evaluate_cv_and_jd(cv_text: str, jd_text: str) -> str:
    """Đối chiếu CV của sinh viên với JD của vị trí thực tập.

    Cách chấm: dò các kỹ năng trong SKILL_VOCABULARY xuất hiện ở JD (kỹ năng
    JD yêu cầu), sau đó xem CV đáp ứng được bao nhiêu phần trăm trong số đó.
    """
    cv = _strip_accents(cv_text)
    jd = _strip_accents(jd_text)

    if not cv.strip() or not jd.strip():
        return json.dumps({
            "status": "INVALID_INPUT",
            "message": "Cần cung cấp đủ cả nội dung CV và nội dung JD để đánh giá."
        }, ensure_ascii=False)

    required = [s for s in SKILL_VOCABULARY if _strip_accents(s) in jd]
    if not required:
        return json.dumps({
            "status": "NO_SKILL_DETECTED",
            "message": "Không nhận diện được kỹ năng cụ thể nào trong JD để đối chiếu."
        }, ensure_ascii=False)

    matched = [s for s in required if _strip_accents(s) in cv]
    missing = [s for s in required if s not in matched]
    score = round(len(matched) / len(required) * 100)

    if score >= 75:
        verdict = "Rất phù hợp — nên nộp hồ sơ ngay."
    elif score >= 50:
        verdict = "Khá phù hợp — nên bổ sung vài kỹ năng còn thiếu trước khi nộp."
    else:
        verdict = "Chưa phù hợp — cần rèn thêm các kỹ năng cốt lõi mà JD yêu cầu."

    suggestions = [f"Bổ sung dự án hoặc kinh nghiệm liên quan tới '{s}' vào CV." for s in missing[:3]]
    if not suggestions:
        suggestions = ["CV đã phủ hết kỹ năng JD yêu cầu; nên làm nổi bật kết quả đo lường được của từng dự án."]

    return json.dumps({
        "status": "SUCCESS",
        "match_score": score,
        "required_skills": required,
        "matched_skills": matched,
        "missing_skills": missing,
        "verdict": verdict,
        "suggestions": suggestions
    }, ensure_ascii=False)


# Router gọi tool thực tế — mỗi tool trong TOOLS_SCHEMA phải có đúng một hàm ở đây
TOOL_ROUTER = {
    "academic_query": execute_academic_query,
    "schedule_appointment": execute_schedule_appointment,
    "search_tool": execute_search_internship,
    "save_application": execute_save_application,
    "Evaluate_CV_and_JD": execute_evaluate_cv_and_jd
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            # Gọi hàm execution tương ứng, unpack arguments từ dict
            result_str = TOOL_ROUTER[tool_name](**arguments)
            return result_str
        except TypeError as e:
            # Lỗi tham số (missing required args, wrong arg names, etc)
            return json.dumps({
                "status": "EXECUTION_ERROR",
                "error": f"Lỗi tham số: {str(e)}",
                "tool_name": tool_name,
                "arguments": arguments
            }, ensure_ascii=False)
        except Exception as e:
            # Lỗi khác (database, logic error, etc)
            return json.dumps({
                "status": "EXECUTION_ERROR",
                "error": str(e),
                "tool_name": tool_name
            }, ensure_ascii=False)
    else:
        # Tool không tồn tại
        return json.dumps({
            "status": "UNKNOWN_TOOL",
            "error": f"Tool '{tool_name}' không tồn tại!",
            "available_tools": list(TOOL_ROUTER.keys())
        }, ensure_ascii=False)
