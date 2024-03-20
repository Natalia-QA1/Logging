import logging
import logging.handlers
import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s >> %(levelname)s >> %(message)s >> %(asctime)s >> %(filename)s >> %(process)d',
    datefmt='%Y.%m.%d %H:%M',
    filename='all_logs.log'  #all logs should be written in file
)

logging.critical('Critical error message')
logging.error('Error message')
logging.warning('Warning message')
logging.info('Info')
logging.debug('Debug message')


main_formatter = logging.Formatter(
    '%(name)s >> %(levelname)s >> %(message)s >> %(asctime)s >> %(filename)s >> %(process)d'
)

# # Define a custom formatter for logs with user information
# filter_formatter = logging.Formatter(
#     '%(asctime)-15s %(name)-5s %(levelname)-8s Run by User: %(user)-20s %(message)s'
# )

#Custom Handler: write logs about critical errors in txt file in a specific format
class LogWriter:
    def __init__(self) -> None:
        pass

    def WriteLog(self, msg: logging.LogRecord) -> None:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        username = os.getlogin()
        with open("critical_logs.txt", 'a', encoding='utf-8') as f:
            f.write('-----------------------------------------------\n')
            f.write(f'{current_date}, critical log >> Produced by: {username}\n')
            f.write(f"{msg}\n")

class WriteToFileHandler(logging.Handler):

    def __init__(self )-> None:
        self.sender = LogWriter()
        logging.Handler.__init__(self=self)

    def emit(self, record) -> None:
        self.sender.WriteLog(record)

# Custom filter:
# class UserFilter(logging.Filter):
#     def filter(self, record):
#         record.user = os.getlogin()
#         return True

root_logger = logging.getLogger()

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(main_formatter)
root_logger.addHandler(console)

writer = WriteToFileHandler()
writer.setLevel(logging.CRITICAL)
writer.setFormatter(main_formatter)
root_logger.addHandler(writer)
#writer.addFilter(UserFilter())


# # Handler to send error and critical logs to email
class TlsSMTPHandler(logging.handlers.SMTPHandler):
    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            import string  # for tls add this line
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)

            # Dynamically set the email subject based on log level
            if record.levelno == logging.CRITICAL:
                subject = 'Attention! Critical error!'
            else:
                subject = 'Errors Logs'

            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                ", ".join(self.toaddrs),
                subject,
                formatdate(),
                msg)
            if self.username:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


#Custom Filters for TlsSMTPHandler
class EmailFilter(logging.Filter):
    """
    Allows to avoid sending logs which start from 'something' for the ERROR level logs.
    CRITICAL level logs should be sent anyway.
    """

    def filter(self, record):
        return not record.msg.lower().startswith('something') if record.levelno != logging.CRITICAL else True


email_filter = EmailFilter()


gm = TlsSMTPHandler(("smtp.gmail.com", 587), 'nataliasp20n08@gmail.com', ['ananiev4nat@yandex.ru'],
                      'Logs', ('nataliasp20n08@gmail.com', 'password'))
gm.setLevel(logging.ERROR)
root_logger.addHandler(gm)
root_logger.addFilter(email_filter)
gm.addFilter(email_filter)

# TESTING
logging.error('something went wrong')  # should not be sent
logging.error('error')  # email subject should be Errors Logs
logging.critical('production is down')  # email subject should be changed >Attention! Critical error!
logging.critical('something failed')  # email subject should be changed >Attention! Critical error!/despite 'something'


#For testing
# def devision(a,b):
#     try:
#         logging.info('Division started')
#         return a / b
#         logging.info('Division successfully performed')
#     except ZeroDivisionError as e:
#         logging.critical(f'Error: {e}')
#     except TypeError as te:
#         logging.error(f'Error: {te}')
#
# print(devision(4, 0))
