def otp_template(username: str, otp: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify your email</title>
</head>
<body style="margin:0; padding:0; background:#eef1f6; font-family:Arial, Helvetica, sans-serif;">

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:32px 16px;">

        <table role="presentation" width="480" cellpadding="0" cellspacing="0"
               style="background:#ffffff; border-radius:12px; overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:#5b3df6; padding:20px; text-align:center;
                       color:#ffffff; font-size:18px; font-weight:bold;">
              WebX Security Check
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="padding:28px 30px 12px; font-size:15px; color:#333333;">
              Hi <b>{username}</b>,
              <p style="color:#666666; font-size:14px; line-height:1.5; margin:8px 0 0;">
                Use this code to sign in. It expires in 10 minutes.
              </p>
            </td>
          </tr>

          <!-- OTP code -->
          <tr>
            <td style="padding:0 30px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f6f4ff; border:1px dashed #8a63ff; border-radius:10px;">
                <tr>
                  <td align="center" style="padding:18px;">
                    <span style="font-size:34px; letter-spacing:8px; font-weight:bold;
                                 color:#2d2350; font-family:'Courier New', monospace;">
                      {otp}
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer note -->
          <tr>
            <td style="padding:18px 30px 26px; font-size:12px; color:#999999;">
              Didn't request this? Ignore this email or secure your account.
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>
"""