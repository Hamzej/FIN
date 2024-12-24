import os
import shutil
from flask import Flask, request, render_template
from PIL import Image
from huffman import compress_image  # Importer uniquement la fonction de compression Huffman
from dct_compression import compress_image_dct  # Assurez-vous que cette fonction existe dans 'dct_compression.py'

app = Flask(__name__)

# Créez un dossier pour stocker les fichiers téléchargés
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Créez un dossier pour les images compressées
if not os.path.exists('static/compressed_images'):
    os.makedirs('static/compressed_images')

# Fonction pour déplacer les fichiers compressés vers le dossier static
def move_to_static(compressed_file):
    static_folder = 'static/compressed_images/'
    compressed_file_name = os.path.basename(compressed_file)
    destination = os.path.join(static_folder, compressed_file_name)

    # Gérer les conflits de noms de fichiers
    if os.path.exists(destination):
        base_name, ext = os.path.splitext(compressed_file_name)
        counter = 1
        while os.path.exists(destination):
            # Ajouter un suffixe au nom du fichier
            compressed_file_name = f"{base_name}_{counter}{ext}"
            destination = os.path.join(static_folder, compressed_file_name)
            counter += 1

    shutil.copy(compressed_file, destination)
    return destination

# Fonction pour déplacer l'image originale vers le dossier static
def move_original_to_static(file_path, file_name):
    static_folder = 'static/'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)
    destination = os.path.join(static_folder, file_name)
    shutil.copy(file_path, destination)
    return destination

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    compression_type = request.form.get('compression_type')  # Récupérer le type de compression choisi

    if file:
        # Enregistrez le fichier téléchargé dans le dossier 'uploads'
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Déplacer l'image originale dans le dossier static pour qu'elle soit accessible
        original_image_url = move_original_to_static(file_path, file.filename)

        # Récupérer les informations de l'image originale
        img = Image.open(file_path)
        original_size = os.path.getsize(file_path) / 1024  # Taille en Ko
        original_width, original_height = img.size

        if compression_type == 'huffman':
            # Appliquer la compression Huffman
            compressed_file = compress_image(file_path)
        elif compression_type == 'dct':
            # Appliquer la compression DCT
            compressed_file = compress_image_dct(file_path)
        else:
            return "Type de compression non supporté", 400

        # Déplacer l'image compressée dans 'static/compressed_images'
        compressed_file = move_to_static(compressed_file)

        # Obtenez la taille du fichier compressé
        compressed_size = os.path.getsize(compressed_file) / 1024  # Taille compressée en Ko

        # Récupérer les dimensions de l'image compressée
        compressed_img = Image.open(compressed_file)
        compressed_width, compressed_height = compressed_img.size

        # Calculer le ratio de compression (original_size / compressed_size)
        compression_ratio = original_size / compressed_size

        # Passer les chemins relatifs vers les fichiers dans 'static' et le ratio de compression
        compressed_image_url = '/static/compressed_images/' + os.path.basename(compressed_file)

        return render_template('index.html', 
                               original_image_url=original_image_url,
                               compressed_image_url=compressed_image_url,
                               original_size=round(original_size, 2),
                               original_width=original_width,
                               original_height=original_height,
                               compressed_size=round(compressed_size, 2),
                               compressed_width=compressed_width,
                               compressed_height=compressed_height,
                               compression_ratio=round(compression_ratio * 100, 2),  # Afficher le ratio en pourcentage
                               compression_type=compression_type)

if __name__ == '__main__':
    app.run(debug=True)
