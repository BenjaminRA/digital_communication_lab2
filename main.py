import os
import time
import random
import string
import matplotlib.pyplot as plt
import numpy as np
from lzw3 import compressor as lzw3Compressor
from lzw3 import decompressor as lzw3Decompressor
from huffman import HuffmanCoding
from rle import RLE
from lz78 import lz78_compress
from ppm import ppm_compression, ppm_decompression

def sum_values(store, sample_values):
	if len(store) is 0:
			store = sample_values
	else:
		for i in range(len(store)):
			store[i] += sample_values[i]
	return store

def save_bar_graph(ratio, timing, title, path, show = False):
	compression_methods = [1, 2, 3, 4, 5]
	tick_label = ['Huffman', 'RLE', 'LZW', 'LZ78', 'PPM']

	plt.figure(figsize=[20, 8])
	plt.suptitle(title)
	plt.subplot(1, 2 ,1)
	plt.bar(compression_methods, ratio, tick_label = tick_label, width=0.8)
	plt.xlabel('Compression Algorithm') 
	plt.ylabel('Compression ratio (%) \n Lower is better')
	plt.title("Compression ratio")

	plt.subplot(1, 2 ,2)
	plt.bar(compression_methods, timing, tick_label = tick_label, width=0.8)
	plt.xlabel('Compression Algorithm') 
	plt.ylabel('Time (ms) \n Lower is better')
	plt.title("Time complexity") 
	
	if show:
		plt.show()

	plt.savefig(path, format="svg")

def random_pattern_test(path):
	with open(path + f"/data.txt", 'a') as records:
		records.write("\n------------------------------------------------------------------------\nRandom Pattern Testing\n")

	path = path + "/random_pattern"
	if not os.path.exists(path):
		os.mkdir(path)

	avg_ratio = []
	avg_timing = []

	for test_number in range(30):
		text = ""
		pattern = ""
		for i in range(20):
			pattern += random.choice(string.ascii_letters)

		for i in range(random.randint(10000, 300000)):
			text += pattern

		sample_ratio, sample_timing = testing(text, test_number + 1, path, "Random Pattern Testing")

		avg_ratio = sum_values(avg_ratio, sample_ratio)
		avg_timing = sum_values(avg_timing, sample_timing)

	for i in range(len(avg_ratio)):
		avg_ratio[i] = avg_ratio[i]/30
		avg_timing[i] = avg_timing[i]/30
	save_bar_graph(avg_ratio, avg_timing, "Random Pattern Testing Average", "graphs/Random Pattern Testing Average.svg")
	
	with open(os.getcwd() + f"/data.txt", 'a') as records:
		records.write(f"\nOriginal Size: {original_size} bytes\n")
		records.write(f"\t\t\tSize\t\tCompression Ratio\t\t\tTime\n")
		for i in range(5):
			spacing = ["\t" if i is not 0 else "", "\t" if int(ratio[i]) < 100 else "", "\t" if int(ratio[i]/100*original_size) < 100000 else ""]
			records.write(f"{tick_label[i]}:\t{spacing[0]}{int(ratio[i]/100*original_size)} bytes{spacing[2]}\t{ratio[i]}%\t\t{timing[i]} ms\n")




def random_test(path):
	with open(path + f"/data.txt", 'a') as records:
		records.write("\n------------------------------------------------------------------------\nRandom Testing\n")

	path = path + "/random"
	if not os.path.exists(path):
		os.mkdir(path)

	avg_ratio = []
	avg_timing = []

	for test_number in range(30):
		text = ""

		for i in range(random.randint(1000000, 5000000)):
			text += random.choice(string.ascii_letters)

		sample_ratio, sample_timing = testing(text, test_number + 1, path, "Random Testing")

		avg_ratio = sum_values(avg_ratio, sample_ratio)
		avg_timing = sum_values(avg_timing, sample_timing)
		
	for i in range(len(avg_ratio)):
		avg_ratio[i] = avg_ratio[i]/30
		avg_timing[i] = avg_timing[i]/30
	save_bar_graph(avg_ratio, avg_timing, "Random Testing Average", "graphs/Random Testing Average.svg")

def testing(text, test_number, path, test_name):

	ratio = []
	timing = []

	print(f"test number: {test_number}")
	output = open(path + f"/test_{test_number}.txt", 'w')
	output.write(text)
	original_size = os.path.getsize(path + f"/test_{test_number}.txt")

	# Huffman
	print("Compressing with Huffman...")
	h = HuffmanCoding(output.name)

	start = time.time()
	compressed = h.compress()
	timing.append((time.time() - start) * 1000)
	
	h.decompress(compressed)
	ratio.append(os.path.getsize(compressed) / original_size * 100)
	print("Compressing with Huffman finished")

	# RLE
	print("Compressing with RLE...")
	rle = RLE()
	output = open(path + f"/test_{test_number}_rle.rle", 'w')
	
	start = time.time()
	output.write(rle.encode(text))
	timing.append((time.time() - start) * 1000)

	ratio.append(os.path.getsize(path + f"/test_{test_number}_rle.rle") / original_size * 100)
	print("Compressing with RLE finished")

	# LZW
	print("Compressing with LZW...")

	start = time.time()
	lzw3Compressor.LZWCompressor().compress(path + f"/test_{test_number}.txt", path + f"/test_{test_number}_lzw.lzw")
	timing.append((time.time() - start) * 1000)
	
	# lzw3Decompressor.LZWDecompressor().decompress(path + f"/test_{test_number}_lzw.lzw", path + f"/test_{test_number}_lzw_decompressed.txt")
	ratio.append(os.path.getsize(path + f"/test_{test_number}_lzw.lzw") / original_size * 100)
	print("Compressing with LZW finished")

	# LZ78
	print("Compressing with LZ78...")
	output = open(path + f"/test_{test_number}_lz78.lz78", 'w')

	start = time.time()
	output.write(lz78_compress(text))
	timing.append((time.time() - start) * 1000)

	ratio.append(os.path.getsize(path + f"/test_{test_number}_lz78.lz78") / original_size * 100)
	print("Compressing with LZ78 finished")

    # PPM
	print("compression with PPM...")

	start = time.time()
	ppm_compression(path + f"/test_{test_number}.txt", path + f"/test_{test_number}_ppm.ppm")
	timing.append((time.time() - start) * 1000)
	
	# ppm_decompression(path + f"/test_{test_number}_ppm.ppm", path + f"/test_{test_number}_ppm_decompresed.txt")
	ratio.append(os.path.getsize(path + f"/test_{test_number}_ppm.ppm") / original_size * 100)
	print("compressing with PPM finished")

	save_bar_graph(ratio, timing, f"{test_name} N°{test_number}\nOriginal Size: {original_size} bytes", f"graphs/{test_name} {test_number}.svg")

	tick_label = ['Huffman', 'RLE', 'LZW', 'LZ78', 'PPM']

	with open(os.getcwd() + f"/data.txt", 'a') as records:
		records.write(f"\nOriginal Size: {original_size} bytes\n")
		records.write(f"\t\t\tSize\t\tCompression Ratio\t\t\tTime\n")
		for i in range(5):
			spacing = ["\t" if i is not 0 else "", "\t" if int(ratio[i]) < 100 else "", "\t" if int(ratio[i]/100*original_size) < 100000 else ""]
			records.write(f"{tick_label[i]}:\t{spacing[0]}{int(ratio[i]/100*original_size)} bytes{spacing[2]}\t{ratio[i]}%\t\t{timing[i]} ms\n")
	
	return ratio, timing

if __name__ == "__main__":
	path = os.getcwd()
	# h = HuffmanCoding(path)
	if os.path.exists(path + "/data.txt"):
		os.remove(path + "/data.txt")

	if not os.path.exists(path + "/graphs"):
		os.mkdir(path + "/graphs")

	# 30 archivos del mismo tamano de entrada tipo texto repetitivo a partir de un patron generado al azar de caracteres de largo 20
	random_pattern_test(path)
		
	# 30 archivos cuyo contenido sean caracteres al azar
	random_test(path)