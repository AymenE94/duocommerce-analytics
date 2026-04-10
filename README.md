# DuoCommerce Analytics - ADW + RFM + DQA

## 📋 Description du projet
Projet complet d'analyse e-commerce comprenant :
- **ADW (Automated Data Warehouse)** : Modélisation en étoile avec PostgreSQL
- **RFM** : Segmentation clients via Machine Learning (Récence, Fréquence, Montant)
- **DQA (Data Quality Auditor)** : Audit automatisé de la qualité des données avec Pydantic

## 🏗️ Architecture du projet
```
duocommerce-analytics/
├── 📁 adw/                         # Scripts du data warehouse
│   ├── DW.sql                      # Création des tables et dimensions
│   └── refresh_DW.py               # Automatisation du rafraîchissement
├── 📁 rfm/                         # Analyse RFM
│   └── rfm_analysis.py             # Script principal de segmentation
├── 📁 dqa/                         # Data Quality Auditor
│   ├── config.py                   # Configuration connexion PostgreSQL
│   ├── models.py                   # Modèles Pydantic (contrats de données)
│   ├── auditor.py                  # Moteur d'audit générique
│   └── run_audit.py                # Script d'exécution
├── 📄 .env.example                 # Template pour les identifiants
├── 📄 .gitignore                   # Fichiers ignorés
├── 📄 requirements.txt             # Dépendances Python
└── 📄 README.md                    # Vous êtes ici
```

## 🗄️ 1. Automated Data Warehouse (ADW)

### Schéma en étoile
- **Tables de dimensions** : `dim_clients`, `dim_produits`, `dim_dates`, `dim_statut`
- **Table de faits** : `fct_commandes`

### Installation de la BDD
```sql
\i adw/DW.sql
```

### Rafraîchissement automatique
```bash
python adw/refresh_DW.py
```

## 📊 2. Segmentation RFM

### Objectif
Classifier les clients en 4 segments basés sur :
- **R**écence : jours depuis dernier achat
- **F**réquence : nombre de commandes
- **M**ontant : total dépensé

### Utilisation
```bash
python rfm/rfm_analysis.py
```

### Segments identifiés
| Segment | Récence | Fréquence | Montant | Action |
|---------|---------|-----------|---------|--------|
| 👑 **Champions** | Faible | Élevée | Élevé | Fidélisation |
| 📈 **Fidèles** | Faible | Élevée | Moyen | Upsell |
| 👋 **Nouveaux/Récents** | Faible | Faible | Faible | Conversion |
| ⚠️ **À risque** | Élevée | Faible | Faible | Réengagement |

### Fichiers générés
- `segmentation_rfm_clients.csv` : Données avec segments
- `rapport_rfm.txt` : Rapport texte
- Table PostgreSQL `rfm_segments` : Données persistées
- Graphiques : distributions et clusters 3D

## 🔍 3. Data Quality Auditor (DQA)

### Objectif
Valider automatiquement la qualité des données avec des règles métier :
- Types de données (int, float, email)
- Valeurs minimales/maximales
- Présence des champs obligatoires
- Formats spécifiques (email, date)

### Modèles de validation
| Modèle | Table auditée | Règles |
|--------|---------------|--------|
| `RFMRecord` | `rfm_segments` | ID > 0, scores 0-3, montant ≥ 0 |
| `DimClientsRecord` | `dim_clients` | Email valide, date inscription |
| `DimProduitsRecord` | `dim_produits` | Prix > 0, coût ≥ 0 |
| `FctCommandesRecord` | `fct_commandes` | IDs > 0, montant ≥ 0 |

### Utilisation
```bash
python dqa/run_audit.py
```

### Sortie attendue
```
✅ 5 / 5 lignes valides
📊 rfm_segments: Aucune erreur détectée
```

## ⚙️ Installation complète

```bash
git clone https://github.com/AymenE94/duocommerce-analytics.git
cd duocommerce-analytics
pip install -r requirements.txt
cp .env.example .env
```

## ⚙️ Configuration

### Variables d'environnement (`.env`)
```
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
pydantic
pydantic-settings
email-validator
```

## 🚀 Workflow Complet

```bash
# 1. Rafraîchir le Data Warehouse
python adw/refresh_DW.py

# 2. Lancer la segmentation RFM
python rfm/rfm_analysis.py

# 3. Auditer la qualité des données
python dqa/run_audit.py
```

## 🚀 Améliorations possibles
- [x] Data Quality Auditor avec Pydantic
- [ ] Automatisation hebdomadaire complète (cron/Airflow)
- [ ] Dashboard interactif (Power BI/Tableau)
- [ ] Ajout de features (panier moyen, catégorie préférée)
- [ ] Tests A/B sur les actions marketing
- [ ] Détection d'anomalies statistiques (Z-score, IQR)
- [ ] Alerting email en cas d'erreur de qualité

## 👤 Auteur
**AymenE94** - [GitHub](https://github.com/AymenE94)

## 📄 Licence
MIT
