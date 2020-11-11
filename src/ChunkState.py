from Compress import compress

class Output:
    def __init__(self, chaining_value, block_words, block_len, counter, flags):
        self.OUTPUT_LENGTH = 32
        self.ROOT = 8
        self.input_chaining_value = chaining_value
        self.block_words = block_words
        self.counter = counter
        self.block_length = block_len
        self.flags = flags

    def chaining_value(self):
        return compress(self.input_chaining_value, self.block_words, self.counter, self.block_length, self.flags)[:8]

    def root_output_bytes(self, output):
        output_block_counter = 0
        for out_block_ind in range(0, len(output), 2*self.OUTPUT_LENGTH):
            remaining_block_bytes = min(2*self.OUTPUT_LENGTH, len(output)- out_block_ind)
            words = compress(self.input_chaining_value, self.block_words, output_block_counter, self.block_length, self.flags | self.ROOT)

            for (word, out_word_ind) in zip(words, range(0, remaining_block_bytes, 4)):
                remaining_word_bytes = min(remaining_block_bytes - out_word_ind, 4)
                output[out_block_ind + out_word_ind : out_block_ind + out_word_ind + remaining_word_bytes] = word.to_bytes(4, byteorder="little")[:remaining_word_bytes]
            output_block_counter += 1


class ChunkState:
    def __init__(self, key, chunk_counter, flags):
        self.BLOCK_SIZE = 64
        self.CHUNK_START = 1
        self.CHUNK_END = 2
        self.PARENT = 4
        self.ROOT = 8
        self.KEYED_HASH = 16
        self.DERIVE_KEY_CONTEXT = 32
        self.DERIVE_KEY_MATERIAL = 64
        self.chaining_value = key
        self.chunk_counter = chunk_counter
        self.block = [0] * self.BLOCK_SIZE
        self.block_length = 0
        self.blocks_compressed = 0
        self.flags = flags

    def len(self):
        return self.BLOCK_SIZE * self.blocks_compressed + self.block_length

    def start_flag(self):
        if self.blocks_compressed == 0:
            return self.CHUNK_START
        else:
            return 0

    #input is a list of bytes
    def update(self, input):
        while len(input) > 0:
            if self.block_length == self.BLOCK_SIZE:
                #We need to pack the little-endian bytes into 32-bit words
                block_words = self.convert_block_to_words()
                #Get the chaining_value
                self.chaining_value = compress(self.chaining_value, block_words, self.chunk_counter, self.BLOCK_SIZE, self.flags | self.start_flag())[:8]
                self.blocks_compressed += 1
                self.block = [0] * self.BLOCK_SIZE
                self.block_length = 0

            missing_bytes = self.BLOCK_SIZE - self.block_length
            taken_bytes = min(len(input), missing_bytes)
            self.block[self.block_length:self.block_length+taken_bytes] = input[:taken_bytes]
            self.block_length += taken_bytes
            input = input[taken_bytes:]

    def convert_block_to_words(self):
        block_words = []
        for i in range(0, len(self.block), 4):
            word = int.from_bytes(self.block[i:i+4], "little")
            block_words.append(word)
        return block_words

    def output(self):
        block_words = self.convert_block_to_words()
        return Output(self.chaining_value, block_words, self.block_length, self.chunk_counter, self.flags | self.start_flag() | self.CHUNK_END)
