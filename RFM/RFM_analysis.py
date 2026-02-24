import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore') 

from sqlalchemy import create_engine 

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

engine = create_engine(
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
                       connect_args={'connect_timeout' : 10}                      
)

try:
    with engine.connect() as conn:
        print("✅ Connexion réussie à PostgreSQL")
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")

query = """
WITH commandes_valides AS (
    SELECT
        id_client,
        date_complete,
        montant_total
    FROM fct_commandes f
    JOIN dim_dates d on f.id_date = d.id_date
    WHERE id_statut = 1
),
rfm_calc AS(
    SELECT
        c.id_client,
        c.nom,
        c.ville,
        c.categorie as categorie_client,
        c.anciennete_mois,
                COALESCE(
            (CURRENT_DATE - MAX(cv.date_complete)),
            999
        ) AS recence,
COUNT(cv.id_client) as frequence,
COALESCE(SUM(cv.montant_total), 0) as montant
FROM dim_clients c 
LEFT JOIN commandes_valides cv ON c.id_client = cv.id_client
GROUP BY c.id_client, c.nom, c.ville, c.categorie, c.anciennete_mois
)
SELECT * FROM  rfm_calc
ORDER BY montant DESC;
"""


df = pd.read_sql(query, engine)
print(f"✅ {len(df)} clients récupérés")
print("\n📋 Aperçu des données :")
print(df.head())

print("\n📊 Statistiques descriptives :")
print(df[['recence', 'frequence', 'montant']].describe())


fig, axes = plt.subplots(1, 3, figsize=(15, 4))


axes[0].hist(df['recence'], bins=20, color='skyblue', edgecolor='black')
axes[0].set_title('Distribution de la Récence')
axes[0].set_xlabel('Jour depuis le dernier achat')

axes[1].hist(df['frequence'], bins=20, color='lightgreen', edgecolor='black')
axes[1].set_title('Distribution de la frequence')
axes[1].set_xlabel('Nombre de commandes')

axes[2].hist(df['montant'], bins=20, color='salmon', edgecolor='black')
axes[2].set_title('Distribution du Montant')
axes[2].set_xlabel('Montant total (€)')

plt.tight_layout()
plt.show()

print("\n🔍 Valeurs manquantes :")
print(df.isnull().sum())
rfm_cols = ['recence', 'frequence', 'montant']
X = df[rfm_cols].copy()

X = X.replace([np.inf, -np.inf], np.nan)
X = X.fillna(0)

scaler = StandardScaler ()#pour standardiser les différentes échelles de valeur
X_scaled = scaler.fit_transform(X)

inertias = []
silhouette_scores = []
K_range = range(2, 9)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.plot(K_range, inertias, 'bo-')
ax1.set_xlabel('Nombre de clusters (k)')
ax1.set_ylabel('Inertie')
ax1.set_title('Méthode du coude')
ax1.grid(True)

ax2.plot(K_range, silhouette_scores, 'ro-')
ax2.set_xlabel('Nombre de clusters (k)')
ax2.set_ylabel('Score de silhouette')
ax2.set_title('Score de silhouette')
ax2.grid(True)

plt.tight_layout()
plt.show()

best_k = K_range[np.argmax(silhouette_scores)]
print(f"✅ Meilleur nombre de clusters selon silhouette : {best_k}")

k= 4 # c'est pour avoir 4 clusters donc 4 groupes
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)


cluster_order = df.groupby('cluster')['montant'].mean().sort_values(ascending=False).index
cluster_mappping = {old: new for new, old in enumerate(cluster_order)}
df['segment'] = df['cluster'].map(cluster_mappping)

segment_names = {
    0: "👑 Champions",
    1: "📈 Fidèles", 
    2: "👋 Nouveaux/Récents",
    3: "⚠️ À risque"
}
df['segment_nom'] = df['segment'].map(segment_names)

segment_analysis = df.groupby('segment').agg({
    'recence':['mean', 'std'],
    'frequence':['mean', 'std'],
    'montant':['mean', 'std'],
    'id_client': 'count'
}).round(2)

segment_analysis.columns = ['recence_moy', 'recence_std', 'frequence_moy', 
                            'frequence_std', 'montant_moy', 'montant_std', 'nb_clients']
segment_analysis['pourcentage'] = (segment_analysis['nb_clients'] / len(df) * 100).round(1)

from mpl_toolkits.mplot3d import Axes3D 

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
colors = ['gold', 'skyblue', 'lightgreen', 'salmon']
for segment in sorted(df['segment'].unique()):
    segment_data = df[df['segment'] == segment]
    ax.scatter(segment_data['recence'],
                segment_data['frequence'],
                 segment_data['montant'],
                  c=colors[segment % len(colors)],
                   label=segment_names[segment],
                    s=50, alpha=0.6 )
    
ax.set_xlabel('Récence (jours)')
ax.set_ylabel('Fréquence')
ax.set_zlabel('Montant (€)')
ax.set_title('Segments RFM - Vue 3D')
ax.legend()
plt.show()

df.to_csv('segmentation_rfm_clients.csv', index=False, encoding='utf-8')
df_to_save = df[['id_client', 'nom', 'segment', 'segment_nom', 'recence', 'frequence', 'montant']].copy()
df_to_save.to_sql('rfm_segments', engine, if_exists='replace', index=False)

summary = f"""
    📊 RAPPORT SEGMENTATION RFM
    ===========================
    Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}
Total clients analysés: {len(df)}
RÉPARTITION DES SEGMENTS:
"""

for segment in sorted(df['segment'].unique()):
    count = len(df[df['segment'] == segment])
    pct = count/len(df)*100
    montant_moy = df[df['segment'] == segment]['montant'].mean()
    summary += f"\n{segment_names[segment]}: {count} clients ({pct:.1f}%) - {montant_moy:.2f}€ en moyenne"

with open ('rapport_rfm.txt', 'w', encoding='utf-8') as f:
    f.write(summary)
