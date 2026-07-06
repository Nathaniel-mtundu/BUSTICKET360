import qrcode

data = "http://192.168.0.10/tickets/verify/TKT001/"

qr = qrcode.make(data)

qr.save("test_qr.png")

print("QR code created successfully!")