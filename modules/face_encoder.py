import cv2
import numpy as np

try:
    from keras_facenet import FaceNet
except ImportError as exc:
    raise ImportError(
        "keras-facenet is required for FaceEncoder. Install it with 'pip install keras-facenet' "
        "or 'pip install -r requirements.txt'."
    ) from exc

class FaceEncoder:
    def __init__(self):
        # Charge le modèle pré-entraîné FaceNet
        self.embedder = FaceNet()

    def get_embedding(self, face_image):
        if face_image is None or face_image.size == 0:
            return None
        
        # FaceNet s'attend à une image 160x160 RGB
        face_image = cv2.resize(face_image, (160, 160))
        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # L'image doit être dans un batch (1, 160, 160, 3)
        samples = np.expand_dims(face_image, axis=0)
        
        # Générer l'embedding (vecteur mathématique)
        embeddings = self.embedder.embeddings(samples)
        return embeddings[0]  # Retourne un vecteur 1D
