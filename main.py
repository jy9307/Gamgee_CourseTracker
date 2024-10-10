import sys, os, json, time, webbrowser, win32gui, win32con
from bs4 import BeautifulSoup
import requests, re, subprocess

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QFrame, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QFontDatabase
from db_handler import *
from file_handler import *

##------------- GUI elements --------------

class CourseTrackHome(QWidget):
    def __init__(self):
        super().__init__()
        self.load_account_settings()   

        # 기존 설정 확인
        self.saved_id = saved_id
        self.save_account = save_account

        # 윈도우 기본 설정
        self.setWindowTitle('Gamgee v0.42-beta')
        self.setStyleSheet("background-color: #f0f0f0;")  # 배경색 설정


        # 레이아웃 설정
        main_layout = QVBoxLayout()

        self.combo_label = QLabel('현재까지 본 프로그램은 <중앙교육연수원>의 연수만을 지원합니다.')
        self.combo_label.setStyleSheet("font-size: 15px;")
        main_layout.addWidget(self.combo_label)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        content_layout = QHBoxLayout()

        manual_layout = QVBoxLayout()

        manual_title = QLabel("수동 접속 모드")
        manual_layout.addWidget(manual_title)

        manual_tutor_1 = QLabel("1. <크롬 실행> 버튼을 눌러 크롬을 켠다.")
        manual_tutor_2 = QLabel("2. 중앙교육연수원에서 직접 원하는 강의를 찾는다.")
        manual_tutor_3 = QLabel("3. 강의 '이어보기'버튼을 누른 뒤, <자동 수강> 버튼을 누른다.")
    
        # 폰트 일괄 설정
        label_font = "font-size: 14px;"
        manual_tutor_1.setStyleSheet(label_font)
        manual_tutor_2.setStyleSheet(label_font)
        manual_tutor_3.setStyleSheet(label_font)

        manual_layout.addWidget(manual_tutor_1)
        manual_layout.addWidget(manual_tutor_2)
        manual_layout.addWidget(manual_tutor_3)

        manual_layout.addStretch(1)
        

        self.manual_chrome_run_button = QPushButton('크롬 실행', self)
        self.manual_chrome_run_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 18px;
                background-color: #4CAF50;  /* 버튼 기본 색상 */
                color: white;
                border: none;
                border-radius: 5px;  /* 살짝 둥근 모서리 */
            }
            QPushButton:hover {
        background-color: #45a049;  /* 호버 시 색상 변화 */
    }
        """)
        self.manual_chrome_run_button.setFixedSize(330, 60)
        self.manual_chrome_run_button.clicked.connect(self.manual_chrome_run)

        self.manual_chrome_auto_button = QPushButton('자동 수강', self)
        self.manual_chrome_auto_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 18px;
                background-color: #2196F3;  /* 버튼 기본 색상 */
                color: white;
                border: none;
                border-radius: 5px;  /* 살짝 둥근 모서리 */
            }
            QPushButton:hover {
        background-color: #1976D2;  /* 호버 시 색상 변화 */
    }
        """)
        self.manual_chrome_auto_button.setFixedSize(330, 60)
        self.manual_chrome_auto_button.clicked.connect(self.manual_chrome_auto)

        manual_layout.addWidget(self.manual_chrome_run_button)
        manual_layout.addWidget(self.manual_chrome_auto_button)

        content_layout.addLayout(manual_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(line)

        auto_layout = QVBoxLayout()

        auto_title = QLabel("완전 자동 모드")
        auto_layout.addWidget(auto_title)
        auto_layout.addStretch(1)

        # 강의 제목과 입력 창을 세로로 배치
        course_layout = QGridLayout()

        self.course_label = QLabel('강의 제목')
        course_layout.addWidget(self.course_label, 0, 0)

        self.course_input = QLineEdit(self)
        self.course_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                background-color: #ffffff;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
        """)
        course_layout.addWidget(self.course_input, 0, 1)

        self.course_help_label = QLabel('강의 제목에 포함된 단어 하나를 적어주세요. ex) 다문화, 안전')
        self.course_help_label.setStyleSheet("font-size: 12px;")
        course_layout.addWidget(self.course_help_label, 1, 0, 1, 2)

        # 메인 레이아웃에 추가
        auto_layout.addLayout(course_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 입력 창 그리드 레이아웃 설정
        account_grid_layout = QGridLayout()

        # ID 입력 부분
        self.id_label = QLabel('ID')
        self.id_input = QLineEdit(self)
        self.id_input.setStyleSheet("""
        QLineEdit {
            padding: 5px;
            font-size: 14px;
            background-color: #ffffff;
            border: 2px solid #cccccc;
            border-radius: 5px;
        }
        """)

        account_grid_layout.addWidget(self.id_label, 0, 0)
        account_grid_layout.addWidget(self.id_input, 0, 1)

        # PW 입력 부분
        self.pw_label = QLabel('PW')
        self.pw_input = QLineEdit(self)
        self.pw_input.setStyleSheet("""
        QLineEdit {
            padding: 5px;
            font-size: 14px;
            background-color: #ffffff;
            border: 2px solid #cccccc;
            border-radius: 5px;
        }
        .
        """)
        self.pw_input.setEchoMode(QLineEdit.Password)  # 비밀번호 숨김 설정
        account_grid_layout.addWidget(self.pw_label, 1, 0)
        account_grid_layout.addWidget(self.pw_input, 1, 1)

        # 실행 버튼 부분 (우측 배치)
        self.run_button = QPushButton('실행', self)
        self.run_button.setFont(QFont("Pretendard-Regular", 12, QFont.Bold))
        self.run_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.run_button.setFixedHeight(60)  # 버튼 높이 설정
        self.run_button.clicked.connect(self.run_button_clicked)

        # Enter 또는 Return 키로 버튼을 실행할 수 있도록 설정
        self.run_button.setDefault(True)

        # 버튼을 그리드에서 두 줄 높이로 설정
        account_grid_layout.addWidget(self.run_button, 0, 2, 2, 1)

        # 메인 레이아웃에 그리드 레이아웃 추가
        auto_layout.addLayout(account_grid_layout)

        account_setting_grid_layout = QGridLayout()

        # 계정 관련 설정 체크박스
        self.saved_id_checkbox = QCheckBox('아이디 기억하기')
        if self.save_account:
            self.saved_id_checkbox.setChecked(True)
            self.id_input.setText(self.saved_id)
        # 체크박스가 활성화되거나 비활성화될 때 이벤트 발생
        self.saved_id_checkbox.stateChanged.connect(self.checkbox_changed)

        account_setting_grid_layout.addWidget(self.saved_id_checkbox, 0, 0)
        self.show_password_checkbox = QCheckBox('비밀번호 보이기')
        self.state = self.show_password_checkbox.checkState()
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        account_setting_grid_layout.addWidget(self.show_password_checkbox, 0, 1)

        # 메인 레이아웃에 추가
        auto_layout.addLayout(account_setting_grid_layout)
        
        content_layout.addLayout(auto_layout)

        main_layout.addLayout(content_layout)
        # 메인 레이아웃 설정
        self.setLayout(main_layout)

    def load_account_settings(self):    
        """settings.json 파일에서 데이터를 로드하고, saved_id와 save_account 설정"""
        try:
            # JSON 파일 로드
            json_path = load_data('settings.json')
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.saved_id = data.get("coursetrack_id", "")  # 'id'가 없으면 빈 문자열로 처리
                self.save_account = data.get("coursetrack_save_account", False)  # 'save_account'가 없으면 False로 처리
        except FileNotFoundError:
            print("account_setting.json 파일을 찾을 수 없습니다.")
            self.saved_id = ""
            self.save_account = False
        except json.JSONDecodeError:
            print("account_setting.json 파일 형식이 잘못되었습니다.")
            self.saved_id = ""
            self.save_account = False 

    def update_status(self, message):
        self.progress_dialog.update_status(message)

    def update_saved_id(self, save, id_value=None):
        data = load_setting()
        if save:
            data["coursetrack_id"] = id_value
            data["coursetrack_save_account"] = True
        else:
            data["coursetrack_id"] = None
            data["coursetrack_save_account"] = False
        save_setting(data)

    def checkbox_changed(self, state):
        save = state == Qt.Checked
        id_value = self.id_input.text() if save else None
        self.update_saved_id(save, id_value)

    def run_button_clicked(self):
        #계정 입력 상태 확인
        id_input = self.id_input.text()
        pw_input = self.pw_input.text()
        course_name = self.course_input.text()

        if not id_input or not pw_input:
            QMessageBox.warning(self, "계정 입력 오류", "아이디와 비밀번호를 모두 입력했는지 확인해주세요!")
            return
        
        if not course_name:
            QMessageBox.warning(self, '수강 과정 입력', "수강하고 싶은 강의를 적었는지 확인해주세요!")
            return
        
        # '아이디 저장' 체크박스 상태에 따라 아이디를 저장하거나 삭제
        save = self.saved_id_checkbox.isChecked()
        id_value = id_input if save else None
        self.update_saved_id(save, id_value)

        # 메인 창 숨기기
        self.hide()


        # CourseTrack 설정
        self.tracker = CourseTrack(id = id_input, pw = pw_input, course_name = course_name)
        
        # ProgressDialog 설정
        self.progress_dialog = ProgressDialog(parent=self, thread=self.tracker)
        self.progress_dialog.setWindowModality(Qt.NonModal)

        # 시그널 연결
        self.progress_dialog.speed_signal.connect(self.tracker.speed_change)
        self.progress_dialog.finished.connect(self.show_main_window)  # ProgressDialog가 닫힐 때 메인 창 표시

        #로그 기록
        total_field_count_up("total_coursetrack_count")


        self.tracker.start()
        self.progress_dialog.exec_()

    def show_main_window(self):
        self.show()

    def manual_chrome_run(self) :

        # Chrome 실행 파일 경로를 정확하게 지정하십시오
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 실제 Chrome 설치 경로로 수정
        # chrome.exe 파일이 존재하는지 확인
        if not os.path.exists(chrome_path):
            QMessageBox.warning(self,"크롬 설치", "본 프로그램 작동을 위해서 크롬 설치가 필요합니다.")
            return
        subprocess.Popen([chrome_path, '--remote-debugging-port=9222', '--user-data-dir=C:\\chrometemp'])

    def manual_chrome_auto(self) :
        # CourseTrack 스레드 생성 및 시작
        self.tracker = CourseTrack(manual=True)
        self.tracker.progress_signal.connect(self.update_status)

        # ProgressDialog 설정
        self.progress_dialog = ProgressDialog(thread=self.tracker)

        # 시그널 연결
        self.progress_dialog.speed_signal.connect(self.tracker.speed_change)

        #로그 기록
        total_field_count_up("total_coursetrack_count")

        self.tracker.start()
        self.progress_dialog.exec_()

    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.pw_input.setEchoMode(QLineEdit.Normal)
        else:
            self.pw_input.setEchoMode(QLineEdit.Password)

class ProgressDialog(QDialog):
    speed_signal = pyqtSignal(str)

    def __init__(self, thread, parent=None):
        super().__init__(parent)
        self.thread = thread
        self.thread.progress_signal.connect(self.update_status)
        self.thread.error_signal.connect(self.handle_error)
        self.setWindowTitle("진행 상황")

        icon_path = load_data('gamgee_icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        
        # QDialog에 최소화 및 최대화 버튼 추가
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout()

        # '현재 프로그램 작동 현황' 라벨 추가 및 스타일링
        self.title_label = QLabel('현재 프로그램 작동 현황')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
            }
        """)
        main_layout.addWidget(self.title_label)

        # 진행 상황 표시 영역을 위한 컨테이너 위젯 생성
        status_container = QWidget()
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_container.setLayout(status_layout)
        status_container.setStyleSheet("""
            QWidget {
                background-color: #ededed;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        # 진행 상황을 표시할 라벨
        self.status_label = QLabel('작동 준비 중...')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #333333;
            }
        """)
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_container)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # '화면 위치 조정하기' 라벨 추가 및 스타일링
        self.window_position_label = QLabel('화면 위치 조정하기')
        self.window_position_label.setAlignment(Qt.AlignCenter)
        self.window_position_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
            }
        """)
        main_layout.addWidget(self.window_position_label)

        # 화면 숨김 및 드러내기 버튼 레이아웃
        window_handle_layout = QHBoxLayout()

        # 숨기기 버튼
        self.hide_button = QPushButton('화면 숨기기')
        self.hide_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 16px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1c75bc;
            }
        """)
        self.hide_button.clicked.connect(self.thread.hide_browser)

        # 다시 드러내기 버튼
        self.restore_button = QPushButton('다시 드러내기')
        self.restore_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 16px;
                background-color: #6ac259;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4caf50;
            }
        """)
        self.restore_button.clicked.connect(self.thread.restore_browser)

        window_handle_layout.addWidget(self.hide_button)
        window_handle_layout.addWidget(self.restore_button)

        main_layout.addLayout(window_handle_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 옵션 안내 라벨 스타일링
        self.setting_label = QLabel("옵션 설정")
        self.setting_label.setAlignment(Qt.AlignCenter)
        self.setting_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
            }
        """)

        self.setting_info_label = QLabel("※ 아래 옵션은 <다음 강의>가 시작될 때 적용됩니다.")
        self.setting_info_label.setAlignment(Qt.AlignCenter)
        self.setting_info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555555;
            }
        """)
        main_layout.addWidget(self.setting_label)
        main_layout.addWidget(self.setting_info_label)

        # 자동 음소거 체크박스
        self.mute_check = QCheckBox('자동 음소거')
        self.mute_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #333333;
            }
        """)
        self.mute_check.stateChanged.connect(self.thread.mute_browser_request)
        main_layout.addWidget(self.mute_check)

        # 속도 조절 레이아웃
        speed_dropdown_layout = QHBoxLayout()
        self.speed_label = QLabel("재생 속도 조절:")
        self.speed_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
            }
        """)
        speed_dropdown_layout.addWidget(self.speed_label)

        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["0.8x", "1.0x", "1.2x", "1.5x"])
        self.speed_dropdown.setCurrentIndex(1)
        self.speed_dropdown.currentIndexChanged.connect(self.emit_speed)

        # 재생 속도 조절 콤보박스 스타일링
        self.speed_dropdown.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                min-width: 80px;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                selection-background-color: #4a90e2;
                selection-color: white;
            }
        """)
        speed_dropdown_layout.addWidget(self.speed_dropdown)

        main_layout.addLayout(speed_dropdown_layout)

        # 중지 버튼
        self.stop_button = QPushButton('중지')
        self.stop_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 14px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.stop_button.clicked.connect(self.stop_program)
        main_layout.addWidget(self.stop_button)

        self.setLayout(main_layout)

    # 시그널을 받아서 진행 상황 업데이트
    def update_status(self, status):
        self.status_label.setText(status)  # 전달받은 메시지를 라벨에 표시

    def handle_error(self, error_message):
        # QDialog가 아직 열려 있다면 닫음
        if self.isVisible():  # QDialog가 열려 있는지 확인
            self.close()      # QDialog를 닫음
        # 오류 메시지 표시
        QMessageBox.critical(self, "오류 발생", error_message)

    def emit_speed(self) :
        self.speed_signal.emit(self.speed_dropdown.currentText())

    # 프로그램 중지
    def stop_program(self):
        self.status_label.setText("안전하게 종료 중...")
        QApplication.processEvents()  # 이벤트 루프에 제어권을 넘김
        
        self.thread.stop()
        self.thread.quit()
        self.thread.wait()
        self.reject()  # 프로그램 종료   

class CourseTrack(QThread) :

    progress_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)  # 에러 시그널 추가

    def __init__(self, id=None, pw=None, course_name=None, manual=False) -> None:
        super().__init__()
        self.id = id
        self.pw = pw
        self.course_name = course_name
        self.manual = manual
        self._is_running = True
        self.mute_mode = False
        self.play_speed = '1.0x'
        
        options = webdriver.ChromeOptions()

        if self.manual :
            options.add_experimental_option('debuggerAddress', 'localhost:9222')

        else :
            # 자동화 메시지 제거 설정
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

        # 브라우저 윈도우 사이즈
        options.add_argument('window-size=1920x1080')

        # 사람처럼 보이게 하는 옵션들
        options.add_argument("disable-gpu")   # 가속 사용 x
        options.add_argument("lang=ko_KR")    # 가짜 플러그인 탑재
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정

        # 드라이버 위치 경로 입력
        self.driver = webdriver.Chrome(options=options)

        # navigator.webdriver 속성 삭제
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

##------------- Tools --------------

    def pass_quiz(self) :
        print("checking quiz....")
        quiz_btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lxPlayerIframe"]/div[2]')))
        if quiz_btn :
            quiz_btn.click()
        next_btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-btn"]')))
        next_btn.click()

    def check_running(self):
        if not self._is_running:
            print("Thread Stopped")  # 예외를 발생시키지 않고 종료 알림
            return False  # 작업을 중단할 수 있도록 False 반환
        return True  # 계속 진행

    def countdown_timer(self, seconds):
        for remaining in range(seconds, 0, -1):
            self.progress_signal.emit(f"남은 시간: {remaining}초")
    
            time.sleep(1)
        self.progress_signal.emit("타이머 종료!")
    
    def hide_browser(self) :

        # 현재 브라우저 위치 저장
        self.window_position = self.driver.get_window_position()
        
        # 브라우저를 화면 밖으로 이동
        self.driver.set_window_position(-3000, 0)

    def find_window_by_title(self,title):
        hwnd = None
        def enum_windows_callback(handle, _):
            nonlocal hwnd
            window_title = win32gui.GetWindowText(handle)
            if title in window_title:  # 제목이 포함된 창을 찾기
                hwnd = handle
        win32gui.EnumWindows(enum_windows_callback, None)
        return hwnd

    def restore_browser(self) :
        if hasattr(self, 'window_position'):
            x = self.window_position['x']
            y = self.window_position['y']
            self.driver.set_window_position(x, y)
        else:
            # 위치가 저장되어 있지 않으면 기본 위치로 설정
            self.driver.set_window_position(500, 0)

        # Selenium 창의 제목을 가져옴
        window_title = self.driver.title
        print(f"찾고 있는 창 제목: {window_title}")

        # EnumWindows를 사용하여 창 핸들을 얻음
        hwnd = self.find_window_by_title(window_title)

        if hwnd:
            print(f"창 핸들: {hwnd}")
            # 창을 최상단으로 설정
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0)
        else:
            print("창 핸들을 찾을 수 없습니다.")
    
    def mute_browser_request(self):
        self.mute_mode = True  # 음소거 신호가 들어오면 상태를 True로 변경

    def mute_browser(self) :
        self.progress_signal.emit("음소거 버튼 찾는 중...")
        print("setting mute....")
        self.show_player()
        mute_btn = WebDriverWait(self.driver, 10).until(
            EC.any_of(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[9]/div[1]/button')),
                EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[10]/div[1]/button')),
            )
        )
        mute_btn.click()
        self.progress_signal.emit("음소거 설정 완료!")
        print("setting mute complete")

    def speed_change(self, speed_signal) :
        self.play_speed = speed_signal
        print(f"재생 속도가 {self.play_speed}로 변경되었습니다.")

    def show_player(self) :
        print("checking player....")
        retries = 3
        for _ in range(retries):
            try:
                print("finding player...")
                # Wait for the video player to be present
                self.video_player = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'lx-player'))
                )
                # Ensure the video player is visible and enabled
                if self.video_player.is_displayed() and self.video_player.is_enabled():
                    break  # Success
            except Exception as e:
                print(f"Error occurred: {e}, retrying...")
                time.sleep(1)
        else:
            print("Failed to find the video player after retries.")
            return
        print("showing control bar...")
        # Trigger mouseover using JavaScript
        self.driver.execute_script("""
            var player = arguments[0];
            var event = new MouseEvent('mouseov er', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            player.dispatchEvent(event);
        """, self.video_player)

    def cleanup(self):
        # Safely quit the driver if it's still active
        try:
            if self.driver:
                print("driver quit...")
                self.driver.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")

        if self.isRunning():  # self가 QThread일 경우
            try:
                print("QThread quit...")
                self.terminate()  # 강제 종료
            except Exception as e:
                print(f"Error while terminating the thread: {e}")

    def speed_control(self) :

        if self.play_speed !='1.0x' :
            print("changing play speed....")
            self.show_player()

            # 1. 버튼 클릭
            button_xpath = '//*[@id="lx-player"]/div[10]/div[9]/button'
            wait = WebDriverWait(self.driver, 10)
            button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button.click()

            # 2. 하위 요소 중에서 self.play_speed와 일치하는 텍스트를 가진 요소 클릭
            options_xpath = '//*[@id="lx-player"]/div[10]/div[9]/div[2]//span'  # 하위 element들 중 텍스트를 포함하는 요소의 XPath
            options = wait.until(EC.presence_of_all_elements_located((By.XPATH, options_xpath)))

            # 3. 각 요소를 순회하며 텍스트가 self.play_speed와 일치하는 요소 찾기
            for option in options:
                if option.text == self.play_speed:
                    option.click()  # self.play_speed와 일치하는 요소를 클릭
                    break

    def play_button_click(self) :
        try : 
            time.sleep(1)
            WebDriverWait(self.driver, 500).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'vjs-loading-spinner'))
        )
            #퀴즈 페이지 아닐 경우 재생 버튼 나올때까지 기다려서 클릭
            play_button = WebDriverWait(self.driver, 20).until(
                EC.any_of(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/button')),
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[4]/button[2]'))
            ))
            play_button.click()
        except Exception as e :
            send_error_to_user_firestore(f"{e}")
            self.error_signal.emit(f"로그인 중 오류 발생: {e}")  # 에러 시그널 emit
            self.cleanup()

    def stop_button_click(self) :
        try :
            time.sleep(1)
            # 로딩 스피너가 사라질 때까지 대기
            WebDriverWait(self.driver, 500).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'vjs-loading-spinner'))
            )

            stop_button =  WebDriverWait(self.driver, 200).until(
                    EC.any_of(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player_html5_api"]')),
                ))
            stop_button.click()
        except Exception as e :
            send_error_to_user_firestore(f"{e}")
            self.error_signal.emit(f"로그인 중 오류 발생: {e}")  # 에러 시그널 emit
            self.cleanup()
##------------- Thread process --------------

    def log_in(self):
        if not self.check_running(): 
            return

        try:
            print("loging in....")
            self.driver.get('https://www.neti.go.kr/system/login/login.do')
            self.hide_browser()

            # Create a WebDriverWait object
            wait = WebDriverWait(self.driver, 10)  # Waits up to 10 seconds for each element

            # Find and interact with the login elements
            wait.until(EC.presence_of_element_located((By.NAME, 'userInputId'))).send_keys(self.id)
            wait.until(EC.presence_of_element_located((By.NAME, 'userInputPw'))).send_keys(self.pw)
            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section/form/div/div/a'))).click()

            print("Login successful and redirected to the main page.")

        except UnexpectedAlertPresentException as UE:
            # unexpected alert 발생 시 처리
            try:
                alert = self.driver.switch_to.alert  # Alert 객체로 스위치
                alert_text = alert.text  # 알림 텍스트 가져오기

                # 사용자에게 오류 메시지 전송                
                print(alert_text)
                send_error_to_user_firestore(f"로그인 중 오류 발생: Alert Text: {alert_text}")
                self.error_signal.emit(f"로그인 중 오류 발생: {alert_text}")
                self.cleanup()
            except Exception as e:
                print(f"Error handling alert: {e}")
                self.error_signal.emit(f"로그인 중 오류 발생: {e}")
                send_error_to_user_firestore(f"Error handling alert: {e}")
                self.cleanup()
            
        except TimeoutException:
            error_message = "로그인 후 메인 페이지로 이동하지 못했습니다."
            send_error_to_user_firestore(error_message)
            self.error_signal.emit(error_message)
            self.cleanup()
            return  # Exit the method to prevent further execution

        except Exception as e:
            send_error_to_user_firestore(f"{e}")
            self.error_signal.emit(f"로그인 중 오류 발생: {e}")  # 에러 시그널 emit
            self.cleanup()
            return  # Exit the method to prevent further execution
        
    def load_course(self) :
        if not self.check_running(): return
        try :
            time.sleep(1)
            self.driver.get('https://www.neti.go.kr/lh/ms/cs/atnlcListView.do?menuId=1000006046')
            print("loading courses....")

            wait = WebDriverWait(self.driver, 20)  # Waits up to 10 seconds for each element

            course_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='course_list_box type_02']//a[@class='title']")))
            target_text = self.course_name
            target_element = None

            print("강의들 발견!")

            # 요소 중에서 텍스트를 비교하여 원하는 요소 찾기
            for element in course_elements:
            
                if target_text in element.text:
                    target_element = element
                    send_log_to_user_firestore(event_result= "success", event_description = f"강의 수강 : {element.text} ")
                    break
            if target_element:
                self.progress_signal.emit("강의를 찾았습니다!")

                # 2. 해당 요소 하위의 '이어보기' 버튼 클릭
                parent_li = target_element.find_element(By.XPATH, "./../../..")  # li 요소로 거슬러 올라가기
                continue_button = parent_li.find_element(By.XPATH, ".//a[contains(text(), '이어보기') or contains(text(), '학습하기')]")

                
                # '이어보기' 버튼 클릭
                continue_button.click()

                print("이어보기 버튼을 클릭했습니다!")
            else:
                self.progress_signal.emit("강의를 발견하지 못했습니다. 다시 시도해주세요.")
        
        except Exception as e :
            send_error_to_user_firestore(f"{e}")
            self.error_signal.emit(f"로그인 중 오류 발생: {e}")  # 에러 시그널 emit
            self.cleanup()
        
    def handle_course(self) :

        # 기존 창 핸들 저장``
        original_window = self.driver.current_window_handle

        # 모든 창 핸들 가져오기
        WebDriverWait(self.driver, 20).until(lambda d: len(d.window_handles) > 1)
        all_windows = self.driver.window_handles

        # 새로운 창 핸들 찾기 및 전환
        for window_handle in all_windows:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                print(self.driver.title)  # 새 창의 제목 출력
                break
            
        #퀴즈 페이지일 경우 - class가 "quiz-type"이면 우측 하단에 '학습 완료 후 여기를 클릭하세요'가 나온다.
        try :
            self.pass_quiz()

        except :
        #퀴즈 페이지 아닐 경우 재생 버튼 나올때까지 기다려서 클릭
            self.play_button_click()

        while 1 :
            #일시정지
            try:
                # 우선 퀴즈인지 확인한다
                self.progress_signal.emit("퀴즈 화면인지 확인 중...")
                self.pass_quiz()
                continue  # 퀴즈일 경우 루프 계속

            except:
                self.stop_button_click()
                # 퀴즈가 아닐 경우 처리
                try:
                    # 먼저 비디오 플레이어를 찾는다.
                    self.progress_signal.emit("비디오 플레이어 위치 확인 중...")

                    # 음소거 모드가 켜져있을 경우 음소거 버튼을 찾고 클릭한다.
                    if self.mute_mode:
                        self.mute_browser()

                except Exception as e:
                    send_error_to_user_firestore(f"{e}")
                    self.error_signal.emit(f"로그인 중 오류 발생: {e}")  # 에러 시그널 emit
                    self.cleanup()
                            
            try :
                # XPath를 사용하여 비디오 플레이어 요소 찾기
                # ActionChains를 사용하여 마우스를 비디오 플레이어 위로 이동        
                self.progress_signal.emit("영상 길이 찾아내는 중...")
                
                #영상 길이 찾아내기 
                total_time=''

                #재생 속도 조정
                self.speed_control()

                while (total_time == '') or (total_time == '-:-') or (current_time == '') or (current_time == '-:-'):

                    self.progress_signal.emit("영상 길이 찾아내는 중...")

                    total_time = WebDriverWait(self.driver, 3).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="lx-player"]/div[9]/div[4]/span[2]')),
                        EC.presence_of_element_located((By.XPATH, '//*[@id="lx-player"]/div[10]/div[4]/span[2]')),
                    ))
                    total_time = total_time.text.strip()
                    self.progress_signal.emit("현재 시점 찾아내는 중...")
                    current_time = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "vjs-current-time-display"))).text.strip()
                    print(total_time, current_time)

                total_time = total_time.split(":")
                total_time = int(total_time[0])*60 + int(total_time[1])

                current_time = current_time.split(":")
                current_time = int(current_time[0])*60 + int(current_time[1])

                remain_time = total_time-current_time
                
                # 재생속도에 따라 남은 시간 계산
                if self.play_speed != '1.0x' and self.play_speed == '1.2x' :
                    remain_time *= (5/6)
                elif  self.play_speed != '1.0x' and self.play_speed == '1.5x' :
                    remain_time *= (2/3)
                elif  self.play_speed != '1.0x' and self.play_speed == '0.8x' :
                    remain_time *= (5/4)

                #다시 재생
                self.play_button_click()

                self.countdown_timer(int(remain_time)+4)
                    
                #다음 누르기
                element = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="next-btn"]'))
                )
                element.click()
                self.progress_signal.emit("다음 강의 시작!")

            except WebDriverException as e :
                send_error_to_user_firestore(f"{e}")
                self.error_signal.emit(f"로그인 중 오류 발생: {e}")  # 에러 시그널 emit
                self.cleanup()
            
            except Exception as e :
                send_error_to_user_firestore(f"{e}")
                self.error_signal.emit(f"로그인 중 오류 발생: {e}")  # 에러 시그널 emit
                self.cleanup()

    def run(self):
        if self.manual :
            # 수동 모드의 경우, 스레드에서 강의 로드, 강의 처리 메서드 실행
            self.handle_course()

        else :
            # 완전 자동 모드의 경우, 스레드에서 로그인, 강의 로드, 강의 처리 메서드 실행
            self.log_in()
            self.load_course()
            self.handle_course()

    def stop(self) :
        self._is_running = False
        self.driver.quit()
        self.terminate()

def show_update_message(ver):
    msg_box = QMessageBox()
    msg_box.setWindowTitle("업데이트 필요")
    
    # 하이퍼링크를 포함한 HTML 메시지
    msg_box.setText(
        f'''현재 최신 버전은 {ver}입니다!<br><br>
        <a href="https://jy9307.tistory.com/4">업데이트 링크</a>를 클릭하세요.'''
    )
    
    # 하이퍼링크를 활성화하도록 설정
    msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
    
    # 링크를 클릭하면 브라우저로 열리도록 처리
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.buttonClicked.connect(lambda: webbrowser.open("https://jy9307.tistory.com/4"))
    
    msg_box.exec_()

def ver_check(version) : 

    app = QApplication(sys.argv)
    # 요청을 보내 웹 페이지의 HTML 소스를 가져옵니다
    url = 'https://jy9307.tistory.com/4'
    # 웹 페이지 요청
    response = requests.get(url)

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')


    # <div class="hgroup"> 안의 <h1> 태그를 찾기
    hgroup_div = soup.find('div', class_='hgroup')

    # <h1> 태그가 존재할 경우 텍스트 가져오기
    if hgroup_div:
        title = hgroup_div.find('h1').get_text()
        # 정규 표현식으로 '<'와 '>' 사이의 텍스트를 추출
        pattern = r'<(.*?)>'  # '<'와 '>' 사이의 텍스트를 추출하는 정규 표현식
        match = re.search(pattern, title)

        extracted_text = match.group(1)

        if extracted_text == version :
            return
        
        else :
            print("버전 불일치")
            show_update_message(extracted_text)
            sys.exit()

    else :
        return
    
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    ver = """Gamgee v0.42"""
    ver_check(ver)
    app = QApplication(sys.argv)

    icon_path = load_data('gamgee_icon.ico')
    app.setWindowIcon(QIcon(icon_path))

    # 폰트 파일을 애플리케이션에 추가
    font_path = load_data('NanumSquareR.ttf')
    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 12))
    else:
        print("폰트를 로드할 수 없습니다.")

    # JSON 파일 로드
    json_path = load_data('settings.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        save_account = data["coursetrack_save_account"]
        saved_id = data["coursetrack_id"]

    ex = CourseTrackHome()
    ex.show()
    sys.exit(app.exec_())

