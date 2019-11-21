import heapq
import os
from functools import total_ordering

"""
Code for Huffman Coding, compression and decompression. 
"""

@total_ordering
class HeapNode:

	"""
	Si no tiene char asociado, significa que no es una hoja del arbol y que se debe seguir bajando para llegar a un caracter
	"""
	def __init__(self, char, freq):
		self.char = char
		self.freq = freq
		self.left = None
		self.right = None

	"""
	Funciones utilizada por la clase heapq para crear el Heap y ordenarlo correctamente
	"""
	def __lt__(self, other):
		return self.freq < other.freq
	def __eq__(self, other):
		if(other == None):
			return False
		if(not isinstance(other, HeapNode)):
			return False
		return self.freq == other.freq


class HuffmanCoding:
	def __init__(self, path):
		self.path = path
		self.heap = []
		self.codes = {}
		self.reverse_mapping = {}

	""" Funciones para la compresión: """

	"""
	Crea el diccionario de frecuencias asociadas a cada caracter
	"""
	def make_frequency_dict(self, text):
		frequency = {}
		for character in text:
			if not character in frequency:
				frequency[character] = 0
			frequency[character] += 1
		return frequency

	"""
	Crea el Heap utilizando la clase HeapNode en cada entrada
	Cada HeapNode es creado utilizando el diccionario
	donde se crea con el caracter y su respectiva frecuencia
	"""
	def make_heap(self, frequency):
		for key in frequency:
			node = HeapNode(key, frequency[key])
			heapq.heappush(self.heap, node)

	"""
	Crea el Árbol a partir del Heap
	Donde se usan los 2 nodos con menor frecuencia (los dos primeros) y se juntan en un mini arbol.
	Este proceso continua hasta que solo quede 1 nodo en el Heap. Lo que quiere decir que el árbol está completo
	y que el nodo que quedo es la raiz del árbol
	"""
	def merge_nodes(self):
		while(len(self.heap)>1):
			node1 = heapq.heappop(self.heap)
			node2 = heapq.heappop(self.heap)

            # Se crea un nodo con char = None para reconocer que no es una hoja y que se debe seguir avanzando para encontrar un caracter
			merged = HeapNode(None, node1.freq + node2.freq)
			merged.left = node1
			merged.right = node2

            # Se agrega el nuevo Nodo al Heap
			heapq.heappush(self.heap, merged)

	"""
	Crea un diccionario que corresponde al código binario asociado a cada caracter
	Y un diccionario que corresponde al caracter asociado a cada código binario.
	Esto lo hace recursivamente a travez del árbol hasta que el atributor char del Nodo sea distinto de None
	lo que quiere decir que llegamos a una hora, osea un caracter
	Un salto a la izquierda corresponde a un 0
	Un salto a la derecha corresponde a un 1
	"""
	def make_codes_helper(self, root, current_code):
		if(root == None):
			return

		if(root.char != None):
			self.codes[root.char] = current_code
			self.reverse_mapping[current_code] = root.char
			return

		self.make_codes_helper(root.left, current_code + "0")
		self.make_codes_helper(root.right, current_code + "1")


	"""
	Punto inicial de la creación de los diccionarios en el método make_codes_helper
	Se separa de esta función para poder usar la recursividad
	"""
	def make_codes(self):
		root = heapq.heappop(self.heap)
		current_code = ""
		self.make_codes_helper(root, current_code)

	"""
	Se codifica el texto utilizando los diccionarios
	"""
	def get_encoded_text(self, text):
		encoded_text = ""
		for character in text:
			encoded_text += self.codes[character]
		return encoded_text

	"""
	Para dejar el texto en trozos de exactamente 1 byte (8 bits)
	"""
	def pad_encoded_text(self, encoded_text):
		extra_padding = 8 - len(encoded_text) % 8
		for i in range(extra_padding):
			encoded_text += "0"
		
		# Se guarda en bits cuanto padding se dejo al final del archivo para dejarlo en 8 bits por trozo
		padded_info = "{0:08b}".format(extra_padding)
		encoded_text = padded_info + encoded_text
		return encoded_text

	"""
	Convierte el string en bytes
	"""
	def get_byte_array(self, padded_encoded_text):
		if(len(padded_encoded_text) % 8 != 0):
			print("Encoded text not padded properly")
			exit(0)

		b = bytearray()
		for i in range(0, len(padded_encoded_text), 8):
			byte = padded_encoded_text[i:i+8]
			b.append(int(byte, 2))
		return b


	"""
	Realiza la compresión utilizando los métodos anteriores
	"""
	def compress(self):
		filename, file_extension = os.path.splitext(self.path)
		output_path = filename + "_huffman.huffman"

		with open(self.path, 'r+') as file, open(output_path, 'wb') as output:
			text = file.read()
			text = text.rstrip()

			frequency = self.make_frequency_dict(text)
			self.make_heap(frequency)
			self.merge_nodes()
			self.make_codes()

			encoded_text = self.get_encoded_text(text)
			padded_encoded_text = self.pad_encoded_text(encoded_text)

			b = self.get_byte_array(padded_encoded_text)
			output.write(bytes(b))

		return output_path


	""" Funciones para Descompresión: """

	"""
	Remueve el padding utilizando la información de los primero 8 bits que indican cuanto padding hay en el trozo final de 8 bits
	"""
	def remove_padding(self, padded_encoded_text):
		padded_info = padded_encoded_text[:8]
		extra_padding = int(padded_info, 2)

		padded_encoded_text = padded_encoded_text[8:] 
		encoded_text = padded_encoded_text[:-1*extra_padding]

		return encoded_text

	"""
	Decodifica el texto viendo bit por bit si esa cadena se encuentra en el diccionario
	"""
	def decode_text(self, encoded_text):
		current_code = ""
		decoded_text = ""

		for bit in encoded_text:
			current_code += bit
			if(current_code in self.reverse_mapping):
				character = self.reverse_mapping[current_code]
				decoded_text += character
				current_code = ""

		return decoded_text


	def decompress(self, input_path):
		filename, file_extension = os.path.splitext(self.path)
		output_path = filename + "_decompressed" + ".txt"

		with open(input_path, 'rb') as file, open(output_path, 'w') as output:
			bit_string = ""

			# Convierte los bytes en strings
			byte = file.read(1)
			while(len(byte) > 0):
				byte = ord(byte)
				bits = bin(byte)[2:].rjust(8, '0')
				bit_string += bits
				byte = file.read(1)

			encoded_text = self.remove_padding(bit_string)

			decompressed_text = self.decode_text(encoded_text)
			
			output.write(decompressed_text)

		return output_path