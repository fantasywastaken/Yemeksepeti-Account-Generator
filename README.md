# 🍽️ Yemeksepeti Account Creator

<img src="https://i.imgur.com/oEeYrvA.png">

Automated account registration tool for Yemeksepeti, designed to handle email verification and form submission processes.

---

### 🚀 Features

- 📥 Automatically sends registration and verification requests
- 📧 Connects to IMAP to read confirmation emails (supports firstmail.ltd)
- 🤖 Generates random user info with Faker
- 🔒 Strong password generator
- 🗂️ Logs successfully created accounts
- 📛 PerimeterX detection handling (limited sessions per run)

---

### ⚠️ Limitations

After multiple requests, the system may trigger PerimeterX security and block further account creation.
This project is continuously improvable and ideal for developers looking to build on automation strategies.

---

### 🔧 Requirements

- Python 3.8+
- An IMAP-supported mail (like from firstmail.ltd)
- Open IMAP access on the mailbox
- accounts.txt file with emails and passwords (email:password per line)

---

### 📦 Dependencies

Install via pip:
```
pip install tls-client loguru faker
```

---

### 📁 File Structure

- ├── accounts.txt
- ├── proxy.txt (not required)

▶️ Usage
```
python main.py
```

---

### 📜 Notes

- IMAP server used: imap.firstmail.ltd
- Waits between actions to reduce detection risk
- Each run sleeps after processing to avoid request bursts

---

### 🧠 Developer Notes

- You can implement proxy support via the proxy.txt list (commented in code)
- Built with development and learning purposes in mind
- Contributions are welcome for extending CAPTCHA solving, or bypassing PerimeterX detection

---

### ⚠️ Disclaimer

This project is for educational purposes only. Use responsibly and at your own risk. The developer is not responsible for any consequences resulting from the use of this tool.
