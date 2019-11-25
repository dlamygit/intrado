import sys;
import codecs;
from Crypto.Cipher import DES;

key = b'\xef\x00\xff\x02\xfb\x00\xffB';

cipher = DES.new(key, DES.MODE_ECB);

file_name = sys.argv[1];

customer_name = sys.argv[2];

with open('./temp/'+customer_name+'/'+file_name+'.txt') as f:
    password = f.readline().rstrip();

trailing_characters_count = 32 - len(password);

trailing_string = '\0' * trailing_characters_count;

plaintext = ( password + trailing_string ).encode('utf-8');

msg_hex = codecs.encode(cipher.encrypt(plaintext), 'hex').decode().upper();

print(msg_hex);