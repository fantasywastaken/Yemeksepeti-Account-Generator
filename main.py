import tls_client
import imaplib
import email
import time
import random
import string
from datetime import datetime, timedelta
from loguru import logger
from faker import Faker
import sys

fake = Faker('tr')

class YemeksepetiRegistration:
    def __init__(self, email, email_password):
        self.email = email
        self.email_password = email_password
        self.session = tls_client.Session(
            client_identifier="chrome_103",
            random_tls_extension_order=True
        )
        #self.proxy = random.choice(open("proxy.txt", "r").readlines()).strip()
        #self.session.proxies = {'http': 'http://' + self.proxy.strip(), 'https': 'http://' + self.proxy.strip()}
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://www.yemeksepeti.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.yemeksepeti.com/',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }

    def send_registration_email(self):
        json_data = {'email': self.email}
        attempts = 0
        while attempts < 3:
            try:
                response = self.session.post('https://www.yemeksepeti.com/login/new/api/email-check', headers=self.headers, json=json_data, allow_redirects=True)
                if not response.json().get('jsClientSrc'):
                    logger.debug(f"{self.email} adresine kayıt maili gönderildi.")
                    break
                else:
                    attempts += 1
                    logger.error(f"Hesap açarken problem oluştu, {attempts}. deneme.")
                    time.sleep(30)
            except Exception as e:
                logger.error(f"İstek sırasında bir hata oluştu: {str(e)}")
                attempts += 1
                time.sleep(30)
        if attempts == 3:
            logger.error("3 deneme sonunda kayıt işlemi başarısız oldu.")
            pass

    def request_email_verification(self):
        json_data = {
            'email': self.email,
            'customerType': 'email',
            'targetPath': 'https://www.yemeksepeti.com/',
            'languageId': 2,
        }
        self.session.post('https://www.yemeksepeti.com/login/new/api/email-verification', headers=self.headers, json=json_data, allow_redirects=True)

    def check_email_for_verification_token(self, imap_server, timeout=300):
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(self.email, self.email_password)
            mail.select("inbox")
            logger.success(f"{self.email} adresine başarıyla giriş yapıldı.")
        except Exception as e:
            logger.error(f"{self.email} adresine giriş yapılamadı: {str(e)}")
            return None
        start_time = time.time()
        while True:
            status, messages = mail.search(None, 'UNSEEN')
            if status == "OK":
                for num in messages[0].split():
                    status, msg_data = mail.fetch(num, '(RFC822)')
                    if status == "OK":
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                subject = msg["subject"]
                                if 'Ready to access your Yemeksepeti account?' in subject:
                                    body = self.get_email_body(msg)
                                    verification_code = body.split('verification-code%3D')[1].split('%26')[0]
                                    logger.debug(f"Kayıt maili okunarak onay kodu tespit edildi: {verification_code}")
                                    mail.logout()
                                    return verification_code
            if time.time() - start_time > timeout:
                mail.logout()
                return None
            time.sleep(5)

    def get_email_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
        else:
            return msg.get_payload(decode=True).decode()

    def register_user(self, first_name, last_name, password, birthdate, verification_code):
        json_data = {
            'email': self.email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'passwordless': '',
            'birthdate': birthdate,
            'terms_and_conditions_consent': 'agreed',
            'marketing_consent': 'opt-in',
            'marketing_sms_consent': 'opt-in',
            'email_verification_token': verification_code,
        }
        response = self.session.post(
            'https://www.yemeksepeti.com/login/new/api/registration',
            headers=self.headers,
            json=json_data,
            allow_redirects=True
        )
        if response.json().get('user_id'):
            return response.json()['user_id']
        else:
            logger.error("Kayıt işlemi başarısız oldu.")
            return None

def generate_random_birthdate():
    start_date = datetime(1980, 1, 1)
    end_date = datetime.now() - timedelta(days=365 * 18)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date.strftime("%Y-%m-%d")

def generate_strong_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
    return ''.join(random.choice(chars) for _ in range(length))

def handle_account(email, email_password):
    try:
        registration = YemeksepetiRegistration(email, email_password)
        registration.send_registration_email()
        registration.request_email_verification()
        verification_code = registration.check_email_for_verification_token("imap.firstmail.ltd")
        if verification_code:
            password = generate_strong_password()
            birthdate = generate_random_birthdate()
            name = fake.first_name()
            surname = fake.last_name()
            user_id = registration.register_user(
                first_name=name,
                last_name=surname,
                password=password,
                birthdate=birthdate,
                verification_code=verification_code
            )
            if user_id:
                logger.success(f"Hesap başarıyla oluşturuldu. Kullanıcı IDsi: {user_id} | Email: {email}")
                try:
                    with open("created_users.txt", "a") as f:
                        f.write(f"{email}:{password}\n")
                        f.flush()
                    logger.debug(f"Kullanıcı başarıyla kaydedildi: {email}")
                except Exception as e:
                    logger.error(f"Kullanıcı kaydedilirken hata oluştu: {email}. Hata: {str(e)}")
            else:
                logger.error(f"{email} için kayıt işlemi başarısız.")
        else:
            logger.error(f"{email} için kayıt kodu alınırken hata oluştu.")
    except Exception as e:
        logger.error(f"Hesap işlemi sırasında hata oluştu: {email}. Hata: {str(e)}")
    finally:
        time.sleep(60)

def main():
    with open('accounts.txt', 'r') as file:
        accounts = file.readlines()
    for account in accounts:
        email, password = account.strip().split(':')
        handle_account(email, password)

if __name__ == "__main__":
    main()
