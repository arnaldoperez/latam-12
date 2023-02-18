# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_mail(to, template):        
    message = Mail(
        from_email=to,
        to_emails=os.environ.get('SENDGRID_API_SENDER'),
        subject=template['subject'],
        html_content=template['body'])
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(e)
        return False

def mailtemplate_password_recovery(token):
    frontend_url=os.environ.get('FRONTEND_URL')
    frontend_url=frontend_url+"/passwordtoken?token=" + token
    body='Para recuperar la contraseña haga click <a href="'+ frontend_url +'">aquí</a>'
    template={}
    template['body']=body
    template['subject']="Recuperacion de contraseña"
    return template