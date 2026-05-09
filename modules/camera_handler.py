import cv2

class CameraHandler:
    def __init__(self, camera_index=0):
        # PATCH VM : Utilisation de cv2.CAP_DSHOW pour forcer DirectShow.
        # Cela évite le crash MSMF (-1072875772) très fréquent sur VMware.
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        
        # Optimisation de la résolution pour garantir la fluidité du flux vidéo
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()