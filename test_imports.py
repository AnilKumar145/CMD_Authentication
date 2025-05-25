# Test if imports are working
print("Testing imports...")

try:
    from jose import jwt
    print("✅ jose.jwt imported successfully")
except ImportError as e:
    print(f"❌ Failed to import jose.jwt: {e}")

try:
    from passlib.context import CryptContext
    print("✅ passlib.context imported successfully")
except ImportError as e:
    print(f"❌ Failed to import passlib.context: {e}")

try:
    from fastapi.security import OAuth2PasswordBearer
    print("✅ OAuth2PasswordBearer imported successfully")
except ImportError as e:
    print(f"❌ Failed to import OAuth2PasswordBearer: {e}")

print("Import test complete")