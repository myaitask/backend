import dotenv from 'dotenv';
dotenv.config();

const RESEND_API_KEY = process.env.RESEND_API_KEY;

export async function sendEmailLink(
  to: string,
  subject: string,
  link: string,
  linkText: string
): Promise<{ success: boolean; error?: string }> {
  if (!RESEND_API_KEY) {
    console.error('RESEND_API_KEY is not defined in backend .env');
    return { success: false, error: 'Email provider not configured.' };
  }

  const emailHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>${subject}</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background-color: #09090b;
          color: #f4f4f5;
          padding: 32px;
          margin: 0;
        }
        .container {
          max-width: 580px;
          margin: 0 auto;
          background-color: #18181b;
          border: 1px solid #27272a;
          border-radius: 8px;
          padding: 32px;
        }
        h1 {
          font-size: 20px;
          font-weight: 600;
          color: #ffffff;
          margin-top: 0;
          border-bottom: 1px solid #27272a;
          padding-bottom: 16px;
        }
        p {
          font-size: 14px;
          line-height: 24px;
          color: #a1a1aa;
        }
        .button-container {
          margin: 24px 0;
        }
        .button {
          display: inline-block;
          background-color: #10b981;
          color: #ffffff !important;
          text-decoration: none;
          font-size: 14px;
          font-weight: 500;
          padding: 12px 24px;
          border-radius: 6px;
        }
        .footer {
          margin-top: 32px;
          border-top: 1px solid #27272a;
          padding-top: 16px;
          font-size: 12px;
          color: #71717a;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>MY AI TASK — Automation Platform</h1>
        <p>Hello,</p>
        <p>You requested a secure link for your account. Please click the button below to proceed:</p>
        <div class="button-container">
          <a href="${link}" class="button" target="_blank">${linkText}</a>
        </div>
        <p>If you did not request this link or email, you can safely ignore this message.</p>
        <div class="footer">
          Sent securely via Resend from MY AI TASK (myaitask.io).
        </div>
      </div>
    </body>
    </html>
  `;

  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'MY AI TASK <onboarding@resend.dev>',
        to: [to],
        subject: subject,
        html: emailHtml,
      }),
    });

    const resJson: any = await response.json();

    if (!response.ok) {
      console.error('Resend API call failed:', resJson);
      return { success: false, error: resJson.message || 'Resend provider error.' };
    }

    return { success: true };
  } catch (err: any) {
    console.error('Error sending email link via Resend:', err);
    return { success: false, error: err.message || 'Network error sending email.' };
  }
}
