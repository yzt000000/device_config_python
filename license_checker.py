import os
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import uuid

#key = Fernet.generate_key()
#print(f"Generated key: {key.decode()}")

class LicenseChecker:
    def __init__(self, license_file='license.key'):
        self.license_file = license_file
        self.key = b'OB7xGY9T7e377bbSG90TPPSWzeVNS3UDYdfxjz9YgL8='  # 替换为你的密钥
        self.fernet = Fernet(self.key)
    def get_mac_address(self):
        mac = uuid.getnode()
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))


    def check_license(self):
        if not os.path.exists(self.license_file):
            print("License file not found.")
            return False

        try:
            with open(self.license_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())

            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            mac_address = license_data['mac_address']
            #current_mac_address = input("Please enter the MAC address: ")
            current_mac_address = self.get_mac_address()
            if mac_address != current_mac_address:
                print(f"License is not valid for this MAC address. Expected: {mac_address}, Entered: {current_mac_address}")
                return False

            if datetime.now() > expiry_date:
                print("License has expired.")
                return False
            
            time_left = expiry_date - datetime.now()
            print(f"License is valid. {time_left} remaining.")
            return True

        except Exception as e:
            print(f"Error checking license: {e}")
            return False



