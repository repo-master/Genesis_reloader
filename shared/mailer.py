import smtplib
import os
import io
import logging
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# from ...shared.config import config_log

COMMA_SPACE = ', '
LOG_TAIL_LINES = 1000

#https://stackoverflow.com/a/13790289/12887350
def tail(f, lines=1, _buffer=4096):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()

        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1

    return ''.join(lines_found[-lines:])

def getSyslog(lines):
    service_name = "genesis.service"
    p = subprocess.Popen(["/bin/journalctl", "-n", str(lines), "--no-pager", "-eu",  service_name], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    f = io.StringIO(output)
    f.name = "stdout.log"
    return f

def getMailConfig(level):
    lvl = logging.getLevelName(level).lower()

    #TODO: Put this into config
    #mail_recp = {'error': ["a.shaikh@phaidelta.com"], 'critical': ["a.shaikh@phaidelta.com"], 'test':["a.shaikh@phaidelta.com"],}
    mail_recp = {'error': ["narayan_band@live.com", "shalabh@phaidelta.com"], 'critical': ["narayan_band@live.com", "shalabh@phaidelta.com", "ratish@phaidelta.com"], 'Failer': ["a.shaikh@phaidelta.com"], 'INFO': ["a.shaikh@phaidelta.com"]}
    recipients = mail_recp[level] if level in mail_recp else mail_recp['error']

    return {
        "credentials": {"mail_host": "smtp.zoho.com", "port": 587, "handshake_type": "starttls", "login": "noreply@phaidelta.com", "passwd": "GKBfB9j1rkAF"},
        "recipients": recipients
    }

def createFileAttachment(f, tail_lines=None, f_name=None):
    data = tail(f, tail_lines) if tail_lines is not None else f.read()
    attachment = MIMEText(data)
    if f_name is not None:
        attachment.add_header('Content-Disposition', 'attachment', filename = f_name)
    elif hasattr(f, 'name'):
        attachment.add_header('Content-Disposition', 'attachment', filename = os.path.basename(f.name))
    return attachment

def send_mail(level, subject, body, attach_svlog=True, attach_systemdlog=False, attachments=[]):
    cfg = getMailConfig(level)
    print(f'recipients for level: {level} are : {cfg}')
    
    message = MIMEMultipart()
    files = []
    html_struct = "<html><head></head><body>%s</body></html>"
    html_bdy = ""
#    print(cfg['recipients'])
    cfg['recipients']=["a.shaikh@phaidelta.com"]
 #   print(cfg['recipients'])

    # recipients = ["a.shaikh@phaidelta.com"]
#    cfg['recipients']="a.shaikh@phaidelta.com"
    message['From'] = cfg['credentials']['login']
    message['To'] = COMMA_SPACE.join(cfg['recipients'])
    message['Subject'] = "[{}] [{}] {}".format(os.environ.get('FLASK_ENV', 'default'), logging.getLevelName(level), subject)
    
    #User-defined body
    html_bdy += "<div>%s</div>" % body
    
    if attach_svlog:
        with open(config_log['log_path'], 'r') as f:
            files.append(createFileAttachment(f, LOG_TAIL_LINES))
    
    if attach_systemdlog:
        with getSyslog(LOG_TAIL_LINES) as f:
            files.append(createFileAttachment(f))
    
    for attachment_file in attachments:
        if isinstance(attachment_file, str):
            f_obj = open(attachment_file, 'r')
        else:
            f_obj = attachment_file
        
        with f_obj:
            files.append(createFileAttachment(f_obj))
    
    #Put some good grammar in there
    num_files = len(files)
    if num_files > 0: html_bdy += "<br/><span style=\"font-weight: bold; color: red;\">Please check the attached log file%s containing last 1000 lines of output.</span>" % "s" if num_files > 1 else ""
    
    #Disclaimer
    html_bdy += "<br/><p style=\"font-weight: bold; color: green;\">This is an auto-generated email. Please do not reply to it.</p>"
    
    #Generate the mail body, attach any files needed
    message.attach(MIMEText(html_struct % html_bdy, 'html'))
    for f in files:
        message.attach(f)
    
    smtpObj = smtplib.SMTP(cfg['credentials']['mail_host'], cfg['credentials']['port'])
    if cfg['credentials']['handshake_type'] == 'starttls':
        smtpObj.starttls()
    
    #Log in to mail server
    smtpObj.login(cfg['credentials']['login'], cfg['credentials']['passwd'])
    
    #Send the mail to the recipients
    smtpObj.sendmail(cfg['credentials']['login'], cfg['recipients'], message.as_string())
    
    #Cleanup
    smtpObj.close()



def test(level, subject,body,attach_systemdlog=False):
    print("Level : ",level)
    print("Subject : ",subject)
    print("Body: ",body)
    print("Att sys log : ", attach_systemdlog)