# Transfer output file to SBS
# Screw you, WinSCP!

from ftplib import FTP_TLS
import ssl
import os

# Set TLS version
# I don't know if this actually does anything, but it doesn't break anything...test later
ctx = ssl._create_stdlib_context(ssl.PROTOCOL_TLSv1_2)

# Open spectrum file reader
spectrum_filename = [file for file in os.listdir() if file.startswith("sainsburys.survey")][0]
spectrum = open(spectrum_filename, "rb")

# Open connection
ftp = FTP_TLS(host="ftp.autographsurvey.co.uk", context=ctx)
ftp.login(user="autograph", passwd="Mastek2017$")
ftp.prot_p()

print("Connection open, storing file")

try:
    ftp.storbinary("STOR " + "test_file.csv", spectrum)
    print("Successfully transferred file")
    ftp.quit()
except:
    print("Transfer failed")
    ftp.quit()
