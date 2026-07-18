import os
import httpx
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

async def send_email_link(to: str, subject: str, link: str, link_text: str) -> dict:
    if not RESEND_API_KEY:
        print("RESEND_API_KEY is not defined in backend .env")
        return {"success": False, "error": "Email provider not configured."}

    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{subject}</title>
      <style>
        body {{
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background-color: #09090b;
          color: #f4f4f5;
          padding: 32px;
          margin: 0;
        }}
        .container {{
          max-width: 580px;
          margin: 0 auto;
          background-color: #18181b;
          border: 1px solid #27272a;
          border-radius: 8px;
          padding: 32px;
        }}
        h1 {{
          font-size: 20px;
          font-weight: 600;
          color: #ffffff;
          margin-top: 0;
          border-bottom: 1px solid #27272a;
          padding-bottom: 16px;
        }}
        p {{
          font-size: 14px;
          line-height: 24px;
          color: #a1a1aa;
        }}
        .button-container {{
          margin: 24px 0;
        }}
        .button {{
          display: inline-block;
          background-color: #10b981;
          color: #ffffff !important;
          text-decoration: none;
          font-size: 14px;
          font-weight: 500;
          padding: 12px 24px;
          border-radius: 6px;
        }}
        .footer {{
          margin-top: 32px;
          border-top: 1px solid #27272a;
          padding-top: 16px;
          font-size: 12px;
          color: #71717a;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h1>MY AI TASK — Automation Platform</h1>
        <p>Hello,</p>
        <p>You requested a secure link for your account. Please click the button below to proceed:</p>
        <div class="button-container">
          <a href="{link}" class="button" target="_blank">{link_text}</a>
        </div>
        <p>If you did not request this link or email, you can safely ignore this message.</p>
        <div class="footer">
          Sent securely via Resend from MY AI TASK (myaitask.io).
        </div>
      </div>
    </body>
    </html>
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "MY AI TASK <onboarding@resend.dev>",
                    "to": [to],
                    "subject": subject,
                    "html": email_html,
                }
            )
            
            res_json = response.json()
            if not response.is_success:
                print("Resend API call failed:", res_json)
                return {"success": False, "error": res_json.get("message", "Resend provider error.")}
            
            return {"success": True}
    except Exception as e:
        print("Error sending email link via Resend:", e)
        return {"success": False, "error": str(e) or "Network error sending email."}
