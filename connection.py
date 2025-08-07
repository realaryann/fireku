import ipaddress
import logging
import subprocess
import socket
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class ConnectionHandler:
    def verify_ipv4(self, FIRESTICK_IP) -> bool:
        FIRESTICK_IP=FIRESTICK_IP.strip()
        try:
            ipaddress.IPv4Address(FIRESTICK_IP)
            logger.info("IPV4 address syntax verified")
            return True
        except Exception as e:
            logger.error(f"{Exception}: IPV4 address syntax not verified")
            return False

    def roku_establish_connection(self, ROKU_IP) -> bool:
        try:
            socket.create_connection((ROKU_IP, 8060), timeout=1)
            return True
        except Exception as e:
            logger.error(e)
            return False
    
    def roku_send_keycode(self, ROKU_IP, keycode):
        url = f'http://{ROKU_IP}:8060/keypress/{keycode}'
        try:
            res = requests.post(url, timeout=2)
            if res.status_code == 200:
                logger.info("Successfully sent the keycode to Roku")
            else:
                logger.info(f'Request failed with status code {res.status_code}')

        except Exception as e:
            logger.errore(e)


    def firetv_establish_connection(self, FIRESTICK_IP) -> bool:
        res = subprocess.run(["adb", "connect", FIRESTICK_IP], capture_output=True)
        logger.error(res.stdout)
        if res.returncode != 0 or ("failed" in str(res.stdout)) or ("missing" in str(res.stdout)):
            logger.error("adb connect failed")
            return False
        return True


    def firetv_send_keycode(self, keycode):
        res = subprocess.run(["adb", "shell", "input", "keyevent", str(keycode)], capture_output=True)