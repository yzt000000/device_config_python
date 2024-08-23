import os
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import uuid
import logging

class LicenseChecker:
    def __init__(self, license_file='license.key'):
        self.license_file = license_file
        self.key = b'OB7xGY9T7e377bbSG90TPPSWzeVNS3UDYdfxjz9YgL8='  # 替换为你的密钥
        self.fernet = Fernet(self.key)

    def get_mac_address(self):
        mac = uuid.getnode()
        return '-'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    def check_license(self):
        if not os.path.exists(self.license_file):
            logging.error("License file not found.")
            return False, "License file not found."

        try:
            with open(self.license_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())

            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            mac_address = license_data['mac_address']
            current_mac_address = self.get_mac_address()

            if mac_address != current_mac_address:
                logging.error(f"License is not valid for this MAC address. Expected: {mac_address}, Found: {current_mac_address}")
                contact_info = "Please contact support at yztfwj1@163.com."
                return False, "License is not valid for this MAC address." + contact_info

            if datetime.now() > expiry_date:
                logging.error("License has expired.")
                return False, self.get_time_remaining(expiry_date)

            time_left = expiry_date - datetime.now()
            logging.info(f"License is valid. {time_left} remaining.")
            return True, self.get_time_remaining(expiry_date)

        except Exception as e:
            logging.error(f"Error checking license: {e}")
            return False, f"Error checking license: {e}"

    def get_time_remaining(self, expiry_date=None):
        """
        返回许可证剩余的有效期时间，如果已过期，提供联系信息。
        """
        try:
            if expiry_date is None:
                with open(self.license_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                license_data = json.loads(decrypted_data.decode())
                expiry_date = datetime.fromisoformat(license_data['expiry_date'])

            current_time = datetime.now()
            if current_time > expiry_date:
                contact_info = "Please contact support at yztfwj1@163.com."
                return f"License expired on {expiry_date}. {contact_info}"

            time_left = expiry_date - current_time
            return f"License is valid. Time remaining: {time_left}."

        except Exception as e:
            logging.error(f"Error retrieving time remaining: {e}")
            return f"Error retrieving time remaining: {e}"

    def load_license(self, file_path):
        """
        加载新的License文件，验证其有效期，并将其保存到程序目录中。
        """
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())

            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            mac_address = license_data['mac_address']
            current_mac_address = self.get_mac_address()
            mac_address = license_data['mac_address']
            current_mac_address = self.get_mac_address()

            if mac_address != current_mac_address:
                logging.error(f"License is not valid for this MAC address. Expected: {mac_address}, Found: {current_mac_address}")
                contact_info = "Please contact support at yztfwj1@163.com."
                return False, "License is not valid for this MAC address." + contact_info

            if datetime.now() > expiry_date:
                logging.error("License has expired.")
                return False, self.get_time_remaining(expiry_date)

            with open(self.license_file, 'wb') as f:
                f.write(encrypted_data)
            time_left = expiry_date - datetime.now()
            logging.info(f"License is valid. {time_left} remaining.")
            return True, self.get_time_remaining(expiry_date)

        except Exception as e:
            logging.error(f"Error loading license: {e}")
            raise ValueError(f"Error loading license: {e}")