import os, sys, json, shutil

def get_resource_path(relative_path):
    """PyInstaller 환경과 개발 환경에서 리소스 파일의 경로를 반환합니다."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def get_user_data_directory():
    """사용자의 데이터 디렉토리를 반환합니다."""
    if sys.platform == 'win32':
        # Windows의 경우 %APPDATA%\Gamgee 사용
        user_data_dir = os.path.join(os.getenv('APPDATA'), 'Gamgee_CourseTracker')
    else:
        # 다른 OS의 경우 ~/.gamgee 사용
        user_data_dir = os.path.join(os.path.expanduser('~'), '.Gamgee_CourseTracker')
    os.makedirs(user_data_dir, exist_ok=True)
    return user_data_dir

def load_data(filename):
    """사용자 데이터 디렉토리에서 파일을 로드하거나, 없으면 리소스 디렉토리에서 복사합니다."""
    user_data_dir = get_user_data_directory()
    user_file_path = os.path.join(user_data_dir, filename)

    if os.path.exists(user_file_path):
        print(f"사용자 경로에서 데이터 로드: {user_file_path}")
        return user_file_path
    else:
        resource_path = get_resource_path(filename)
        print(f"기본 {filename}을 사용자 디렉토리로 복사합니다.")
        try:
            shutil.copy(resource_path, user_file_path)
            return user_file_path
        except Exception as e:
            print(f"파일 복사 중 오류 발생: {e}")
            return None

##-----------s  etting--------

def load_setting():
    """사용자 데이터 디렉토리에서 설정을 로드합니다."""
    settings_path = load_data('settings.json')
    if settings_path and os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"설정 로드 중 오류 발생: {e}")
            return {}
    else:
        print("설정 파일을 찾을 수 없습니다. 기본 설정을 사용합니다.")
        return {}

def save_setting(data):
    """설정을 사용자 데이터 디렉토리에 저장합니다."""
    user_data_dir = get_user_data_directory()
    settings_path = os.path.join(user_data_dir, 'settings.json')
    try:
        with open(settings_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"설정이 저장되었습니다: {settings_path}")
    except Exception as e:
        print(f"설정 저장 중 오류 발생: {e}")