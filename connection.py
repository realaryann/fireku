import ipaddress
import logging
import re
import subprocess
import socket
import requests
import xml.etree.ElementTree as ET


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class ConnectionHandler:
    
    def __init__(self):
        self.devices = set()
        self.remember_device = set()
        self.firetv_map = {}
        self.device_ip_name = [
        ]

    def discover_firetv(self, text):
        # Collect LOCATION header data
        match = re.search(r'LOCATION:\s*(.+)', text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Browse the upnp schema to get firetv info
            try:
                r = requests.get(location, timeout=2)
                xml = ET.fromstring(r.content)
                name = xml.find('.//{urn:schemas-upnp-org:device-1-0}friendlyName')
                if name is not None:
                    return name.text
                else:
                    return None
            except Exception as e:
                logger.error(f"Failed to query {location}: {e}")

    def discover_roku(self):
        # "HOST: 239.255.255.250:1900" means a multicast message header. SSDP is efficient so it doesn't use 
        # broadcasting. Port 1900 is the ssdp port
        msg = '\r\n'.join([
            "M-SEARCH * HTTP/1.1",
            "HOST: 239.255.255.250:1900",
            "MAN: ssdp:discover",
            "MX: 2",
            "ST: urn:dial-multiscreen-org:service:dial:1",
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

        try:
            while True:
                data, addr = sock.recvfrom(1024)
                data = data.decode("utf-8")
                if 'Roku' in data:
                    self.devices.add(addr[0])
                else:
                    # Try to get a Fire TV's friendly name by using UPnP friendly device
                    name = self.discover_firetv(data) 
                    if name:
                        self.firetv_map[addr[0]] = name
                        self.devices.add(addr[0])
        
        except socket.timeout:
            pass

        for ip in self.devices:
            # Try for Roku
            if self.roku_establish_connection(ip) and (ip not in self.remember_device):
                entry={"type": "roku", "name": self.get_roku_name(ip), "ip": ip}
                self.device_ip_name.append(entry) 
                self.remember_device.add(ip)
            # Try for FireTV
            elif ip not in self.remember_device:
                name = self.firetv_map[ip]
                entry={"type": "firetv", "name": name, "ip": ip}
                self.device_ip_name.append(entry) 
                self.remember_device.add(ip)


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