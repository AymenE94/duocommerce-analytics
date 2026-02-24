# DuoCommerce Analytics - ADW + RFM Segmentation

## 📋 Description du projet
Projet complet d'analyse e-commerce comprenant :
- **ADW (Automated Data Warehouse)** : Modélisation en étoile avec PostgreSQL
- **RFM** : Segmentation clients via Machine Learning (Récence, Fréquence, Montant)

## 🏗️ Architecture du projet
```
duocommerce-analytics/
├── 📁 adw/                    # Scripts du data warehouse
│   └── DW.sql                 # Création des tables et dimensions
│   └── Refresh_DW.py          # Automatisation de l'actualisation des données de la DW
├── 📁 rfm/                     # Analyse RFM
│   └── rfm_analysis.py        # Script principal de segmentation
├── 📄 .env.example             # Template pour les identifiants
├── 📄 .gitignore               # Fichiers ignorés
└── 📄 README.md                 # Vous êtes ici
```

## 🗄️ 1. Automated Data Warehouse (ADW)

### Schéma en étoile
- **Tables de dimensions** : `dim_clients`, `dim_produits`, `dim_dates`, `dim_statut`
- **Table de faits** : `fct_commandes`

### Installation de la BDD
```sql
-- Exécuter dans PostgreSQL
\i adw/DW.sql
```

## 📊 2. Segmentation RFM

### Objectif
Classifier les clients en 4 segments basés sur :
- **R**écence : jours depuis dernier achat
- **F**réquence : nombre de commandes
- **M**ontant : total dépensé

### Installation
```bash
# Cloner le repo
git clone https://github.com/AymenE94/duocommerce-analytics.git
cd duocommerce-analytics

# Installer les dépendances
pip install -r requirements.txt

# Configurer les identifiants
cp .env.example .env
# Éditer .env avec vos identifiants PostgreSQL
```

### Utilisation
```bash
# Lancer l'analyse RFM
python rfm/rfm_analysis.py
```

## 📈 Résultats

### Segments identifiés
| Segment | Récence | Fréquence | Montant | Action |
|---------|---------|-----------|---------|--------|
| 👑 **Champions** | Faible | Élevée | Élevé | Fidélisation |
| 📈 **Fidèles** | Faible | Élevée | Moyen | Upsell |
| 👋 **Nouveaux** | Faible | Faible | Faible | Conversion |
| ⚠️ **À risque** | Élevée | Faible | Faible | Réengagement |

### Fichiers générés
- `data/segmentation_rfm_clients.csv` : Données avec segments
- `rfm/rapport_rfm.txt` : Rapport texte
- Graphiques : distributions et clusters 3D

## ⚙️ Configuration

### Variables d'environnement (`.env`)
```env
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DB_NAME=duocommerce_dw
```

## 📦 Dépendances
```
pandas
numpy
scikit-learn
matplotlib
seaborn
sqlalchemy
psycopg2-binary
python-dotenv
```

## 🚀 Améliorations possibles
- [ ] Automatisation hebdomadaire
- [ ] Dashboard interactif (Power BI/Tableau)
- [ ] Ajout de features (panier moyen, catégorie préférée)
- [ ] Tests A/B sur les actions marketing

## 👤 Auteur
**AymenE94** - [GitHub](https://github.com/AymenE94)

## 📄 Licence
MIT
