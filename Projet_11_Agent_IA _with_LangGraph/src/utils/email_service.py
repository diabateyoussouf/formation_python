import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# --- CONFIGURATION SMTP GMAIL ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "diabateyoussouf.datascience@gmail.com"
SMTP_PASSWORD = "vzyndmraerynbfrt"
DEFAULT_FROM_EMAIL = "Hôtel Le Belvédère <diabateyoussouf.datascience@gmail.com>"


def send_payment_notice_email(
    to_email: str,
    nom_client: str,
    reservation_id: int,
    nom_chambre: str,
    prix_total: float,
    mode_garantie: str,
    date_arrivee: datetime
):
    """Envoie un e-mail de relance/demande de paiement avant la date d'échéance."""
    try:
        # Calcul de la date/heure limite (ex: 18h00 le jour d'arrivée ou sous 24h)
        date_limite_str = (date_arrivee - timedelta(hours=6)).strftime("%d/%m/%Y à 18h00")

        subject = f"🔔 Confirmation & Paiement requis - Réservation #{reservation_id} - Hôtel Le Belvédère"

        # Modèle HTML du mail
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #e2e8f0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #0d1322; border: 1px solid #1f2c40; border-radius: 12px; padding: 24px;">
                <h2 style="color: #ff2a75; margin-top: 0;">Hôtel Le Belvédère - Meknès</h2>
                <p>Bonjour <strong>{nom_client}</strong>,</p>
                <p>Votre pré-réservation <strong>#{reservation_id}</strong> a été enregistrée avec succès.</p>
                
                <div style="background: #131b2e; border-left: 4px solid #ff2a75; padding: 12px 16px; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 4px 0;">🏨 <strong>Chambre :</strong> {nom_chambre}</p>
                    <p style="margin: 4px 0;">💳 <strong>Mode de garantie :</strong> {mode_garantie}</p>
                    <p style="margin: 4px 0;">💰 <strong>Montant total :</strong> {prix_total:.2f} €</p>
                    <p style="margin: 4px 0; color: #f59e0b;">⏳ <strong>Échéance de paiement :</strong> Avant le <strong>{date_limite_str}</strong></p>
                </div>

                <p>Afin de valider définitivement votre chambre et d'éviter sa remise en disponibilité automatique, merci de procéder au règlement ou de confirmer votre arrivée auprès de la réception.</p>
                
                <p style="margin-top: 24px; font-size: 0.85rem; color: #94a3b8;">
                    Pour toute question, répondez directement à cet e-mail ou contactez la réception.<br>
                    Cordialement,<br>
                    <em>L'équipe de l'Hôtel Le Belvédère</em>
                </p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = DEFAULT_FROM_EMAIL
        msg["To"] = to_email
        msg.attach(MIMEText(html_content, "html"))

        # Connexion au serveur SMTP Gmail
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"✅ E-mail envoyé avec succès à {to_email} pour la réservation #{reservation_id}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'e-mail à {to_email} : {e}")
        return False