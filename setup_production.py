#!/usr/bin/env python
"""
本番環境用のマイグレーション・管理スクリプト
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    
    from django.contrib.auth.models import User
    
    # スーパーユーザーを作成
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Superuser created: username=admin, password=admin123')
    else:
        print('ℹ️ Superuser already exists')
    
    print('🚀 Setup completed successfully!')
