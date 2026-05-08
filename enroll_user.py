import cv2
import numpy as np
from modules.camera_handler import CameraHandler
from modules.face_detector import FaceDetector
from modules.face_encoder import FaceEncoder
from modules.database import DatabaseManager

def main():
    print("=== Enrôlement FaceLock ===")
    username = input("Entrez votre nom d'utilisateur : ")
    
    cam = CameraHandler()
    detector = FaceDetector()
    encoder = FaceEncoder()
    db = DatabaseManager()

    embeddings = []
    print("Tournez légèrement la tête. Appuyez sur 'c' pour capturer, 'q' pour quitter.")

    while len(embeddings) < 5:
        frame = cam.get_frame()
        if frame is None: break

        face = detector.detect_and_crop(frame)
        display_frame = frame.copy()

        if face is not None:
            cv2.putText(display_frame, f"Visage detecte - Captures: {len(embeddings)}/5", 
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Enrolement", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('c') and face is not None:
            emb = encoder.get_embedding(face)
            if emb is not None:
                embeddings.append(emb)
                print(f"Capture {len(embeddings)} réussie.")
        elif key == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    if len(embeddings) == 5:
        # Calculer l'embedding moyen pour plus de précision
        avg_embedding = np.mean(embeddings, axis=0)
        db.add_user(username, avg_embedding)
        print("Enrôlement terminé. Les photos ont été détruites, seul le vecteur est conservé.")
    else:
        print("Enrôlement annulé.")

if __name__ == "__main__":
    main()