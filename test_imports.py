import traceback
import sys

try:
    print("Testing imports...")
    
    print("1. Testing schemas...")
    from app.models.schemas import IncomingRequest, APIResponse
    print("   ✓ Schemas OK")
    
    print("2. Testing session_manager...")
    from app.services.session_manager import session_manager
    print("   ✓ Session Manager OK")
    
    print("3. Testing intelligence...")
    from app.services import intelligence
    print("   ✓ Intelligence OK")
    
    print("4. Testing gemini_agent...")
    from app.services import gemini_agent
    print("   ✓ Gemini Agent OK")
    
    print("5. Testing reporting...")
    from app.services import reporting
    print("   ✓ Reporting OK")
    
    print("6. Testing endpoints...")
    from app.api.endpoints import router
    print("   ✓ Endpoints OK")
    
    print("7. Testing main app...")
    from app.main import app
    print("   ✓ Main App OK")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Import failed!")
    traceback.print_exc()
    sys.exit(1)
