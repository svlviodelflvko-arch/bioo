import time
import cv2
import numpy as np
import sys
import pyautogui 
from modules.camera_handler import CameraHandler
from modules.face_detector import FaceDetector
from modules.face_encoder import FaceEncoder
from modules.database import DatabaseManager
from modules.face_authenticator import FaceAuthenticator
from modules.system_controller import SystemController

# Configurations
ABSENCE_TIMEOUT = 10
AUTH_INTERVAL = 2
pyautogui.FAILSAFE = False 

def create_lock_screen_image():
    # Crée une image totalement noire (1920x1080)
    img = np.zeros((1080, 1920, 3), dtype=np.uint8)
    cv2.putText(img, "SESSION VERROUILLEE", (600, 500), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 3)
    cv2.putText(img, "Presentez votre visage a la camera pour deverrouiller", (450, 600), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
    return img

def main():
    cam = CameraHandler()
    
    # PATCH VM : Attendre que la caméra s'allume
    camera_ready = False
    for _ in range(30):
        if cam.get_frame() is not None:
            camera_ready = True
            break
        time.sleep(1)

    if not camera_ready:
        print("Erreur critique : Caméra introuvable.")
        sys.exit(1)

    detector = FaceDetector()
    encoder = FaceEncoder()
    db = DatabaseManager()
    auth = FaceAuthenticator(db, threshold=0.45) 

    last_seen_time = time.time()
    last_auth_time = 0
    is_locked = False
    lock_screen_img = create_lock_screen_image()

    print("[+] FaceLock Furtif démarré. Attente de verrouillage...")

    while True:
        frame = cam.get_frame()
        if frame is None:
            time.sleep(0.5) 
            continue

        face = detector.detect_and_crop(frame)
        current_time = time.time()

        if face is not None:
            last_seen_time = current_time
            
            if current_time - last_auth_time > AUTH_INTERVAL:
                emb = encoder.get_embedding(face)
                if emb is not None:
                    is_auth, user = auth.authenticate(emb)
                    if is_auth:
                        SystemController.keep_awake()
                        # DÉVERROUILLAGE
                        if is_locked:
                            is_locked = False
                            print(f"[{time.strftime('%H:%M:%S')}] Déverrouillé par {user}")
                            # --- ENVOI DU LOG DE SUCCÈS À LA BDD ---
                            db.log_access(user, "SUCCES")
                    else:
                        # INTRUS
                        if not is_locked:
                            # --- ENVOI DU LOG D'ÉCHEC À LA BDD ---
                            db.log_access("Inconnu", "ECHEC")
                        is_locked = True
                last_auth_time = current_time
        else:
            if current_time - last_seen_time > ABSENCE_TIMEOUT:
                if not is_locked:
                    print(f"[{time.strftime('%H:%M:%S')}] Verrouillage actif !")
                is_locked = True

        # ==========================================
        # GESTION DE L'AFFICHAGE ET ANTI-NAVIGATION
        # ==========================================
        if is_locked:
            cv2.namedWindow("VERROUILLAGE", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("VERROUILLAGE", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("VERROUILLAGE", lock_screen_img)
            cv2.setWindowProperty("VERROUILLAGE", cv2.WND_PROP_TOPMOST, 1)

            # SÉCURITÉ : On bloque la souris au milieu de l'écran
            pyautogui.moveTo(960, 540)

        else:
            # L'écran est déverrouillé : on détruit l'écran noir
            try:
                cv2.destroyWindow("VERROUILLAGE")
            except:
                pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()