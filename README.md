# 🛡️ SafeHer - Protection des Femmes contre les VBG

[![Hackathon VBG 2025](https://img.shields.io/badge/Hackathon-VBG%202025-purple)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

> **Renforcer la sécurité numérique des femmes et des filles** - Développer des outils de protection personnelle et d'alerte en temps réel

## 🎯 Problème Adressé

- **1 femme sur 3** est victime de violence dans sa vie  
- **60% des femmes en ligne** subissent du cyberharcèlement  
- **80% des cas** ne sont jamais signalés  
> _Source : Enquêtes démographique sur la santé 2018_
- Les victimes ne savent souvent pas vers qui se tourner ni dans quel ordre

## 💡 Notre Solution

SafeHer est une plateforme double composée de :

1. **Un site web éducatif** pour sensibiliser et informer sur les VBG
2. **Un bot Telegram intelligent** qui accompagne les victimes avec un parcours personnalisé vers les bons experts

### ✨ Fonctionnalités Clés

| Fonctionnalité | Description |
|----------------|-------------|
| 🔍 **Identification** | Le bot identifie le type de VBG via des questions |
| 🛤️ **Parcours personnalisé** | Chaque type de violence = un parcours d'experts adapté |
| 👨‍⚕️ **Redirection intelligente** | Médecin → Police → Avocat → Psychologue (selon le cas) |
| 🆘 **Alerte SOS** | Alerte discrète aux contacts de confiance |
| 📍 **Géolocalisation** | Partage de position en cas d'urgence |
| 🔒 **Confidentialité** | Aucune donnée personnelle stockée |

## 🏗️ Architecture

```
safeher/
│
├── web/                 # Site web éducatif
│   └── index.html          # Page principale (HTML/CSS/JS)
│
├── bot/  # Bot Telegram
│   |                   
│   ├── prototype.py      # Code principal du bot
│   ├── start.sh          # fichier de lancement du bot
│   ├── .env              # variable environement 
│
├── nginx/  
│   |                  
│   ├── Dockerfile      # fichier de configuration docker
│   ├── nginx.conf          # fichier configuration web
│ 
├── docker-compose.yml    # Fichier de configuration docker compose
├── Dockerfile          # Fichier de configuration docker
├── requirements.txt    # Dépendances Python
│
└── README.md               # Ce fichier
```

## 🚀 Installation & Déploiement (Docker)

### Prérequis

- Un VPS avec Docker installé
- Un compte Telegram
- Un token de bot Telegram (via [@BotFather](https://t.me/botfather))

### 1. Créer le Bot Telegram

1. Ouvrez Telegram et cherchez `@BotFather`
2. Envoyez `/newbot`
3. Suivez les instructions (nom: `SafeHer Bot`, username: `SafeHerBot`)
4. **Copiez le token fourni** (vous en aurez besoin)

### 2. Déployer avec Docker (Recommandé)

```bash
# Se connecter au VPS
ssh user@votre-vps

# Créer le dossier du projet
mkdir -p /opt/safeher && cd /opt/safeher

# Transférer les fichiers (depuis votre machine locale)
# scp -r SafeHer/* user@votre-vps:/opt/safeher/

# Configurer les variables d'environnement
cp .env.example .env
nano .env  # Ajouter votre TELEGRAM_BOT_TOKEN

# Rendre le script exécutable
chmod +x deploy.sh

# Installation et démarrage
./deploy.sh install
./deploy.sh start
```

### 3. Commandes utiles

```bash
# Démarrer SafeHer
./deploy.sh start

# Arrêter SafeHer
./deploy.sh stop

# Redémarrer
./deploy.sh restart

# Voir les logs
./deploy.sh logs

# Logs du bot uniquement
./deploy.sh logs-bot

# Status des services
./deploy.sh status

# Mise à jour
./deploy.sh update
```

### 4. Structure Docker

```
SafeHer/
├── docker-compose.yml      # Orchestration des services
├── deploy.sh               # Script de déploiement
├── .env.example            # Variables d'environnement
├── .dockerignore           # Fichiers à ignorer
├── website/
│   ├── Dockerfile          # Image Nginx
│   ├── nginx.conf          # Config Nginx
│   └── index.html          # Site web
└── bot/
    ├── Dockerfile          # Image Python
    ├── requirements.txt    # Dépendances
    └── safeher_bot.py      # Code du bot
```

### 5. Ports utilisés

| Service | Port | Description |
|---------|------|-------------|
| Website | 80 | Site web (Nginx) |
| Bot | - | Pas de port exposé (polling Telegram) |

### 6. Avec un nom de domaine (optionnel)

Si vous avez un domaine, éditez `.env` :

```env
DOMAIN=safeher.votredomaine.com
```

Pour HTTPS, ajoutez un reverse proxy comme Traefik ou Nginx Proxy Manager.

## 📋 Parcours Utilisateur

```
┌─────────────────────────────────────────┐
│         Utilisatrice arrive             │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│     Vérification urgence                │
│  "Êtes-vous en sécurité ?"              │
└─────────────────┬───────────────────────┘
                  ▼
        ┌─────────┴─────────┐
        ▼                   ▼
   En danger           En sécurité
        │                   │
        ▼                   ▼
   Alerte SOS         Identification
   + Numéros          du type de VBG
   urgence                  │
                            ▼
                    ┌────────────────┐
                    │ Parcours       │
                    │ personnalisé   │
                    │ d'experts      │
                    └────────────────┘
```

## 🗂️ Types de VBG et Parcours

| Type | Parcours |
|------|----------|
| Violence physique | Médecin → Police → Avocat → Psychologue → Hébergement |
| Violence sexuelle | Médecin (72h!) → Police → Psychologue → Avocat |
| Violence psychologique | Psychologue → ONG → Assistant social → Avocat |
| Violence économique | Assistant social → Avocat → ONG → Psychologue |
| Mariage forcé | ONG → Assistant social → Avocat → Hébergement |
| Cyberviolence | ONG (preuves) → Police → Psychologue → Avocat |

## 🌍 Adaptation au Contexte Africain

- ✅ Fonctionne avec peu de données (Telegram est léger)
- ✅ Pas besoin de télécharger une nouvelle app
- ✅ Interface simple avec boutons (pas de texte à taper)
- ✅ Multilingue (français, bientôt langues locales)
- ✅ Contacts locaux par pays/ville
- ✅ Mode discret (le bot peut avoir un nom anodin)

## 🔐 Sécurité & Confidentialité

- Aucune donnée personnelle stockée de façon permanente
- Conversations chiffrées par Telegram
- Pas d'enregistrement audio (légalité)
- La victime contrôle tout (opt-in)
- Alertes SOS envoyées uniquement sur demande

## 📊 Avantages Concurrentiels

| Critère | AlertGBV | App-Elles | SafeHer |
|---------|----------|-----------|---------|
| Bot Telegram | ❌ | ❌ | ✅ |
| Parcours personnalisé | ❌ | ❌ | ✅ |
| Fonctionne hors-ligne | ❌ | ❌ | Partiellement |
| Multi-experts | Partiel | ❌ | ✅ |
| Gratuit | ✅ | ✅ | ✅ |
| Open source | ❌ | ❌ | ✅ |

## 🛣️ Roadmap

### Phase 1 (Hackathon) ✅
- [x] Site web éducatif
- [x] Bot Telegram avec parcours
- [x] Base de données experts Cameroun

### Phase 2 (Post-hackathon)
- [ ] Ajout d'autres pays africains
- [ ] Intégration SMS pour zones sans internet
- [ ] Langues locales (Ewondo, Fulfulde, etc.)
- [ ] Partenariats avec ONG

### Phase 3 (Scale)
- [ ] Application mobile PWA
- [ ] Tableau de bord pour ONG partenaires
- [ ] Statistiques anonymisées pour recherche
- [ ] Formation des agents communautaires

## 👥 Équipe

- **[Votre nom]** - Développeur / Chef d'équipe
- **SOKOUDJOU CHENDJOU Christian Manuel** - [Rôle]
- **STEPHANE ROYLEX NKOLO KOUMNDA** - Développeur
- **[Coéquipier 3]** - [Rôle]

## 🤝 Partenaires Potentiels

- AlertGBV Cameroun
- ONU Femmes
- ALVF (Association de Lutte contre les Violences faites aux Femmes)
- Ministère de la Promotion de la Femme et de la Famille

## 📜 Licence

Ce projet est sous licence MIT. Libre d'utilisation et de modification.

## 📞 Contact

- **Site web** : [URL du site déployé]
- **Bot Telegram** : [@SafeHerBot](https://t.me/SafeHerBot)
- **Email** : [votre email]

---

💜 **Projet réalisé dans le cadre du Hackathon VBG 2025**

*Ensemble, brisons le silence sur les violences faites aux femmes.*