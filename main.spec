# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py','db_handler.py', 'file_handler.py'],  # 실행할 스크립트들
    pathex=[],  # 추가할 모듈 경로가 필요하지 않으면 비워둘 수 있음
    binaries=[],  # 외부 바이너리가 없으면 비워둠
    datas=[
        ('chromedriver.exe', '.'), 
        ('gamgee_icon.ico', '.'), 
        ('NanumSquareR.ttf', '.'), 
        ('settings.json', '.'),
        ('fs_gamgee.json','.')
           ],
    hiddenimports=[],  # 숨겨진 의존 모듈이 없다면 비워둠
    hookspath=[],  # 후크 경로가 필요하지 않으면 비워둠
    excludes=[],  # 제외할 모듈이 없으면 비워둠
    noarchive=False,  # 모든 파일을 하나의 아카이브로 묶기 (보통 False로 설정)
    optimize=1,  # 최적화 레벨: 0(없음), 1(일부), 2(전체)
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gamgee',  # 실행 파일 이름
    debug=False,  # 디버그 모드 비활성화
    strip=False,  # 바이너리 스트리핑 비활성화
    upx=True,  # UPX로 압축, UPX가 없으면 False로 설정
    console=False,  # GUI 애플리케이션의 경우 False, 콘솔 애플리케이션은 True
    icon='gamgee_icon.ico',  # 아이콘 설정
    onefile=True  # 하나의 실행 파일로 묶음
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='gamgee'
)