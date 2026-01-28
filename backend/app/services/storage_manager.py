import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_user_file(user_id: str) -> Path:
    return DATA_DIR / f"{user_id}.json"

def load_user_data(user_id: str) -> Dict[str, Any]:
    ensure_data_dir()
    file_path = get_user_file(user_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"user_id": user_id, "sessions": []}

def save_user_data(user_id: str, data: Dict[str, Any]):
    try:
        ensure_data_dir()
        file_path = get_user_file(user_id).absolute()
        print(f"DEBUG: 准备写入文件，绝对路径为: {file_path}", flush=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 保存成功！文件大小: {os.path.getsize(file_path)} 字节", flush=True)
    except Exception as e:
        print(f"❌ 存储失败！错误原因: {str(e)}", flush=True)

def add_full_session_to_user(user_id: str, detailed_logs: List[Dict[str, Any]], final_report: Dict[str, Any]):
    print(f"DEBUG: 开始处理用户 {user_id} 的结案数据", flush=True)
    data = load_user_data(user_id)
    new_session = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "final_report": final_report,
        "detailed_steps": detailed_logs 
    }
    data["sessions"].append(new_session)
    save_user_data(user_id, data)

def get_last_report(user_id: str) -> Optional[Dict[str, Any]]:
    data = load_user_data(user_id)
    if data["sessions"]:
        # 获取最近一次结案报告
        return data["sessions"][-1]["final_report"]
    return None
