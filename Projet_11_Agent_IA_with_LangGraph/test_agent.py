import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# Import du graphe compilé depuis src/graph.py
try:
    from src.graph import agent
except ImportError:
    from src.agent.graph import agent


def executer_batterie_de_tests():
    # Définition de l'ensemble des scénarios de test (y compris cas complexes et réels)
    scenarios_test = [
        # ============================================================
        # CATEGORIE 1 : RAG & PROCÉDURES (Services, Équipements, Règles)
        # ============================================================
        {
            "categorie": "1. RAG - Procédures & Réservation",
            "question": "Comment faire la réservation ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "RAG (Doit expliquer les étapes depuis la documentation sans 'Je ne sais pas')"
        },
        {
            "categorie": "1. RAG - Équipements & Services",
            "question": "Quels sont les services proposés par l'hôtel ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "RAG (Liste des services : PMR, Parking, Navette, Séminaires...)"
        },
        {
            "categorie": "1. RAG - Horaires & Accès",
            "question": "À quelle heure le check-in démarre-t-il ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "RAG (Horaires d'arrivée et de départ)"
        },
        {
            "categorie": "1. RAG - Politiques & Animaux",
            "question": "Les animaux de compagnie sont-ils autorisés ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "RAG (Politique de poids <10kg et supplément 15€/nuit)"
        },
        {
            "categorie": "1. RAG - Hors Contexte (Garde-fou)",
            "question": "Avez-vous une navette spatiale vers la Lune ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "RAG -> Doit répondre 'Je ne sais pas, veuillez contacter la réception.'"
        },

        # ============================================================
        # CATEGORIE 2 : DISPONIBILITÉ & TARIFS PAR CHAMBRE
        # ============================================================
        {
            "categorie": "2. DISPO & Tarifs - Chambre BDD Existante",
            "question": "Est-ce qu'il reste une Suite Royale Vue Jardin libre ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "DISPO -> Stock et tarifs (basse/haute saison) de la Suite Royale Vue Jardin"
        },
        {
            "categorie": "2. DISPO & Tarifs - Demande de prix",
            "question": "Les prix de la chambre Vue Panorama ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "DISPO -> Doit donner le tarif exact et le stock de la chambre Vue Panorama"
        },
        {
            "categorie": "2. DISPO & Tarifs - Liste Générale",
            "question": "Quelles sont les catégories de chambres disponibles ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "DISPO / RAG -> Doit lister les catégories existantes"
        },
        {
            "categorie": "2. DISPO & Tarifs - Chambre Inexistante",
            "question": "Avez-vous une Suite Spatiale disponible ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "DISPO -> Indique que la chambre n'existe pas et donne les catégories réelles"
        },

        # ============================================================
        # CATEGORIE 3 : CALCULS DE SÉJOUR
        # ============================================================
        {
            "categorie": "3. CALCUL - Multi-nuits simple",
            "question": "Combien coûtent 4 nuits à 110 € ?",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "CALCUL -> 440€ + taxe de séjour (10€) = 450€"
        },
        {
            "categorie": "3. CALCUL - Décimales",
            "question": "Calculer le tarif pour 3 nuits à 85.50 €",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "CALCUL -> Gestion propre des décimales"
        },

        # ============================================================
        # CATEGORIE 4 : SÉCURITÉ / ANNULATION & RBAC
        # ============================================================
        {
            "categorie": "4. ANNULATION - Bloqué si non connecté",
            "question": "Je veux annuler une réservation sous l'adresse test@gmail.com",
            "user_email": None,
            "user_role": "client",
            "attendu": "ANNULATION -> ⛔ Bloqué (Sécurité : vous devez être connecté)"
        },
        {
            "categorie": "4. ANNULATION - Bloqué si Usurpation IDOR",
            "question": "Je veux annuler la réservation de youssouf@example.com",
            "user_email": "hacker@gmail.com",
            "user_role": "client",
            "attendu": "ANNULATION -> ⛔ Refusé (Le compte connecté ne correspond pas à la réservation)"
        },
        {
            "categorie": "4. ANNULATION - Email inexistant en BDD",
            "question": "Je veux annuler une réservation avec l'adresse y.diabate@gamail.com ?",
            "user_email": "y.diabate@gamail.com",
            "user_role": "client",
            "attendu": "ANNULATION -> Aucune réservation correspondante n'a été trouvée"
        },
        {
            "categorie": "4. ANNULATION - Client Légitime (Étape 1 : Identification)",
            "question": "Je veux annuler ma réservation sous l'adresse youssouf@example.com",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "ANNULATION -> Identifie la réservation #2 et DEMANDE confirmation explicite"
        },
        {
            "categorie": "4. ANNULATION - Client Légitime (Étape 2 : Confirmation)",
            "question": "Oui, je confirme l'annulation de ma réservation #2",
            "user_email": "youssouf@example.com",
            "user_role": "client",
            "attendu": "ANNULATION -> Confirme la suppression et réintègre +1 au stock"
        },
        {
            "categorie": "4. ANNULATION - Mode Admin Bypass",
            "question": "Je veux annuler la réservation #2 pour le client client@gmail.com",
            "user_email": "admin@belvedere.com",
            "user_role": "admin",
            "attendu": "ANNULATION -> Autorisé car rôle = admin"
        }
    ]

    print("=" * 80)
    print("🚀 DÉMARRAGE DE LA BATTERIE DE TESTS COMPLETE DE L'AGENT IA")
    print("=" * 80)

    succes_count = 0
    total_tests = len(scenarios_test)

    for idx, test in enumerate(scenarios_test, start=1):
        print(f"\n--- [Test {idx}/{total_tests}] {test['categorie']} ---")
        print(f"👤 Question Client : \"{test['question']}\"")
        print(f"🔑 Session User    : Email={test['user_email']} | Role={test['user_role']}")
        print(f"🎯 Attendu         : {test['attendu']}")

        input_state = {
            "question": test["question"],
            "user_email": test["user_email"],
            "user_role": test["user_role"]
        }

        try:
            resultat = agent.invoke(input_state)

            decision = resultat.get("decision", "INCONNUE")
            reponse = resultat.get("reponse", "AUCUNE RÉPONSE")

            print(f"⚙️ Intention Prise : \033[1m{decision}\033[0m")
            print(f"🤖 Réponse Agent   :\n{reponse}")
            succes_count += 1

        except Exception as e:
            print(f"❌ ERREUR LORS DE L'EXÉCUTION : {str(e)}")

        print("-" * 80)

    print("\n" + "=" * 80)
    print(f"📊 FIN DU TEST : {succes_count}/{total_tests} scénarios exécutés avec succès.")
    print("=" * 80)


if __name__ == "__main__":
    executer_batterie_de_tests()