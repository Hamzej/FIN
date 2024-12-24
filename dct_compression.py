import os
import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct

# Étape 1 : Transformation en DCT
def apply_dct(block):
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

# Étape 2 : Transformation inverse en DCT
def apply_idct(block):
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

# Compression de l'image avec DCT
def compress_image_dct(image_path, quality=50, output_dir='static/compressed_images'):
    img = Image.open(image_path)
    img = img.convert('L')  # Convertir en niveaux de gris (DCT simple pour la démonstration)
    pixels = np.array(img)

    # Appliquer DCT par blocs de 8x8
    height, width = pixels.shape
    compressed_pixels = np.zeros_like(pixels, dtype=float)

    for i in range(0, height, 8):
        for j in range(0, width, 8):
            block = pixels[i:i+8, j:j+8]
            dct_block = apply_dct(block)
            
            # Garder un pourcentage des coefficients (basé sur la qualité)
            threshold = np.percentile(abs(dct_block), quality)
            dct_block[abs(dct_block) < threshold] = 0
            
            compressed_pixels[i:i+8, j:j+8] = dct_block

    # Reconstruction de l'image via DCT inverse
    reconstructed_pixels = np.zeros_like(pixels, dtype=float)
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            block = compressed_pixels[i:i+8, j:j+8]
            idct_block = apply_idct(block)
            reconstructed_pixels[i:i+8, j:j+8] = idct_block

    reconstructed_pixels = np.clip(reconstructed_pixels, 0, 255).astype(np.uint8)
    compressed_image = Image.fromarray(reconstructed_pixels)

    # Sauvegarder l'image compressée
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    compressed_file_name = os.path.basename(image_path).split('.')[0] + '_dct_compressed.jpg'
    compressed_file_path = os.path.join(output_dir, compressed_file_name)
    compressed_image.save(compressed_file_path, format='JPEG')

    return compressed_file_path
