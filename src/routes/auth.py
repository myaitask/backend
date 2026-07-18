from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import re
import random
from src.lib.supabase import supabase, create_scoped_client
from src.lib.email import send_email_link

router = APIRouter()

class SignupRequest(BaseModel):
    email: str
    password: str
    companyName: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ContactRequest(BaseModel):
    organization_id: str
    full_name: str
    phone_number: str

class SendLinkRequest(BaseModel):
    to: str
    subject: str
    link: str
    linkText: str

def get_token(request: Request) -> str:
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required.")
    return auth_header.split(" ")[1]

@router.post("/signup")
async def signup(req: SignupRequest):
    if not req.email or not req.password or not req.companyName:
        return JSONResponse(status_code=400, content={"success": False, "error": "Email, password, and companyName are required."})
    
    try:
        # A. Sign up user via Supabase Auth
        auth_res = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password
        })
        if not auth_res.user:
            return JSONResponse(status_code=400, content={"success": False, "error": "Authentication signup failed."})
        
        # Force-confirm the user's email
        try:
            supabase.rpc('confirm_user_email', {'user_email': req.email}).execute()
        except Exception as e:
            print('Auto-confirm RPC trigger warned, proceeding to login attempt.', e)
            
        # B. Sign in immediately
        login_res = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        if not login_res.user or not login_res.session:
            return JSONResponse(status_code=400, content={"success": False, "error": "Verification pending. Please try logging in directly."})
            
        user = login_res.user
        session = login_res.session
        
        # C. Create scoped client
        user_client = create_scoped_client(session.access_token)
        
        # Create slug
        slug_base = re.sub(r'[^a-z0-9]+', '-', req.companyName.lower().strip())
        slug_base = re.sub(r'(^-|-$)', '', slug_base)
        slug = f"{slug_base}-{random.randint(1000, 9999)}"
        
        # Insert Org
        org_res = user_client.table('organizations').insert({
            'name': req.companyName,
            'slug': slug,
            'status': 'active'
        }).execute()
        
        if not org_res.data:
            print("Error inserting organization")
            return JSONResponse(status_code=500, content={"success": False, "error": "Failed to create workspace organization."})
        
        org_data = org_res.data[0]
        
        # Insert Member
        try:
            user_client.table('organization_members').insert({
                'organization_id': org_data['id'],
                'user_id': user.id,
                'role': 'owner',
                'status': 'active'
            }).execute()
        except Exception as e:
            print('Error creating membership:', e)
            return JSONResponse(status_code=500, content={"success": False, "error": "Failed to establish workspace membership."})
            
        # Insert Profile
        try:
            user_client.table('profiles').insert({
                'id': user.id,
                'full_name': req.companyName
            }).execute()
        except Exception as e:
            print('Profile creation failed but proceeding.', e)
            
        return JSONResponse(status_code=201, content={
            "success": True,
            "message": "Signup successful.",
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email
                },
                "session": {
                    "access_token": session.access_token,
                    "refresh_token": session.refresh_token,
                    "expires_at": session.expires_at
                }
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})


@router.post("/login")
async def login(req: LoginRequest):
    if not req.email or not req.password:
        return JSONResponse(status_code=400, content={"success": False, "error": "Email and password are required."})
        
    try:
        data = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        if not data.user or not data.session:
             return JSONResponse(status_code=401, content={"success": False, "error": "Invalid email or password."})
             
        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Login successful.",
            "data": {
                "user": {
                    "id": data.user.id,
                    "email": data.user.email
                },
                "session": {
                    "access_token": data.session.access_token,
                    "refresh_token": data.session.refresh_token,
                    "expires_at": data.session.expires_at
                }
            }
        })
    except Exception as e:
        return JSONResponse(status_code=401, content={"success": False, "error": str(e) or "Invalid email or password."})


@router.get("/user")
async def get_user(request: Request):
    try:
        token = get_token(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"success": False, "error": e.detail})
        
    try:
        user_client = create_scoped_client(token)
        user_res = user_client.auth.get_user(token)
        if not user_res.user:
            return JSONResponse(status_code=401, content={"success": False, "error": "Invalid or expired session."})
        
        user = user_res.user
        
        member_res = user_client.table('organization_members').select('role, organizations(*)').eq('user_id', user.id).limit(1).execute()
        membership = member_res.data[0] if member_res.data else None
        
        plan_name = 'Trial'
        if membership and 'organizations' in membership and membership['organizations']:
            try:
                org = membership['organizations']
                if type(org) == list: org = org[0]
                sub_res = user_client.table('subscriptions').select('status, subscription_plans(name)').eq('organization_id', org['id']).execute()
                if sub_res.data and len(sub_res.data) > 0:
                    sub_data = sub_res.data[0]
                    if 'subscription_plans' in sub_data and sub_data['subscription_plans']:
                        plans = sub_data['subscription_plans']
                        if type(plans) == list and len(plans) > 0:
                            plan_name = plans[0].get('name', 'Trial')
                        elif type(plans) == dict:
                            plan_name = plans.get('name', 'Trial')
            except Exception as e:
                print('Subscriptions read failed on backend /user', e)
                
        return JSONResponse(status_code=200, content={
            "success": True,
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email
                },
                "membership": {
                    "role": membership['role'],
                    "organizations": {
                        **((membership['organizations'][0] if type(membership['organizations']) == list else membership['organizations']) if membership['organizations'] else {}),
                        "plan": plan_name
                    }
                } if membership else None
            }
        })
    except Exception as e:
        return JSONResponse(status_code=401, content={"success": False, "error": str(e) or "Invalid or expired session."})

@router.get("/dashboard/summary")
async def dashboard_summary(request: Request):
    try:
        token = get_token(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"success": False, "error": e.detail})
        
    try:
        user_client = create_scoped_client(token)
        user_res = user_client.auth.get_user(token)
        if not user_res.user:
            return JSONResponse(status_code=401, content={"success": False, "error": "Invalid or expired session."})
            
        user = user_res.user
        
        member_res = user_client.table('organization_members').select('organization_id, organizations(*)').eq('user_id', user.id).limit(1).execute()
        membership = member_res.data[0] if member_res.data else None
        
        if not membership:
             return JSONResponse(status_code=200, content={
                "success": True,
                "data": {
                  "activeTenant": None,
                  "wabaConnection": None,
                  "dbMetrics": {
                    "totalCalls": "0",
                    "activeAgents": "0",
                    "contactsCount": "0"
                  }
                }
              })
              
        active_tenant = membership['organizations']
        if type(active_tenant) == list: active_tenant = active_tenant[0]
        
        phone_res = user_client.table('phone_numbers').select('*').eq('organization_id', active_tenant['id']).execute()
        phone_data = phone_res.data[0] if phone_res.data else None
        
        contacts_res = user_client.table('contacts').select('*', count='exact').eq('organization_id', active_tenant['id']).execute()
        contacts_count = contacts_res.count
        
        return JSONResponse(status_code=200, content={
            "success": True,
            "data": {
                "activeTenant": active_tenant,
                "wabaConnection": phone_data,
                "dbMetrics": {
                    "scheduledPosts": "18",
                    "activeAutomations": "6",
                    "contactsCount": str(contacts_count) if contacts_count is not None else "0"
                }
            }
        })
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/contacts")
async def create_contact(req: ContactRequest, request: Request):
    try:
        token = get_token(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"success": False, "error": e.detail})
        
    if not req.organization_id or not req.full_name or not req.phone_number:
         return JSONResponse(status_code=400, content={"success": False, "error": "Missing organization_id, full_name, or phone_number."})
         
    try:
        user_client = create_scoped_client(token)
        res = user_client.table('contacts').insert({
            "organization_id": req.organization_id,
            "full_name": req.full_name,
            "phone_number": req.phone_number,
            "tags": ['test-rls']
        }).execute()
        
        return JSONResponse(status_code=201, content={"success": True, "contact": res.data[0] if res.data else None})
    except Exception as e:
        print('Error inserting contact under backend scope:', e)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/send-link")
async def send_link(req: SendLinkRequest, request: Request):
    try:
        token = get_token(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"success": False, "error": e.detail})
        
    if not req.to or not req.subject or not req.link or not req.linkText:
        return JSONResponse(status_code=400, content={"success": False, "error": "Missing parameters (to, subject, link, linkText)."})
        
    try:
        user_client = create_scoped_client(token)
        user_res = user_client.auth.get_user(token)
        if not user_res.user:
            return JSONResponse(status_code=401, content={"success": False, "error": "Invalid session token."})
            
        email_result = await send_email_link(req.to, req.subject, req.link, req.linkText)
        if not email_result.get('success'):
            return JSONResponse(status_code=500, content={"success": False, "error": email_result.get('error', 'Failed to send email.')})
            
        return JSONResponse(status_code=200, content={"success": True, "message": "Email sent successfully."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
