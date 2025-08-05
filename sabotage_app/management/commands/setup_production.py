from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection


class Command(BaseCommand):
    help = 'Setup production database with all necessary tables and superuser'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Setting up production database...")
        
        try:
            # データベース接続を確認
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write("✅ Database connection successful")
            
            # スーパーユーザーを作成
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
                self.stdout.write("✅ Superuser created: admin/admin123")
            else:
                self.stdout.write("ℹ️ Superuser already exists")
                
            self.stdout.write("🚀 Production setup completed successfully!")
            
        except Exception as e:
            self.stdout.write(f"❌ Error during setup: {e}")
            raise
