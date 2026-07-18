import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_anon_key:
    raise ValueError("Missing Supabase environment variables in backend")

supabase: Client = create_client(supabase_url, supabase_anon_key)

def create_scoped_client(token: str) -> Client:
    options = {
        "global": {
            "headers": {
                "Authorization": f"Bearer {token}"
            }
        }
    }
    # Note: create_client takes url, key, options dictionary in Python SDK.
    from supabase.client import ClientOptions
    client_options = ClientOptions(
        headers={"Authorization": f"Bearer {token}"}
    )
    return create_client(supabase_url, supabase_anon_key, options=client_options)
