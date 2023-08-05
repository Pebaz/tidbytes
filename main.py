from tidbytes import *

# mem = Mem(u8(255))
# print(mem)

# print(identity_bytes_u8(u8(0xFF)))
# # print(identity_bytes_u16(u16(0x01FF)))

i = identity_bytes_u16(u16(0b00000000_11000001))
print(*identity_bits_from_numeric_byte(0b00000011))
print('!', i)


# x = 0b10000000
# print(bin(x), bin(reverse_byte(x)))

# x = 0b1
# print(bin(x), bin(reverse_byte(x)))

# print(Mem(u16(1)))

print(*identity_bits_from_numeric_byte(0b00000011))
