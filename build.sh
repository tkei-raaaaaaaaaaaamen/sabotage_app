#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📊 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️ Force creating database tables..."
# Djangoの標準テーブルを強制作成
python manage.py migrate --run-syncdb

echo "🗄️ Running all migrations..."
python manage.py migrate

echo "👤 Setting up production..."
python manage.py setup_production

echo "🚀 Build completed successfully!"
