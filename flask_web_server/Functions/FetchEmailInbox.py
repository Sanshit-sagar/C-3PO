import datetime
import email
import imaplib
import mailbox
from inspect import getsourcefile
import os.path
import sys

from NLPHelpers import text_analysis

def FetchEmailInbox(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    
    EMAIL_ACCOUNT = "s@gmail.com"#"thirdnorthdelivery@gmail.com"
    PASSWORD = "asf"#"SSALAKKB509E"

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.list()
    mail.select('inbox')
    result, data = mail.uid('search', None, "UNSEEN") # (ALL/UNSEEN)
    i = len(data[0].split())
    new_emails = []

    for x in range(i):
        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        # result, email_data = conn.store(num,'-FLAGS','\\Seen')
        # this might work to set flag to seen, if it doesn't already
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # Header Details
        date_tuple = email.utils.parsedate_tz(email_message['Date'])

        if date_tuple:

            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))

        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        # Body details

        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                new_emails.append({"from": email_from, "subject": subject, "body": body.decode('utf-8').replace("\r\n", ""), "date": local_message_date})
                # file_name = "email_" + str(x) + ".txt"
                # output_file = open(file_name, 'w')
                # output_file.write("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" %(email_from, email_to,local_message_date, subject, body.decode('utf-8')))
                # output_file.close()
            else:
                continue

    follow_up = False
    if len(new_emails) > 0:
        if len(new_emails) == 1:
            resp = "You have one new email from " + new_emails[0]["from"] + " saying: " + new_emails[0]["body"]
            follow_up = False
        else:
            resp = "You have " + str(len(new_emails)) + " new emails. Would you like me to read you them?"
            follow_up = True
    else:
        resp = "You have no new emails."
        follow_up = False

    return {"follow_up":follow_up, "response": resp, "data": new_emails, "store": False}
