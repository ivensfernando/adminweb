import requests
import os

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
BASE_HOST = os.getenv("BASE_HOST", "https://wapi.biidin.com")


def send_invite_via_mailgun(recipient, company_name, secret_code, username, invite_type, subject=None):
    """
    Send an email using the Mailgun SDK.

    :param secret_code:
    :param recipient: The email address to send the email to.
    :param company_name: The company name to include in the email title.
    :return: Response from Mailgun.
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Read the HTML content
    with open(os.path.join(script_dir, f"{invite_type}.html"), 'r') as file:
        html_template = file.read()

    # Replace placeholders with actual values
    html_content = html_template.format(email=recipient, company_name=company_name, secret_code=secret_code,
                                        username=username, host=BASE_HOST)

    # Email details
    from_email = "no-reply@biidin.com"  # Replace with your desired "from" email address
    if not subject:
        subject = f"You've been invited to join {company_name} Account"

    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"

    # Send the email
    response = requests.post(
        url,
        auth=("api", MAILGUN_API_KEY),
        data={"from": from_email,
              "to": [recipient],
              "subject": subject,
              "html": html_content}
    )

    return response
