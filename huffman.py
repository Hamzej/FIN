import os
import heapq
from collections import defaultdict
from PIL import Image
import numpy as np

# Étape 1: Extraction des pixels de l'image (inclut toutes les couleurs)
def extract_pixels(image):
    pixels = np.array(image)
    return pixels

# Étape 2: Calcul des fréquences des pixels par canal
def calculate_frequencies(pixels):
    frequencies = []
    for channel in range(pixels.shape[-1]):  # Traiter chaque canal (R, G, B)
        freq = defaultdict(int)
        for pixel in pixels[:, :, channel].flatten():
            freq[pixel] += 1
        frequencies.append(freq)
    return frequencies

# Étape 3: Construction de l'arbre de Huffman pour un canal
def build_huffman_tree(frequencies):
    heap = [[weight, [pixel, ""]] for pixel, weight in frequencies.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return sorted(heap[0][1:], key=lambda p: (len(p[-1]), p))

# Étape 4: Génération des codes de Huffman pour un canal
def generate_huffman_codes(huffman_tree):
    huff_codes = {}
    for pixel, code in huffman_tree:
        huff_codes[pixel] = code
    return huff_codes

# Étape 5: Encodage de l'image par canal
def encode_channel(channel, huffman_codes):
    return ''.join([huffman_codes[pixel] for pixel in channel.flatten()])

# Étape 6: Compression d'une image couleur
def compress_image(image_path, output_dir='static/compressed_images'):
    img = Image.open(image_path)
    pixels = extract_pixels(img)  # Garde les couleurs intactes
    frequencies = calculate_frequencies(pixels)

    # Traiter chaque canal indépendamment
    huffman_trees = [build_huffman_tree(freq) for freq in frequencies]
    huffman_codes = [generate_huffman_codes(tree) for tree in huffman_trees]

    # Encoder chaque canal
    encoded_channels = [encode_channel(pixels[:, :, i], huffman_codes[i]) for i in range(len(huffman_codes))]

    # Recréer l'image compressée (ici, on ne change pas réellement les pixels pour visualisation)
    compressed_image = Image.fromarray(pixels)  # Garde l'image originale

    # Sauvegarder l'image compressée
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    compressed_file_name = os.path.basename(image_path).split('.')[0] + '_compressed.jpg'
    compressed_file_path = os.path.join(output_dir, compressed_file_name)
    compressed_image.save(compressed_file_path, format='JPEG')

    return compressed_file_path
