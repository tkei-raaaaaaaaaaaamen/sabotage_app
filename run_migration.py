import os
import django
import subprocess

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# マイグレーションを実行
try:
    result = subprocess.run(['python', 'manage.py', 'migrate'], 
                          capture_output=True, text=True, cwd=r'c:\Users\Takahashi\Desktop\授業２\前期\Django\sabotage_app')
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except Exception as e:
    print("Error:", e)
