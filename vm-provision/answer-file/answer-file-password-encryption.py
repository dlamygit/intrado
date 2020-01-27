import sys;
import codecs;
from Crypto.Cipher import DES;

key = b'\xef\x00\xff\x02\xfb\x00\xffB';

cipher = DES.new(key, DES.MODE_ECB);

password = sys.argv[1];

trailing_characters_count = 32 - len(password);

trailing_string = '\0' * trailing_characters_count;

plaintext = ( password + trailing_string ).encode('utf-8');

msg_hex = codecs.encode(cipher.encrypt(plaintext), 'hex').decode().upper();

print(msg_hex);