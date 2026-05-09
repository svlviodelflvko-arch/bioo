from scipy.spatial.distance import cosine

class FaceAuthenticator:
    def __init__(self, database, threshold=0.4):
        self.database = database
        self.threshold = threshold

    def authenticate(self, current_embedding):
        users = self.database.get_all_users()
        if not users:
            return False, "Aucun utilisateur en base."

        best_match = None
        lowest_distance = float('inf')

        for username, stored_embedding in users:
            # Calcul de la distance cosinus pour comparer les visages
            dist = cosine(current_embedding, stored_embedding)
            if dist < lowest_distance:
                lowest_distance = dist
                best_match = username

        # Si la distance est sous le seuil de tolérance, c'est la bonne personne
        if lowest_distance <= self.threshold:
            return True, best_match
        return False, "Inconnu"