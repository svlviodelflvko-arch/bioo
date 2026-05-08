import cv2

class FaceDetector:
    def __init__(self):
        # Utilisation du modèle Haar Cascade intégré à OpenCV (très léger et fiable)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_and_crop(self, frame):
        # Convertir en niveaux de gris pour la détection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Détecter les visages
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(60, 60)
        )

        if len(faces) == 0:
            return None

        # Prendre le premier visage détecté
        x, y, w, h = faces[0]

        # Ajouter une petite marge autour du visage pour l'embedding
        margin_x = int(0.1 * w)
        margin_y = int(0.1 * h)
        
        x = max(0, x - margin_x)
        y = max(0, y - margin_y)
        w = min(frame.shape[1] - x, w + 2 * margin_x)
        h = min(frame.shape[0] - y, h + 2 * margin_y)

        # Découper le visage de l'image originale (en couleur)
        cropped_face = frame[y:y+h, x:x+w]
        return cropped_face