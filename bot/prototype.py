"""
SafeHer Bot - Version Prototype CORRIGÉE
=========================================
Bot Telegram avec données statiques (sans base de données)
Bugs fixés : tel: URLs, parsing des étapes
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# ============================================================================
# CONFIGURATION
# ============================================================================

# 🔑 METS TON TOKEN ICI (obtenu via @BotFather)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8381412145:AAEfcvXy76kBNyVLI9YE6WLbhTH-KsgprPs")

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# États de conversation
(
    MAIN_MENU,
    URGENCY_CHECK,
    VBG_TYPE,
    EXPERT_PARCOURS,
    CONTACTS_SETUP,
    CONTACT_NAME,
    CONTACT_PHONE,
    SOS_CONFIRM
) = range(8)

# ============================================================================
# 📊 DONNÉES STATIQUES - EXPERTS CAMEROUN
# ============================================================================

EXPERTS = {
    "medical": [
        {
            "nom": "Hôpital Central de Yaoundé",
            "telephone": "+237 222 23 40 20",
            "ville": "Yaoundé",
            "urgence_24h": True,
            "gratuit": False,
            "specialite": "Urgences, certificat médical, soins"
        },
        {
            "nom": "Hôpital Laquintinie",
            "telephone": "+237 233 42 60 91",
            "ville": "Douala",
            "urgence_24h": True,
            "gratuit": False,
            "specialite": "Urgences, certificat médical"
        },
        {
            "nom": "Centre Mère-Enfant FCB",
            "telephone": "+237 222 23 14 89",
            "ville": "Yaoundé",
            "urgence_24h": True,
            "gratuit": False,
            "specialite": "Santé femme et enfant"
        }
    ],
    "psychologue": [
        {
            "nom": "Association ALVF",
            "telephone": "+237 222 20 29 24",
            "ville": "Yaoundé",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Accompagnement psychologique victimes VBG"
        },
        {
            "nom": "Centre d'Écoute Psychologique",
            "telephone": "+237 677 50 00 00",
            "ville": "Douala",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Soutien psychologique, trauma"
        }
    ],
    "avocat": [
        {
            "nom": "Clinique Juridique ACAT",
            "telephone": "+237 222 20 55 22",
            "ville": "Yaoundé",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Aide juridique gratuite, droits des femmes"
        },
        {
            "nom": "Barreau du Cameroun - Aide juridictionnelle",
            "telephone": "+237 222 22 00 00",
            "ville": "National",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Aide juridictionnelle"
        }
    ],
    "police": [
        {
            "nom": "Police Nationale - Urgences",
            "telephone": "117",
            "ville": "National",
            "urgence_24h": True,
            "gratuit": True,
            "specialite": "Urgences, dépôt de plainte"
        },
        {
            "nom": "Gendarmerie Nationale",
            "telephone": "113",
            "ville": "National",
            "urgence_24h": True,
            "gratuit": True,
            "specialite": "Urgences zones rurales"
        }
    ],
    "assistant_social": [
        {
            "nom": "MINAS - Ministère Affaires Sociales",
            "telephone": "+237 222 23 21 40",
            "ville": "Yaoundé",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Aide sociale, hébergement d'urgence"
        }
    ],
    "hebergement": [
        {
            "nom": "Foyer de l'Espérance",
            "telephone": "+237 699 00 00 00",
            "ville": "Yaoundé",
            "urgence_24h": True,
            "gratuit": True,
            "specialite": "Hébergement d'urgence femmes victimes"
        },
        {
            "nom": "Centre d'Accueil MINPROFF",
            "telephone": "+237 222 22 33 44",
            "ville": "Douala",
            "urgence_24h": True,
            "gratuit": True,
            "specialite": "Accueil et hébergement temporaire"
        }
    ],
    "ong_vbg": [
        {
            "nom": "AlertGBV Cameroun",
            "telephone": "+237 242 232 170",
            "whatsapp": True,
            "ville": "National",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Signalement, orientation, accompagnement VBG"
        },
        {
            "nom": "RENATA",
            "telephone": "+237 677 00 00 00",
            "ville": "National",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Réseau contre les violences faites aux femmes"
        },
        {
            "nom": "ACAFEJ",
            "telephone": "+237 222 20 44 88",
            "ville": "Yaoundé",
            "urgence_24h": False,
            "gratuit": True,
            "specialite": "Assistance juridique femmes"
        }
    ]
}

# ============================================================================
# 📋 PARCOURS PAR TYPE DE VBG
# ============================================================================

PARCOURS = {
    "physique": {
        "titre": "Violence Physique",
        "emoji": "👊",
        "description": "Coups, blessures, séquestration...",
        "urgence": True,
        "etapes": [
            {
                "ordre": 1,
                "expert_type": "medical",
                "titre": "🏥 Soins médicaux",
                "description": "Consultez un médecin pour vos blessures et obtenez un certificat médical (important pour une plainte).",
                "obligatoire": True,
                "delai": "⚠️ Immédiat"
            },
            {
                "ordre": 2,
                "expert_type": "police",
                "titre": "👮 Dépôt de plainte",
                "description": "Déposez plainte avec votre certificat médical. Gardez une copie du récépissé.",
                "obligatoire": False,
                "delai": "Dans les 72h si possible"
            },
            {
                "ordre": 3,
                "expert_type": "avocat",
                "titre": "⚖️ Conseil juridique",
                "description": "Un avocat peut vous accompagner dans la procédure et défendre vos droits.",
                "obligatoire": False,
                "delai": "Après le dépôt de plainte"
            },
            {
                "ordre": 4,
                "expert_type": "psychologue",
                "titre": "🧠 Soutien psychologique",
                "description": "Parlez à un professionnel pour vous aider à surmonter ce traumatisme.",
                "obligatoire": True,
                "delai": "Dès que possible"
            },
            {
                "ordre": 5,
                "expert_type": "hebergement",
                "titre": "🏠 Mise en sécurité",
                "description": "Si vous êtes en danger chez vous, des centres peuvent vous héberger.",
                "obligatoire": False,
                "delai": "Si nécessaire"
            }
        ]
    },
    "sexuelle": {
        "titre": "Violence Sexuelle",
        "emoji": "⚠️",
        "description": "Viol, agression sexuelle, attouchements...",
        "urgence": True,
        "etapes": [
            {
                "ordre": 1,
                "expert_type": "medical",
                "titre": "🏥 Examen médical URGENT",
                "description": "⚠️ IMPORTANT: Consultez dans les 72h maximum pour le certificat médico-légal et les soins.\n\n❌ Ne vous lavez pas avant l'examen\n❌ Ne changez pas de vêtements si possible",
                "obligatoire": True,
                "delai": "🔴 URGENT - 72h maximum"
            },
            {
                "ordre": 2,
                "expert_type": "police",
                "titre": "👮 Dépôt de plainte",
                "description": "Vous pouvez porter plainte. C'est votre choix et votre droit. Un accompagnant peut vous aider.",
                "obligatoire": False,
                "delai": "Quand vous vous sentirez prête"
            },
            {
                "ordre": 3,
                "expert_type": "psychologue",
                "titre": "🧠 Accompagnement psychologique",
                "description": "Un soutien psychologique spécialisé est essentiel après un traumatisme sexuel. Vous n'êtes pas seule.",
                "obligatoire": True,
                "delai": "Dès que possible"
            },
            {
                "ordre": 4,
                "expert_type": "avocat",
                "titre": "⚖️ Aide juridique",
                "description": "Un avocat peut vous accompagner si vous décidez de poursuivre l'agresseur.",
                "obligatoire": False,
                "delai": "Selon votre décision"
            }
        ]
    },
    "psychologique": {
        "titre": "Violence Psychologique",
        "emoji": "🧠",
        "description": "Insultes, humiliations, menaces, isolement, contrôle...",
        "urgence": False,
        "etapes": [
            {
                "ordre": 1,
                "expert_type": "psychologue",
                "titre": "🧠 Soutien psychologique",
                "description": "Parler à un professionnel vous aidera à comprendre votre situation et à reprendre confiance en vous.",
                "obligatoire": True,
                "delai": "Dès que possible"
            },
            {
                "ordre": 2,
                "expert_type": "ong_vbg",
                "titre": "🤝 Accompagnement associatif",
                "description": "Les associations spécialisées peuvent vous aider dans vos démarches et vous soutenir.",
                "obligatoire": False,
                "delai": "Quand vous êtes prête"
            },
            {
                "ordre": 3,
                "expert_type": "assistant_social",
                "titre": "👥 Aide sociale",
                "description": "Si vous avez besoin d'aide pour vous reconstruire (logement, emploi...).",
                "obligatoire": False,
                "delai": "Selon vos besoins"
            },
            {
                "ordre": 4,
                "expert_type": "avocat",
                "titre": "⚖️ Conseil juridique",
                "description": "Si la situation empire ou si vous voulez vous protéger légalement (divorce, ordonnance de protection).",
                "obligatoire": False,
                "delai": "Si nécessaire"
            }
        ]
    },
    "economique": {
        "titre": "Violence Économique",
        "emoji": "💰",
        "description": "Privation d'argent, interdiction de travailler, vol de salaire...",
        "urgence": False,
        "etapes": [
            {
                "ordre": 1,
                "expert_type": "assistant_social",
                "titre": "👥 Aide sociale",
                "description": "Un assistant social peut vous aider à accéder à vos droits et à des aides financières d'urgence.",
                "obligatoire": True,
                "delai": "Dès que possible"
            },
            {
                "ordre": 2,
                "expert_type": "avocat",
                "titre": "⚖️ Conseil juridique",
                "description": "Connaître vos droits financiers, notamment en cas de séparation ou de divorce.",
                "obligatoire": True,
                "delai": "Rapidement"
            },
            {
                "ordre": 3,
                "expert_type": "ong_vbg",
                "titre": "🤝 Accompagnement vers l'autonomie",
                "description": "Certaines associations proposent des formations et aides à l'emploi pour retrouver votre indépendance.",
                "obligatoire": False,
                "delai": "Selon vos besoins"
            },
            {
                "ordre": 4,
                "expert_type": "psychologue",
                "titre": "🧠 Soutien psychologique",
                "description": "La violence économique a aussi un impact sur votre bien-être mental et votre confiance.",
                "obligatoire": False,
                "delai": "Quand vous le souhaitez"
            }
        ]
    },
    "mariage": {
        "titre": "Mariage Forcé / Précoce",
        "emoji": "💒",
        "description": "Mariage imposé, mariage avant 18 ans...",
        "urgence": True,
        "etapes": [
            {
                "ordre": 1,
                "expert_type": "ong_vbg",
                "titre": "🤝 Contact ONG spécialisée",
                "description": "Des associations spécialisées peuvent vous aider à vous mettre en sécurité rapidement et discrètement.",
                "obligatoire": True,
                "delai": "🔴 URGENT"
            },
            {
                "ordre": 2,
                "expert_type": "assistant_social",
                "titre": "👥 Protection sociale",
                "description": "Les services sociaux peuvent intervenir pour protéger les mineures en danger.",
                "obligatoire": True,
                "delai": "Immédiat si mineure"
            },
            {
                "ordre": 3,
                "expert_type": "avocat",
                "titre": "⚖️ Aide juridique",
                "description": "Un avocat peut vous aider à faire annuler un mariage forcé ou à vous protéger légalement.",
                "obligatoire": True,
                "delai": "Rapidement"
            },
            {
                "ordre": 4,
                "expert_type": "hebergement",
                "titre": "🏠 Hébergement sécurisé",
                "description": "Si vous devez quitter votre domicile pour votre sécurité.",
                "obligatoire": False,
                "delai": "Si nécessaire"
            },
            {
                "ordre": 5,
                "expert_type": "psychologue",
                "titre": "🧠 Accompagnement psychologique",
                "description": "Pour vous aider à traverser cette épreuve et reconstruire votre vie.",
                "obligatoire": False,
                "delai": "Dès que possible"
            }
        ]
    },
    "cyber": {
        "titre": "Cyberviolence",
        "emoji": "📱",
        "description": "Harcèlement en ligne, revenge porn, doxxing, surveillance...",
        "urgence": False,
        "etapes": [
            {
                "ordre": 1,
                "expert_type": "ong_vbg",
                "titre": "📱 Conseils sécurité numérique",
                "description": "Apprenez à sécuriser vos comptes et à collecter les preuves correctement:\n\n📸 Faites des captures d'écran\n🔒 Changez vos mots de passe\n🚫 Bloquez les harceleurs",
                "obligatoire": True,
                "delai": "Immédiat"
            },
            {
                "ordre": 2,
                "expert_type": "police",
                "titre": "👮 Signalement / Plainte",
                "description": "Le cyberharcèlement est un délit puni par la loi. Vous pouvez porter plainte avec vos preuves (captures d'écran).",
                "obligatoire": False,
                "delai": "Après collecte de preuves"
            },
            {
                "ordre": 3,
                "expert_type": "psychologue",
                "titre": "🧠 Soutien psychologique",
                "description": "Le cyberharcèlement peut être très traumatisant. N'hésitez pas à en parler à un professionnel.",
                "obligatoire": True,
                "delai": "Dès que possible"
            },
            {
                "ordre": 4,
                "expert_type": "avocat",
                "titre": "⚖️ Aide juridique",
                "description": "Pour faire retirer les contenus illicites et poursuivre les harceleurs en justice.",
                "obligatoire": False,
                "delai": "Si vous souhaitez poursuivre"
            }
        ]
    }
}

# ============================================================================
# 💬 MESSAGES
# ============================================================================

MESSAGES = {
    "welcome": """
🛡️ *Bienvenue sur SafeHer*

Je suis votre assistant confidentiel pour vous accompagner face aux Violences Basées sur le Genre.

💜 *Je peux vous aider à :*
• Identifier votre situation
• Vous orienter vers les bons experts
• Alerter vos proches en cas d'urgence
• Trouver des ressources d'aide

🔒 *Tout est 100% confidentiel.*

Comment puis-je vous aider aujourd'hui ?
""",

    "urgency_check": """
⚠️ *Avant tout, êtes-vous en sécurité ?*

Choisissez l'option qui correspond à votre situation actuelle :
""",

    "immediate_danger": """
🆘 *ALERTE URGENCE*

Si vous êtes en danger immédiat, appelez immédiatement :

📞 *Police : 117*
📞 *Gendarmerie : 113*

Restez en ligne avec eux jusqu'à l'arrivée des secours.

💜 Vous n'êtes pas seule.
""",

    "vbg_type_question": """
💬 *Parlez-moi de votre situation*

Quel type de violence vivez-vous ou avez-vous vécu ?

_(Sélectionnez l'option la plus proche de votre situation. Si vous n'êtes pas sûre, choisissez "Je ne sais pas")_
""",

    "sos_sent": """
🆘 *ALERTE ENVOYÉE*

✅ Vos contacts de confiance ont été alertés
📍 Votre position a été partagée

🚨 Restez en sécurité. Aide en route.

📞 En cas d'extrême urgence : *117*
""",

    "no_contacts": """
⚠️ *Aucun contact de confiance configuré*

Pour utiliser l'alerte SOS, vous devez d'abord configurer vos contacts de confiance.

En attendant, si vous êtes en danger :
📞 Appelez le *117* (Police)
📞 Appelez le *113* (Gendarmerie)
""",

    "contact_added": """
✅ *Contact ajouté avec succès !*

*{name}* ({phone}) fait maintenant partie de vos contacts de confiance.

En cas d'alerte SOS, cette personne sera prévenue automatiquement.

📊 Vous avez *{count}/3* contacts configurés.
""",

    "info_vbg": """
📚 *Qu'est-ce qu'une VBG ?*

Une Violence Basée sur le Genre est tout acte nuisible perpétré contre une personne en raison de son genre.

*3 critères définissent une VBG :*

⚖️ *Déséquilibre de pouvoir*
Une relation où l'un domine l'autre (conjoint, parent, employeur, figure d'autorité...)

🚫 *Absence de consentement*
La victime n'a pas donné son accord libre et éclairé, ou n'est pas en mesure de le faire

🏛️ *Construction sociale*
La violence s'appuie sur des normes de genre, des traditions ou des croyances discriminatoires

💜 *Vous n'êtes jamais responsable des violences que vous subissez.*
"""
}

# ============================================================================
# 🤖 HANDLERS DU BOT
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Démarre le bot et affiche le menu principal"""
    # Initialiser les données utilisateur
    if 'contacts' not in context.user_data:
        context.user_data['contacts'] = []
    
    keyboard = [
        [InlineKeyboardButton("🆘 J'ai besoin d'aide MAINTENANT", callback_data="urgency")],
        [InlineKeyboardButton("💬 Parler de ma situation", callback_data="situation")],
        [InlineKeyboardButton("📚 M'informer sur les VBG", callback_data="info")],
        [InlineKeyboardButton("👥 Mes contacts de confiance", callback_data="contacts")],
        [InlineKeyboardButton("📍 Ressources et numéros utiles", callback_data="resources")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            MESSAGES["welcome"],
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            MESSAGES["welcome"],
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    return MAIN_MENU


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gère les choix du menu principal"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "urgency":
        return await handle_urgency(update, context)
    elif query.data == "situation":
        return await ask_vbg_type(update, context)
    elif query.data == "info":
        return await show_info(update, context)
    elif query.data == "contacts":
        return await show_contacts(update, context)
    elif query.data == "resources":
        return await show_resources(update, context)
    elif query.data == "back_main":
        return await start(update, context)
    elif query.data.startswith("expert_"):
        return await show_experts_by_type(update, context)
    elif query.data.startswith("info_"):
        return await show_info_type(update, context)
    
    return MAIN_MENU


async def handle_urgency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gère les situations d'urgence"""
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("🔴 Je suis en DANGER maintenant", callback_data="danger_now")],
        [InlineKeyboardButton("🟠 Je ne suis pas en sécurité chez moi", callback_data="unsafe_home")],
        [InlineKeyboardButton("🟡 J'ai peur mais pas de danger immédiat", callback_data="afraid")],
        [InlineKeyboardButton("🟢 Je suis en sécurité", callback_data="safe")],
        [InlineKeyboardButton("◀️ Retour au menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES["urgency_check"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return URGENCY_CHECK


async def urgency_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Répond selon le niveau d'urgence"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "danger_now":
        # CORRIGÉ: Plus de url="tel:117" - on affiche juste les numéros
        keyboard = [
            [InlineKeyboardButton("🆘 Alerter mes contacts SOS", callback_data="send_sos")],
            [InlineKeyboardButton("◀️ Retour", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES["immediate_danger"],
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return SOS_CONFIRM
        
    elif query.data == "unsafe_home":
        message = """
🏠 *Vous n'êtes pas en sécurité chez vous*

Je comprends. Voici vos options :

*1️⃣ Hébergement d'urgence*
Des centres peuvent vous accueillir cette nuit.

*2️⃣ Aller chez un proche*
Avez-vous quelqu'un de confiance ?

*3️⃣ Préparer un départ*
Documents importants à prendre :
• Carte d'identité
• Carnet de santé
• Argent / carte bancaire
• Téléphone et chargeur
• Vêtements essentiels

💜 Votre sécurité est la priorité.
"""
        keyboard = [
            [InlineKeyboardButton("🏠 Trouver un hébergement", callback_data="expert_hebergement")],
            [InlineKeyboardButton("💬 Parler de ma situation", callback_data="situation")],
            [InlineKeyboardButton("◀️ Retour", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        return MAIN_MENU
        
    elif query.data in ["afraid", "safe"]:
        return await ask_vbg_type(update, context)
    
    elif query.data == "back_main":
        return await start(update, context)
    
    return URGENCY_CHECK


async def ask_vbg_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Demande le type de VBG"""
    query = update.callback_query
    
    keyboard = []
    for key, parcours in PARCOURS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{parcours['emoji']} {parcours['titre']}", 
                callback_data=f"vbg:{key}"  # CORRIGÉ: utiliser : au lieu de _
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❓ Je ne sais pas / Autre", callback_data="vbg:unknown")])
    keyboard.append([InlineKeyboardButton("◀️ Retour au menu", callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES["vbg_type_question"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return VBG_TYPE


async def handle_vbg_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gère la sélection du type de VBG"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        return await start(update, context)
    
    if query.data == "vbg:unknown":
        return await help_identify_vbg(update, context)
    
    # CORRIGÉ: parsing avec : au lieu de _
    vbg_type = query.data.replace("vbg:", "")
    
    if vbg_type in PARCOURS:
        context.user_data['vbg_type'] = vbg_type
        return await show_parcours(update, context, vbg_type)
    
    return VBG_TYPE


async def show_parcours(update: Update, context: ContextTypes.DEFAULT_TYPE, vbg_type: str) -> int:
    """Affiche le parcours personnalisé"""
    query = update.callback_query
    parcours = PARCOURS[vbg_type]
    
    urgence_tag = "🔴 *URGENT*\n\n" if parcours['urgence'] else ""
    
    message = f"""
{parcours['emoji']} *{parcours['titre']}*

{urgence_tag}📋 *Votre parcours personnalisé*

Voici les étapes recommandées pour vous aider. Chaque étape vous mettra en contact avec un expert adapté à votre situation.

"""
    
    for etape in parcours['etapes']:
        obligatoire = "⚠️ Recommandé" if etape['obligatoire'] else "📌 Optionnel"
        message += f"*{etape['ordre']}. {etape['titre']}*\n"
        message += f"   ⏰ {etape['delai']} | {obligatoire}\n\n"
    
    message += "\n👆 _Cliquez sur une étape pour voir les contacts disponibles._"
    
    keyboard = []
    for etape in parcours['etapes']:
        keyboard.append([
            InlineKeyboardButton(
                f"{etape['ordre']}. {etape['titre']}",
                callback_data=f"step:{vbg_type}:{etape['ordre']}"  # CORRIGÉ: utiliser : comme séparateur
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀️ Retour au menu", callback_data="back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return EXPERT_PARCOURS


async def show_expert_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Affiche les détails d'une étape avec les contacts"""
    query = update.callback_query
    await query.answer()
    
    # CORRIGÉ: parsing avec : comme séparateur
    # Format: step:type:num
    parts = query.data.split(":")
    if len(parts) >= 3:
        vbg_type = parts[1]
        try:
            step_num = int(parts[2])
        except ValueError:
            return EXPERT_PARCOURS
        
        parcours = PARCOURS.get(vbg_type)
        if not parcours:
            return EXPERT_PARCOURS
        
        etape = next((e for e in parcours['etapes'] if e['ordre'] == step_num), None)
        if not etape:
            return EXPERT_PARCOURS
        
        expert_type = etape['expert_type']
        experts = EXPERTS.get(expert_type, [])
        
        message = f"""
{etape['titre']}

📝 *Ce qu'il faut faire :*
{etape['description']}

⏰ *Délai recommandé :* {etape['delai']}

━━━━━━━━━━━━━━━━━━━━━

📞 *Contacts disponibles :*

"""
        
        for expert in experts:
            urgence = "🔴 24h/24" if expert.get('urgence_24h') else ""
            gratuit = "✅ Gratuit" if expert.get('gratuit') else "💰 Payant"
            whatsapp = "📱 WhatsApp" if expert.get('whatsapp') else ""
            
            message += f"""
🏢 *{expert['nom']}*
📍 {expert['ville']}
📞 `{expert['telephone']}`
{gratuit} {urgence} {whatsapp}
_{expert.get('specialite', '')}_

"""
        
        keyboard = [
            [InlineKeyboardButton("✅ J'ai contacté un expert", callback_data=f"done:{vbg_type}:{step_num}")],
            [InlineKeyboardButton(f"◀️ Retour au parcours", callback_data=f"vbg:{vbg_type}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    return EXPERT_PARCOURS


async def mark_step_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Marque une étape comme complétée"""
    query = update.callback_query
    await query.answer("✅ Bravo ! Étape complétée.")
    
    # CORRIGÉ: parsing avec :
    parts = query.data.split(":")
    if len(parts) >= 2:
        vbg_type = parts[1]
        
        message = """
✅ *Étape complétée !*

💜 Vous avez fait un pas important. Chaque étape compte.

Continuez votre parcours ou revenez quand vous êtes prête pour la suite.

_Vous n'êtes pas seule. Nous sommes là pour vous._
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 Continuer le parcours", callback_data=f"vbg:{vbg_type}")],
            [InlineKeyboardButton("🏠 Menu principal", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    return EXPERT_PARCOURS


async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Affiche et gère les contacts de confiance"""
    query = update.callback_query
    
    contacts = context.user_data.get('contacts', [])
    
    message = """
👥 *Vos contacts de confiance*

En cas d'alerte SOS, ces personnes seront automatiquement prévenues avec votre position.

"""
    
    if contacts:
        message += "*Contacts enregistrés :*\n\n"
        for i, contact in enumerate(contacts, 1):
            message += f"{i}. *{contact['name']}*\n   📞 {contact['phone']}\n\n"
        message += f"_({len(contacts)}/3 contacts maximum)_"
    else:
        message += "⚠️ _Aucun contact configuré_\n\n"
        message += "Ajoutez des personnes de confiance qui pourront être alertées en cas d'urgence."
    
    keyboard = []
    if len(contacts) < 3:
        keyboard.append([InlineKeyboardButton("➕ Ajouter un contact", callback_data="add_contact")])
    if contacts:
        keyboard.append([InlineKeyboardButton("🗑️ Supprimer tous les contacts", callback_data="clear_contacts")])
    keyboard.append([InlineKeyboardButton("◀️ Retour au menu", callback_data="back_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return CONTACTS_SETUP


async def add_contact_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Démarre l'ajout d'un contact"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "👤 *Nouveau contact de confiance*\n\n"
        "Quel est le *nom* de cette personne ?\n\n"
        "_Envoyez-moi son prénom ou surnom (ex: Maman, Marie, Paul...)_",
        parse_mode='Markdown'
    )
    return CONTACT_NAME


async def clear_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Supprime tous les contacts"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['contacts'] = []
    
    await query.edit_message_text(
        "🗑️ *Contacts supprimés*\n\n"
        "Tous vos contacts de confiance ont été supprimés.",
        parse_mode='Markdown'
    )
    
    # Retour au menu
    keyboard = [
        [InlineKeyboardButton("👥 Ajouter un contact", callback_data="add_contact")],
        [InlineKeyboardButton("🏠 Menu principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Que souhaitez-vous faire ?",
        reply_markup=reply_markup
    )
    return CONTACTS_SETUP


async def receive_contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Reçoit le nom du contact"""
    name = update.message.text.strip()
    context.user_data['new_contact_name'] = name
    
    await update.message.reply_text(
        f"✅ Nom enregistré : *{name}*\n\n"
        "Maintenant, quel est son *numéro de téléphone* ?\n\n"
        "_Format : +237 6XX XXX XXX ou 6XX XXX XXX_",
        parse_mode='Markdown'
    )
    return CONTACT_PHONE


async def receive_contact_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Reçoit le téléphone et enregistre le contact"""
    phone = update.message.text.strip()
    name = context.user_data.get('new_contact_name', 'Contact')
    
    # Ajouter le contact
    if 'contacts' not in context.user_data:
        context.user_data['contacts'] = []
    
    if len(context.user_data['contacts']) >= 3:
        await update.message.reply_text(
            "❌ Vous avez déjà 3 contacts de confiance (maximum).\n"
            "Supprimez un contact pour en ajouter un nouveau.",
            parse_mode='Markdown'
        )
    else:
        context.user_data['contacts'].append({
            'name': name,
            'phone': phone
        })
        
        count = len(context.user_data['contacts'])
        
        await update.message.reply_text(
            MESSAGES["contact_added"].format(name=name, phone=phone, count=count),
            parse_mode='Markdown'
        )
    
    # Retour au menu des contacts
    keyboard = [
        [InlineKeyboardButton("👥 Voir mes contacts", callback_data="contacts")],
        [InlineKeyboardButton("🏠 Menu principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Que souhaitez-vous faire maintenant ?",
        reply_markup=reply_markup
    )
    return MAIN_MENU


async def send_sos_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Envoie une alerte SOS"""
    query = update.callback_query
    await query.answer()
    
    contacts = context.user_data.get('contacts', [])
    
    if not contacts:
        keyboard = [
            [InlineKeyboardButton("👥 Configurer mes contacts", callback_data="contacts")],
            [InlineKeyboardButton("◀️ Retour", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES["no_contacts"],
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return MAIN_MENU
    
    # Simuler l'envoi d'alerte (en production, envoyer SMS/message)
    logger.info(f"🆘 SOS Alert! Contacts: {contacts}")
    
    keyboard = [
        [InlineKeyboardButton("🏠 Menu principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES["sos_sent"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return MAIN_MENU


async def show_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Affiche les ressources et numéros utiles"""
    query = update.callback_query
    
    message = """
📍 *Ressources et Numéros Utiles*

━━━━━━━━━━━━━━━━━━━━━
🆘 *URGENCES*
━━━━━━━━━━━━━━━━━━━━━
📞 Police : *117*
📞 Gendarmerie : *113*
📞 SAMU : *119*

━━━━━━━━━━━━━━━━━━━━━
🤝 *ONG ET ASSOCIATIONS*
━━━━━━━━━━━━━━━━━━━━━
📱 AlertGBV : +237 242 232 170 _(WhatsApp)_
📞 ALVF : +237 222 20 29 24
📞 RENATA : +237 677 00 00 00
📞 ACAFEJ : +237 222 20 44 88

━━━━━━━━━━━━━━━━━━━━━
⚖️ *AIDE JURIDIQUE*
━━━━━━━━━━━━━━━━━━━━━
📞 Clinique Juridique ACAT : +237 222 20 55 22

━━━━━━━━━━━━━━━━━━━━━
🏥 *HÔPITAUX*
━━━━━━━━━━━━━━━━━━━━━
📞 Hôpital Central Yaoundé : +237 222 23 40 20
📞 Hôpital Laquintinie Douala : +237 233 42 60 91

💜 _N'hésitez pas à appeler. Vous n'êtes pas seule._
"""
    
    keyboard = [
        [InlineKeyboardButton("🏥 Centres médicaux", callback_data="expert_medical")],
        [InlineKeyboardButton("⚖️ Aide juridique", callback_data="expert_avocat")],
        [InlineKeyboardButton("🧠 Psychologues", callback_data="expert_psychologue")],
        [InlineKeyboardButton("🏠 Hébergement", callback_data="expert_hebergement")],
        [InlineKeyboardButton("◀️ Retour au menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return MAIN_MENU


async def show_experts_by_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Affiche les experts par type"""
    query = update.callback_query
    await query.answer()
    
    expert_type = query.data.replace("expert_", "")
    
    type_names = {
        "medical": "🏥 Centres médicaux",
        "avocat": "⚖️ Aide juridique",
        "psychologue": "🧠 Psychologues",
        "hebergement": "🏠 Hébergement d'urgence",
        "police": "👮 Police et Gendarmerie",
        "ong_vbg": "🤝 ONG et Associations",
        "assistant_social": "👥 Services sociaux"
    }
    
    title = type_names.get(expert_type, "Experts")
    experts = EXPERTS.get(expert_type, [])
    
    message = f"*{title}*\n\n"
    
    if experts:
        for expert in experts:
            urgence = "🔴 24h/24" if expert.get('urgence_24h') else ""
            gratuit = "✅ Gratuit" if expert.get('gratuit') else ""
            whatsapp = "📱" if expert.get('whatsapp') else ""
            
            message += f"""
🏢 *{expert['nom']}*
📍 {expert['ville']}
📞 `{expert['telephone']}` {whatsapp}
{gratuit} {urgence}
_{expert.get('specialite', '')}_

"""
    else:
        message += "_Aucun expert disponible dans cette catégorie._"
    
    keyboard = [
        [InlineKeyboardButton("◀️ Retour aux ressources", callback_data="resources")],
        [InlineKeyboardButton("🏠 Menu principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return MAIN_MENU


async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Affiche les informations sur les VBG"""
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("👊 Violence physique", callback_data="info_physique")],
        [InlineKeyboardButton("⚠️ Violence sexuelle", callback_data="info_sexuelle")],
        [InlineKeyboardButton("🧠 Violence psychologique", callback_data="info_psychologique")],
        [InlineKeyboardButton("💰 Violence économique", callback_data="info_economique")],
        [InlineKeyboardButton("💒 Mariage forcé", callback_data="info_mariage")],
        [InlineKeyboardButton("📱 Cyberviolence", callback_data="info_cyber")],
        [InlineKeyboardButton("◀️ Retour au menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES["info_vbg"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return MAIN_MENU


async def show_info_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Affiche les infos détaillées sur un type de VBG"""
    query = update.callback_query
    await query.answer()
    
    vbg_type = query.data.replace("info_", "")
    parcours = PARCOURS.get(vbg_type)
    
    if parcours:
        message = f"""
{parcours['emoji']} *{parcours['titre']}*

{parcours['description']}

━━━━━━━━━━━━━━━━━━━━━

*Exemples :*
"""
        
        exemples = {
            "physique": "• Coups de poing, gifles\n• Brûlures, morsures\n• Étranglement\n• Séquestration\n• Utilisation d'armes",
            "sexuelle": "• Viol (y compris conjugal)\n• Attouchements non consentis\n• Harcèlement sexuel\n• Excision/mutilation\n• Prostitution forcée",
            "psychologique": "• Insultes, humiliations\n• Menaces, chantage\n• Isolement forcé\n• Contrôle excessif\n• Dénigrement constant",
            "economique": "• Privation d'argent\n• Interdiction de travailler\n• Vol de salaire\n• Contrôle des dépenses\n• Sabotage professionnel",
            "mariage": "• Mariage avant 18 ans\n• Mariage sans consentement\n• Lévirat (héritage de veuve)\n• Mariage arrangé forcé",
            "cyber": "• Harcèlement en ligne\n• Revenge porn\n• Doxxing (diffusion d'infos)\n• Surveillance du téléphone\n• Usurpation d'identité"
        }
        
        message += exemples.get(vbg_type, "")
        message += "\n\n💜 *Si vous vivez cela, vous pouvez obtenir de l'aide.*"
        
        keyboard = [
            [InlineKeyboardButton("🆘 Obtenir de l'aide", callback_data=f"vbg:{vbg_type}")],
            [InlineKeyboardButton("◀️ Retour aux infos", callback_data="info")],
            [InlineKeyboardButton("🏠 Menu principal", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    return MAIN_MENU


async def help_identify_vbg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Aide à identifier le type de VBG"""
    query = update.callback_query
    
    message = """
🤔 *Aidez-moi à comprendre votre situation*

Répondez à cette question :

*Est-ce que la personne vous fait subir l'une de ces choses ?*

_(Choisissez ce qui correspond le mieux)_
"""
    
    keyboard = [
        [InlineKeyboardButton("👊 Me frappe ou me blesse", callback_data="vbg:physique")],
        [InlineKeyboardButton("⚠️ Me touche sans mon accord", callback_data="vbg:sexuelle")],
        [InlineKeyboardButton("🧠 M'insulte ou m'humilie", callback_data="vbg:psychologique")],
        [InlineKeyboardButton("💰 Contrôle mon argent", callback_data="vbg:economique")],
        [InlineKeyboardButton("💒 Me force à me marier", callback_data="vbg:mariage")],
        [InlineKeyboardButton("📱 Me harcèle en ligne", callback_data="vbg:cyber")],
        [InlineKeyboardButton("💬 Autre / Je veux en parler", callback_data="resources")],
        [InlineKeyboardButton("◀️ Retour", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    return VBG_TYPE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annule et retourne au menu"""
    await update.message.reply_text(
        "💜 Prenez soin de vous.\n\n"
        "Tapez /start pour recommencer quand vous voulez."
    )
    return ConversationHandler.END


# ============================================================================
# 🚀 LANCEMENT DU BOT
# ============================================================================

def main():
    """Lance le bot"""
    
    # Vérifier le token
    if TOKEN == "METS_TON_TOKEN_ICI" or not TOKEN:
        print("\n" + "="*50)
        print("❌ ERREUR : Token non configuré !")
        print("="*50)
        print("\n📝 Comment obtenir ton token :")
        print("1. Ouvre Telegram")
        print("2. Cherche @BotFather")
        print("3. Envoie /newbot")
        print("4. Suis les instructions")
        print("5. Copie le token fourni")
        print("\n📁 Ensuite, modifie ce fichier :")
        print("   Ligne 24 : TOKEN = 'ton_token_ici'")
        print("\nOu lance avec :")
        print("   TELEGRAM_BOT_TOKEN=ton_token python safeher_bot_prototype.py")
        print("="*50 + "\n")
        return
    
    print("\n" + "="*50)
    print("🛡️  SafeHer Bot - Prototype Hackathon")
    print("="*50)
    print(f"✅ Token configuré")
    print("🚀 Démarrage du bot...")
    print("="*50 + "\n")
    
    # Créer l'application
    application = Application.builder().token(TOKEN).build()
    
    # Gestionnaire de conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(show_experts_by_type, pattern="^expert_"),
                CallbackQueryHandler(show_info_type, pattern="^info_"),
                CallbackQueryHandler(main_menu_handler),
            ],
            URGENCY_CHECK: [
                CallbackQueryHandler(urgency_response),
            ],
            VBG_TYPE: [
                CallbackQueryHandler(handle_vbg_type, pattern="^vbg:"),
                CallbackQueryHandler(main_menu_handler),
            ],
            EXPERT_PARCOURS: [
                CallbackQueryHandler(mark_step_done, pattern="^done:"),
                CallbackQueryHandler(show_expert_step, pattern="^step:"),
                CallbackQueryHandler(handle_vbg_type, pattern="^vbg:"),
                CallbackQueryHandler(main_menu_handler),
            ],
            CONTACTS_SETUP: [
                CallbackQueryHandler(add_contact_start, pattern="^add_contact$"),
                CallbackQueryHandler(clear_contacts, pattern="^clear_contacts$"),
                CallbackQueryHandler(main_menu_handler),
            ],
            CONTACT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_contact_name),
            ],
            CONTACT_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_contact_phone),
            ],
            SOS_CONFIRM: [
                CallbackQueryHandler(send_sos_alert, pattern="^send_sos$"),
                CallbackQueryHandler(main_menu_handler),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
        per_message=False  # AJOUTÉ pour supprimer le warning
    )
    
    application.add_handler(conv_handler)
    
    # Lancer le bot
    print("✅ Bot prêt ! Cherche ton bot sur Telegram et envoie /start")
    print("\n💡 Pour arrêter : Ctrl+C\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()