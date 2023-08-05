from tidbytes import *

# mem = Mem(u8(255))
# print(mem)

print(identity_bytes_u8(u8(0xFF)))
# print(identity_bytes_u16(u16(0x01FF)))

i = identity_bytes_u16(u16(0b1011))
print(i)
print([bin(a) for a in i])


# x = 0b10000000
# print(bin(x), bin(reverse_byte(x)))
