import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from starlette.middleware.base import BaseHTTPMiddleware
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from src.routes.index import router

load_dotenv()

class HostValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get('x-forwarded-host') or request.headers.get('host')
        if host:
            host = host.split(',')[0].strip()
        hostname = host.split(':')[0] if host else ''
        
        allowed_hosts = ['backend.myaitask.io']
        if os.getenv('NODE_ENV') == 'development' or True: # True since FastAPI runs in dev by default easily or explicit check
            allowed_hosts.extend(['localhost', '127.0.0.1'])
            
        if hostname not in allowed_hosts:
            print(f'[HostValidation Failed] Hostname: "{hostname}", Raw Host: "{request.headers.get("host")}", X-Forwarded-Host: "{request.headers.get("x-forwarded-host")}"')
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "Forbidden",
                    "message": f"Access Denied: Invalid Host. Received: \"{hostname}\""
                }
            )
        response = await call_next(request)
        return response

app = FastAPI()

# Host Validation
app.add_middleware(HostValidationMiddleware)

# Configure CORS
allowed_origins = ['https://www.myaitask.io', 'http://www.myaitask.io']
if os.getenv('NODE_ENV') == 'development' or True: # Simplified for dev
    allowed_origins.extend([
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5001',
        'http://127.0.0.1:5001'
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api")

@app.get("/")
def default_route():
    return "Backend running successfully"

# Exception Handler to mimic old 500 handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": str(exc) if os.getenv('NODE_ENV') == 'development' else None
        }
    )
