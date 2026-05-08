import time
import cv2
from modules.camera_handler import CameraHandler
from modules.face_detector import FaceDetector
from modules.face_encoder import FaceEncoder
from modules.database import DatabaseManager
from modules.face_authenticator import FaceAuthenticator
from modules.system_controller import SystemController

# Configurations
ABSENCE_TIMEOUT = 10  # Secondes sans visage avant verrouillage
AUTH_INTERVAL = 2     # Vérifier l'identité toutes les X secondes

def main():
    cam = CameraHandler()
    detector = FaceDetector()
    encoder = FaceEncoder()
    db = DatabaseManager()
    auth = FaceAuthenticator(db, threshold=0.45) # Ajustez le threshold si besoin

    last_seen_time = time.time()
    last_auth_time = 0

    print("FaceLock tourne en arrière-plan...")

    while True:
        frame = cam.get_frame()
        if frame is None:
            continue

        face = detector.detect_and_crop(frame)
        current_time = time.time()

        if face is not None:
            last_seen_time = current_time
            
            # Ne pas calculer l'embedding à chaque frame (trop gourmand)
            if current_time - last_auth_time > AUTH_INTERVAL:
                emb = encoder.get_embedding(face)
                if emb is not None:
                    is_auth, user = auth.authenticate(emb)
                    if is_auth:
                        print(f"[{time.strftime('%H:%M:%S')}] Utilisateur reconnu: {user}")
                        SystemController.keep_awake()
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] Intrus détecté ! Verrouillage imminent...")
                        # Optionnel : Verrouiller immédiatement si visage inconnu
                        # SystemController.lock_workstation() 
                last_auth_time = current_time
        else:
            # Logique de verrouillage d'absence
            if current_time - last_seen_time > ABSENCE_TIMEOUT:
                print(f"[{time.strftime('%H:%M:%S')}] Absence prolongée. Verrouillage de la session.")
                SystemController.lock_workstation()
                last_seen_time = current_time # Reset pour éviter le spam de la commande

        # En production, retirez l'affichage OpenCV pour que ça tourne vraiment en tâche de fond
        cv2.imshow("FaceLock Debug (Appuyez sur 'q' pour quitter)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()