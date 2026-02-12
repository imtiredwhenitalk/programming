from wifi_qrcode_generator.generator import wifi_qrcode
from PIL import Image

ssid = "wifi name"
password = "password"
security = "WPA"  

qr = wifi_qrcode(ssid, False, security, password)
qr.make_image().save("wifi_qr.png")
Image.open("wifi_qr.png")