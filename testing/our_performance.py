from blake3 import Blake3

BUF_SIZE = 65536*8
hasher = Blake3()
i = 0
with open('IMG.JPG', 'rb') as f:
	while True:
		data = f.read(BUF_SIZE)
		if not data:
			break
		hasher.update(data)
		i = i + 1

out_block = [0] * 32
byte_output = []
for b in out_block:
	byte_output.append(b.to_bytes(1, byteorder="little"))

final = hasher.finalize(byte_output)
print("HASH", final.hex())
