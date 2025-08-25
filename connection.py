import ipaddress
import logging
import subprocess
import socket
import requests
import xml.etree.ElementTree as ET


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class ConnectionHandler:
    
    def __init__(self):
        self.device_ip_name = [
        ]

    def discover_roku(self):
        # "HOST: 239.255.255.250:1900" means a multicast message header. SSDP is efficient so it doesn't use 
        # broadcasting. Port 1900 is the ssdp port
        msg = '\r\n'.join([
            "M-SEARCH * HTTP/1.1",
            "HOST: 239.255.255.250:1900",
            "MAN: ssdp:discover",
            "MX: 2",
            "ST: roku:ecp",
            '',''
        ]).encode("utf-8")

        # AF_INET = ipv4
        # SOCK_DGRAM = UDP
        # IPPROTO_UDP = udp
        
        # find local IP to bind to (windows solution)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Does not send any data, just connects to a dummy address to get local IP
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(3)
        sock.bind((local_ip, 0))
        sock.sendto(msg, ("239.255.255.250", 1900))

        devices = []
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                if b'roku:ecp' in data:
                    response = data.decode("utf-8")
                    devices.append(addr[0])
        
        except socket.timeout:
            pass

        for roku_ip in devices:
            if self.roku_establish_connection(roku_ip):
                entry={"type": "roku", "name": self.get_roku_name(roku_ip), "ip": roku_ip}
                self.device_ip_name.append(entry) 
    
    def get_roku_name(self,ip):
        url = f'http://{ip}:8060/query/device-info'
        try:
            ret = requests.get(url, timeout=2)
            if ret.status_code == 200:
                root = ET.fromstring(ret.text)
                name = root.find("friendly-device-name").text
                return name
            else:
                return f"Error: {r.status_code}"
        except Exception as e:
            return f"Error: {e}"
        

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