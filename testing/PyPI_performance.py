from blake3 import blake3, KEY_LEN, OUT_LEN

BUF_SIZE = 65536*8
hasher = blake3()
i = 0
with open('IMG.jpg', 'rb') as f:
	while True:
		data = f.read(BUF_SIZE)
		if not data:
			break
		hasher.update(data)
		i = i + 1

final = hasher.digest()
print("HASH", final.hex())

