import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
from file_handler import *


class AppUserState:
    def __init__(self):
        self.user_id = None

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

# 전역적으로 사용할 인스턴스 생성
app_user_state = AppUserState()

# Firestore 초기화
firestore_key_path = load_data('fs_gamgee.json')
cred = credentials.Certificate(firestore_key_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
          
def total_field_count_up(field_name) :
    # users 컬렉션의 특정 사용자 문서(id)에 접근
    total_ref = db.collection('statistics').document("total_count")

    total_ref.update({
    'total_access' : firestore.Increment(1),        
    field_name: firestore.Increment(1)
})
      
# 특정 사용자 ID에 로그 저장하는 함수
def send_log_to_user_firestore(event_result, event_description):
    
    # users 컬렉션의 특정 사용자 문서(id)에 접근
    user_ref = db.collection('users').document('Unknown')
    
    # 현재 UTC 시간의 ISO 8601 형식의 문자열로 변환
    timestamp_iso = datetime.now(timezone.utc).isoformat()  # 예: 2024-10-05T12:34:56.789000+00:00
    
    # 타임스탬프를 역순으로 변환
    timestamp_reversed = timestamp_iso[::-1]  # 문자열을 역순으로 정렬

    # app_logs 하위 컬렉션에 역순 타임스탬프를 문서 이름으로 설정
    log_ref = user_ref.collection('app_logs').document(timestamp_reversed)

    log_data = {
        'event_description': event_description,
        'event_result': event_result,
        'timestamp': datetime.now(timezone.utc)  # 시간대 인식 UTC 타임스탬프
    }
    log_ref.set(log_data)

# 특정 사용자 ID에 오류 로그 저장하는 함수
def send_error_to_user_firestore(error_description):
    
    # users 컬렉션의 특정 사용자 문서(id)에 접근
    user_ref = db.collection('users').document('Unknown')

    # 현재 UTC 시간의 ISO 8601 형식의 문자열로 변환
    timestamp_iso = datetime.now(timezone.utc).isoformat()  # 예: 2024-10-05T12:34:56.789000+00:00
    
    # 타임스탬프를 역순으로 변환
    timestamp_reversed = timestamp_iso[::-1]  # 문자열을 역순으로 정렬
    
    # 사용자 문서 내 error_logs 하위 컬렉션에 새로운 로그 추가
    log_ref = user_ref.collection('error_logs').document(timestamp_reversed)
    log_data = {
        'error_description': error_description,
        'timestamp': datetime.now(timezone.utc)  # 시간대 인식 UTC 타임스탬프
    }
    log_ref.set(log_data)

def log_error(user_id, error_description) :
     send_log_to_user_firestore(user_id, error_description)