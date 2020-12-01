from blake3_parallel import Blake3

hasher = Blake3()

file = open("IMG.JPG", 'rb')
byte = file.read()
hasher.update(byte)

out_block = [0] * 32
byte_output = []
for b in out_block:
	byte_output.append(b.to_bytes(1, byteorder="little"))

final = hasher.finalize(byte_output)
print("HASH", final.hex())
