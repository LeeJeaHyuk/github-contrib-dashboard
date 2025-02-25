import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os

# 🔹 Matplotlib 한글 폰트 자동 설정 함수
def set_korean_font():
    system_name = platform.system()
    font_path = None

    # 시스템별 기본 폰트 경로 설정
    if system_name == "Windows":
        font_candidates = ["malgun.ttf", "gulim.ttf"]  # Windows 기본 한글 폰트
    elif system_name == "Darwin":  # macOS
        font_candidates = ["AppleGothic.ttf"]
    else:  # Linux (Ubuntu, Debian 등)
        font_candidates = ["NanumGothic.ttf", "UnDotum.ttf"]

    # 시스템에서 사용 가능한 한글 폰트 찾기
    system_fonts = fm.findSystemFonts(fontpaths=None)
    for font_candidate in font_candidates:
        for font in system_fonts:
            if font_candidate in font:
                font_path = font
                break
        if font_path:
            break

    # 폰트를 찾았을 경우 Matplotlib에 적용
    if font_path:
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc("font", family=font_name)
        print(f"✅ 한글 폰트 적용: {font_name}")
    else:
        print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 설정을 사용합니다.")

# 🔹 한글 폰트 적용
set_korean_font()
