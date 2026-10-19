import re
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from src.db.session import SessionLocal
from src.db.models import ReservationModel, ChambreModel


# ============================================================
# OUTIL 1 : Calcul de facture et devis
# ============================================================

def calculer_facture(nombre_nuits: int, prix_par_nuit: float) -> str:
    """Calcule le montant total d'un séjour incluant la taxe de séjour."""
    taxe_sejour = 2.50 * nombre_nuits
    total = (nombre_nuits * prix_par_nuit) + taxe_sejour
    return (
        f"📊 **Devis estimatif** pour {nombre_nuits} nuit(s) :\n"
        f"- Nuits : {nombre_nuits} × {prix_par_nuit:.2f} € = {nombre_nuits * prix_par_nuit:.2f} €\n"
        f"- Taxe de séjour : {taxe_sejour:.2f} € (2.50 € / nuit)\n"
        f"💶 **Total à régler** : **{total:.2f} €**"
    )


# ============================================================
# OUTIL 2 : Consultation de disponibilité et Catalogue
# ============================================================

def verifier_disponibilite(type_chambre: Optional[str] = "") -> str:
    """Vérifie la disponibilité actuelle des chambres dans l'établissement."""
    db: Session = SessionLocal()
    try:
        terme = (type_chambre or "").strip().lower()
        mots_generiques = {
            "", "chambre", "chambres", "suite", "suites", 
            "toutes", "all", "catalogue", "disponible", 
            "disponibles", "libre", "libres"
        }

        if terme in mots_generiques:
            chambres = db.query(ChambreModel).all()
            if not chambres:
                return "Aucune chambre n'est répertoriée dans le système."

            lignes = ["🏨 **Catalogue & Disponibilités actuelles de l'Hôtel Le Belvédère** :\n"]
            for c in chambres:
                stock_val = getattr(c, "stock", getattr(c, "disponible", 0))
                statut = f"✅ **{stock_val} disponible(s)**" if stock_val > 0 else "❌ **Complet**"
                lignes.append(
                    f"- **{c.nom}** : {statut} | {c.prix_basse:.2f} € (Basse) — {c.prix_haute:.2f} € (Haute)"
                )
            return "\n".join(lignes)

        chambre = db.query(ChambreModel).filter(ChambreModel.nom.ilike(f"%{terme}%")).first()

        if not chambre:
            chambres_existantes = db.query(ChambreModel).all()
            noms = ", ".join([c.nom for c in chambres_existantes]) if chambres_existantes else "Aucune"
            return f"Aucune catégorie correspondant à '{type_chambre}' n'a été trouvée. Catégories disponibles : {noms}."

        details = []
        if getattr(chambre, "surface", None):
            details.append(f"Surface : {chambre.surface}")
        if getattr(chambre, "vue", None):
            details.append(f"Vue : {chambre.vue}")
        if getattr(chambre, "lit", None):
            details.append(f"Literie : {chambre.lit}")

        info_supp = f" ({', '.join(details)})" if details else ""
        stock_val = getattr(chambre, "stock", getattr(chambre, "disponible", 0))

        if stock_val > 0:
            return (
                f"🛏️ **{chambre.nom}**{info_supp} :\n"
                f"- **Stock** : ✅ {stock_val} chambre(s) libre(s)\n"
                f"- **Tarifs** : {chambre.prix_basse:.2f} € / nuit (Basse saison) | {chambre.prix_haute:.2f} € / nuit (Haute saison)"
            )
        else:
            return (
                f"La chambre **{chambre.nom}** est actuellement **complète**.\n"
                f"- **Tarifs indicatifs** : {chambre.prix_basse:.2f} € / nuit (Basse) | {chambre.prix_haute:.2f} € / nuit (Haute)"
            )
    finally:
        db.close()


# ============================================================
# OUTIL 3 : Création directe de réservation (Avec Statut & Garantie)
# ============================================================

def creer_reservation(
    type_chambre: str, 
    user_email: Optional[str] = None, 
    nom_client: Optional[str] = None,
    mode_garantie: Optional[str] = "RECEPTION",
    ref_virement: Optional[str] = None
) -> str:
    """Crée une nouvelle réservation en base de données avec statut et mode de garantie."""
    if not user_email or not str(user_email).strip():
        return "⛔ **Connexion requise** : Veuillez vous connecter à votre compte pour valider votre réservation."

    clean_email = str(user_email).strip().lower()
    db: Session = SessionLocal()
    try:
        chambre = db.query(ChambreModel).filter(ChambreModel.nom.ilike(f"%{type_chambre}%")).first()
        if not chambre:
            chambres = db.query(ChambreModel).all()
            noms = ", ".join([c.nom for c in chambres])
            return f"Impossible de réserver : la catégorie '{type_chambre}' n'existe pas. Choix possibles : {noms}."

        stock_val = getattr(chambre, "stock", getattr(chambre, "disponible", 0))
        if stock_val <= 0:
            return f"Désolé, la catégorie **{chambre.nom}** est actuellement complète."

        nom_final = nom_client or clean_email.split("@")[0].capitalize()
        now = datetime.utcnow()
        date_arr = now + timedelta(days=1)
        date_dep = date_arr + timedelta(days=1)
        prix = float(chambre.prix_basse)

        # Détermination automatique du statut initial (correction de la faute de frappe)
        garantie_clean = (mode_garantie or "RECEPTION").upper()
        if garantie_clean == "CARTE":
            statut_init = "CONFIRMEE"
            garantie_txt = "Paiement CB validé"
        elif garantie_clean == "VIREMENT":
            statut_init = "EN_ATTENTE"
            garantie_txt = f"Virement bancaire (Réf: {ref_virement or 'N/A'})"
        else:
            statut_init = "EN_ATTENTE"
            garantie_txt = "Paiement à la réception (Garantie jusqu'à 18h00)"

        nouvelle_res = ReservationModel(
            nom_client=nom_final,
            email_client=clean_email,
            chambre_id=chambre.id,
            date_arrivee=date_arr,
            date_depart=date_dep,
            nb_personnes=1,
            prix_total=prix,
            statut=statut_init,
            mode_garantie=garantie_clean,
            ref_virement=ref_virement,
            created_at=now
        )

        if hasattr(chambre, "stock") and chambre.stock > 0:
            chambre.stock -= 1
        elif hasattr(chambre, "disponible") and chambre.disponible > 0:
            chambre.disponible -= 1

        db.add(nouvelle_res)
        db.commit()
        db.refresh(nouvelle_res)

        return (
            f"🎉 **Pré-réservation enregistrée avec succès !**\n"
            f"- **Numéro de réservation** : #{nouvelle_res.id}\n"
            f"- **Statut** : `{statut_init}`\n"
            f"- **Garantie** : {garantie_txt}\n"
            f"- **Client** : {nom_final} ({clean_email})\n"
            f"- **Chambre** : {chambre.nom}\n"
            f"- **Dates** : du {date_arr.strftime('%d/%m/%Y')} au {date_dep.strftime('%d/%m/%Y')}\n"
            f"- **Montant total** : {prix:.2f} €\n\n"
            f"Un e-mail de récapitulatif a été transmis à **{clean_email}**."
        )
    except Exception as e:
        db.rollback()
        return f"⚠️ Erreur lors de la création de la réservation : {str(e)}"
    finally:
        db.close()


# ============================================================
# OUTIL 4 : Consultation des réservations client
# ============================================================

def consulter_mes_reservations(user_email: Optional[str] = None) -> str:
    """Liste toutes les réservations d'un client avec leur statut."""
    if not user_email or not str(user_email).strip():
        return "⛔ **Connexion requise** : Veuillez vous connecter pour consulter vos réservations."

    clean_email = str(user_email).strip().lower()
    db: Session = SessionLocal()
    try:
        reservations = db.query(ReservationModel).options(
            joinedload(ReservationModel.chambre)
        ).filter(
            ReservationModel.email_client == clean_email
        ).all()

        if not reservations:
            return f"Vous n'avez actuellement aucune réservation enregistrée sous l'adresse **{clean_email}**."

        lignes = [f"📋 **Vos réservations ({len(reservations)})** :\n"]
        for r in reservations:
            nom_chambre = r.chambre.nom if r.chambre else f"Chambre #{r.chambre_id}"
            statut_display = getattr(r, "statut", "EN_ATTENTE")
            garantie_display = getattr(r, "mode_garantie", "RECEPTION") or "RECEPTION"
            
            lignes.append(
                f"- **Réservation #{r.id}** : {nom_chambre} "
                f"(du {r.date_arrivee.strftime('%d/%m/%Y')} au {r.date_depart.strftime('%d/%m/%Y')} — {r.prix_total:.2f} €) | "
                f"Statut : **{statut_display}** ({garantie_display})"
            )

        lignes.append("\n💡 *Pour annuler une réservation spécifique, dites : « Annuler la réservation #ID ».*")
        return "\n".join(lignes)
    except Exception as e:
        return f"⚠️ Erreur lors de la consultation de vos réservations : {str(e)}"
    finally:
        db.close()


# ============================================================
# OUTIL 5 : Annulation ciblée, libération du stock et sécurité
# ============================================================

def consulter_et_annuler_reservation(
    question: str, 
    user_email: Optional[str] = None, 
    user_role: Optional[str] = "client"
) -> str:
    """Consulte ou annule une réservation spécifique avec remise en stock automatique."""
    if not user_email or not str(user_email).strip():
        return "⛔ Sécurité : Vous devez être connecté à votre compte pour effectuer une annulation."

    clean_user_email = str(user_email).strip().lower()

    match_email = re.search(r"[\w.-]+@[\w.-]+\.\w+", question)
    target_email = match_email.group(0).lower() if match_email else clean_user_email

    if (user_role or "client").lower() != "admin" and target_email != clean_user_email:
        return (
            f"⛔ Sécurité : Vous êtes connecté avec le compte '{clean_user_email}'. "
            f"Vous ne pouvez pas annuler la réservation appartenant à '{target_email}'."
        )

    db: Session = SessionLocal()
    try:
        reservations = db.query(ReservationModel).options(
            joinedload(ReservationModel.chambre)
        ).filter(
            ReservationModel.email_client == target_email
        ).all()

        if not reservations:
            return f"Aucune réservation n'a été trouvée pour l'adresse **{target_email}**."

        match_id = re.search(r"(?:#|id\s*|réservation\s*|numéro\s*)(\d+)", question.lower())
        requested_id = int(match_id.group(1)) if match_id else None

        res_cible = None
        if requested_id:
            for r in reservations:
                if r.id == requested_id:
                    res_cible = r
                    break
            if not res_cible:
                ids_existants = ", ".join([f"#{r.id}" for r in reservations])
                return f"La réservation **#{requested_id}** n'a pas été trouvée parmi vos réservations actives ({ids_existants})."
        else:
            res_cible = reservations[-1]

        question_lower = question.lower().strip()
        mots_confirmation = ["oui", "confirme", "valide", "d'accord", "je confirme"]
        est_confirmation = any(m in question_lower for m in mots_confirmation) and ("non" not in question_lower)

        res_id = res_cible.id
        res_chambre = res_cible.chambre
        nom_chambre = res_chambre.nom if res_chambre else f"Chambre #{res_cible.chambre_id}"
        res_nom = res_cible.nom_client
        res_email = res_cible.email_client

        if est_confirmation:
            if res_chambre:
                if hasattr(res_chambre, "stock"):
                    res_chambre.stock += 1
                elif hasattr(res_chambre, "disponible"):
                    res_chambre.disponible += 1

            db.delete(res_cible)
            db.commit()

            return (
                f"✅ **Annulation effectuée** : La réservation **#{res_id}** ({nom_chambre}) "
                f"au nom de **{res_nom}** ({res_email}) a été annulée et la chambre a été remise en disponible."
            )

        statut_actuel = getattr(res_cible, "statut", "EN_ATTENTE")
        return (
            f"🔎 **Réservation identifiée** : ID #{res_id} ({nom_chambre}) - Statut : `{statut_actuel}` "
            f"au nom de **{res_nom}** ({res_email}).\n\n"
            f"Pour confirmer définitivement l'annulation, veuillez répondre : "
            f"**« Oui, je confirme l'annulation de la réservation #{res_id} »**."
        )
    except Exception as e:
        db.rollback()
        return f"⚠️ Erreur lors de l'annulation : {str(e)}"
    finally:
        db.close()