import secrets
import string

def generate_secret_key(length=50):
    """Django用のランダムなSECRET_KEYを生成"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("Generated SECRET_KEY:")
    print(secret_key)
    print("\nRender.comの環境変数に以下を設定してください:")
    print(f"SECRET_KEY={secret_key}")
