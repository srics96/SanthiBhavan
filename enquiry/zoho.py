import smtplib
from email.mime.text import MIMEText

# Define to/from
sender = 'no-reply@hotelsanthibhavan.in'
recipient = 'sricharanprograms@gmail.com'

# Create message
msg = MIMEText("Message text")
msg['Subject'] = "Sent from python"
msg['From'] = sender
msg['To'] = recipient

# Create server object with SSL option
server = smtplib.SMTP_SSL('smtp.zoho.com', 465)

# Perform operations via server
server.login('no-reply@hotelsanthibhavan.in', 'noreplysanthinoreply9')
server.sendmail(sender, [recipient], msg.as_string())
server.quit()