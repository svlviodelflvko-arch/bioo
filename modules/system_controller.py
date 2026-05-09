import ctypes
import pyautogui
pyautogui.FAILSAFE = False

class SystemController:
    @staticmethod
    def lock_workstation():
        # Appel direct à l'API Windows pour verrouiller la session
        ctypes.windll.user32.LockWorkStation()

    @staticmethod
    def keep_awake():
        # Simule l'appui sur une touche inoffensive pour empêcher la mise en veille
        pyautogui.press('volumedown')
        pyautogui.press('volumeup')