import subprocess
import os
import time

# .streamlit 디렉토리 생성
os.makedirs(os.path.expanduser('~/.streamlit'), exist_ok=True)

# config.toml 작성
config_path = os.path.expanduser('~/.streamlit/config.toml')
config_content = """[client]
showErrorDetails = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[logger]
level = "error"

[server]
port = 8501
headless = true
"""

with open(config_path, 'w', encoding='utf-8') as f:
    f.write(config_content)

print("[OK] Streamlit config created")

# credentials.toml 작성 (이메일 설정)
creds_path = os.path.expanduser('~/.streamlit/credentials.toml')
with open(creds_path, 'w', encoding='utf-8') as f:
    f.write("")

print("[OK] Credentials file created")

# 프로세스 실행
cmd = ['python', '-m', 'streamlit', 'run', 'dashboard.py', '--server.port=8501']

print("[OK] Starting Streamlit dashboard...")
print("[INFO] Open browser: http://localhost:8501")
print("")

# stdin을 DEVNULL로 설정하고 프롬프트 우회
proc = subprocess.Popen(
    cmd,
    stdin=subprocess.DEVNULL,
    cwd='c:\\scl'
)

proc.wait()
