# ============================================
# AUTOMATISATION DATA WAREHOUSE DUOCOMMERCE
# Script Python pour rafraîchir le DW
# ============================================

# 1. IMPORTATIONS


import psycopg2 
from psycopg2 import sql
import logging
from datetime import datetime
from config import DB_CONFIG, LOG_FILE


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



def connect_to_db() :
    try:
        logger.info("Connexion à PostgreSQL")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        logger.info("✅ Connexion réussie")
        return conn, cursor
    except Exception as e:
            logger.error(f"❌ Erreur connexion : {e}")
            return None, None 


def refresh_dim_clients(conn, cursor):
     try:
        logger.info("Rafraîchissement dim_clients...")
        query =  """
        INSERT INTO dim_clients (
            client_id_original, nom, email, ville, date_inscription,
            categorie, anciennete_mois, segment, email_present, region_commercial
        )
        SELECT 
            c.client_id,
            c.nom,
            c.email,
            c.ville,
            c.date_inscription,
            c.categorie,
            DATE_PART('month', AGE(CURRENT_DATE, c.date_inscription)),
            CASE
                WHEN DATE_PART('month', AGE(CURRENT_DATE, c.date_inscription)) < 3 THEN 'Nouveau'
                WHEN DATE_PART('month', AGE(CURRENT_DATE, c.date_inscription)) > 12 THEN 'Fidèle'
                ELSE 'Régulier'
            END,
            c.email IS NOT NULL,
            CASE
                WHEN c.ville = 'Paris' THEN 'île-de-france'
                ELSE 'autre_regions'
            END
        FROM clients c
        WHERE NOT EXISTS (
            SELECT 1 FROM dim_clients dc 
            WHERE dc.client_id_original = c.client_id
        )
        """
        cursor.execute(query)
        count = cursor.rowcount
        logger.info(f"✅ dim_clients : {count} nouveaux clients")
        return count
     except Exception as e:
        logger.error(f"Erreur dim_clients : {e}")
        raise 
     


def refresh_dim_produits(conn, cursor):
     try:
          logger.info("Rafraîchissement dim_produits...")

          query=  """
        INSERT INTO dim_produits (
            produit_id_original, nom, categorie, prix, cout_production,
            est_actif, gamme_prix, taux_marge, marge_brut_unit,
            est_produit_phare, date_ajout
        )
        SELECT 
            p.produit_id,
            p.nom,
            p.categorie,
            p.prix,
            p.cout_production,
            p.est_actif,
            CASE 
                WHEN p.prix >= 200 THEN 'haut de gamme'
                WHEN p.prix <= 50 THEN 'entrée de gamme'
                ELSE 'milieu de gamme'
            END,
            CASE 
                WHEN p.prix > 0 THEN (((p.prix - p.cout_production)/p.prix)*100.0) 
                ELSE 0
            END,
            (p.prix - p.cout_production),
            FALSE,
            CURRENT_DATE
        FROM produits p
        WHERE NOT EXISTS (
            SELECT 1 FROM dim_produits dp 
            WHERE dp.produit_id_original = p.produit_id
        )
        """
          cursor.execute(query)
          count = cursor.rowcount
          logger.info(f"✅ dim_produits : {count} nouveaux produits")
          return count
     except Exception as e:
          logger.error(f"Erreur dim_produits : {e}")
          raise
     
def main():
     logger.info("=== DÉBUT RAFRAÎCHISSEMENT DW ===")
     conn, cursor = connect_to_db()
     if not conn :
          return False
     
     try:
          dates_count = create_dim_dates(conn, cursor)
          statut_created = create_dim_statut(conn, cursor)
          
          clients_count = refresh_dim_clients(conn, cursor)
          produits_count = refresh_dim_produits(conn, cursor)
          commandes_count = refresh_fct_commandes(conn, cursor)
          conn.commit()

          logger.info(f"=== RÉSUMÉ ===")
          logger.info(f"- Dates: {dates_count}")
          logger.info(f"- Statuts: créés/rafraîchis")
          logger.info(f"- Clients: {clients_count}")
          logger.info(f"- Produits: {produits_count}")
          logger.info(f"- Commandes: {commandes_count}")
          logger.info("✅ RAFRAÎCHISSEMENT RÉUSSI")

          return True
     except Exception as e:
          logger.error(f"❌ ERREUR: {e}")
          conn.rollback()
          return False
     finally:
          cursor.close()
          conn.close()
          logger.info("Connexion PostgreSQL fermée")


def refresh_fct_commandes(conn, cursor):
    try:
        logger.info("Rafraîchissement fct_commandes...")
        query = """
            INSERT INTO fct_commandes (
            id_date,
            id_client, 
            id_produit,
            id_statut,
            quantite,
            prix_unitaire,
            reduction,
            montant_total,
            marge
        )
        SELECT 
            (TO_CHAR(cmd.date_commande, 'YYYYMMDD')::INTEGER) AS id_date,
            cli_dim.id_client AS id_client,
            prod_dim.id_produit AS id_produit,
            CASE cmd.statut
                WHEN 'Confirmée' THEN 1
                WHEN 'Annulée' THEN 2
                WHEN 'En attente' THEN 3
                ELSE NULL
            END AS id_statut,
            cmd.quantite,
            COALESCE(prod_source.prix, 0) AS prix_unitaire,
            cmd.reduction,
            COALESCE(cmd.quantite, 0) * COALESCE(prod_source.prix, 0) * 
            (1 - COALESCE(cmd.reduction, 0)/100.0) AS montant_total,
            (COALESCE(cmd.quantite, 0) * COALESCE(prod_source.prix, 0) * 
             (1 - COALESCE(cmd.reduction, 0)/100.0)) - 
            (COALESCE(cmd.quantite, 0) * COALESCE(prod_source.cout_production, 0)) AS marge
        FROM commandes AS cmd
        LEFT JOIN dim_clients AS cli_dim ON cmd.client_id = cli_dim.client_id_original
        LEFT JOIN dim_produits AS prod_dim ON cmd.produit_id = prod_dim.produit_id_original
        LEFT JOIN produits AS prod_source ON cmd.produit_id = prod_source.produit_id
        WHERE NOT EXISTS (
            SELECT 1 FROM fct_commandes fc 
            WHERE fc.id_date = (TO_CHAR(cmd.date_commande, 'YYYYMMDD')::INTEGER)
              AND fc.id_client = cli_dim.id_client
              AND fc.id_produit = prod_dim.id_produit
              AND COALESCE(fc.quantite, 0) = COALESCE(cmd.quantite, 0)
        )
        """
        cursor.execute(query)
        count = cursor.rowcount
        logger.info(f"✅ fct_commandes : {count} nouvelles commandes")
        return count
    except Exception as e:
        logger.error(f"Erreur fct_commandes : {e}")
    raise

def create_dim_dates(conn, cursor):
    try:
          logger.info("Rafraichissement dim_dates...")
          query= """
            INSERT INTO dim_dates
	        SELECT
	        (EXTRACT(YEAR FROM date) * 10000 + EXTRACT(MONTH FROM date) * 100 + EXTRACT(DAY FROM date)):: INTEGER AS id_date,
	        date AS date_complete,
	        EXTRACT(YEAR FROM date)::INTEGER AS annee,
	        EXTRACT(QUARTER FROM date)::INTEGER AS trimestre,
            EXTRACT(MONTH FROM date)::INTEGER AS mois,
                
                TO_CHAR(date, 'TMMon') AS nom_mois,
                EXTRACT(DAY FROM date)::INTEGER AS jour_mois,
                EXTRACT(ISODOW FROM date)::INTEGER AS jour_semaine,
                
                TO_CHAR(date, 'TMDay') AS nom_jour,
               
                EXTRACT(ISODOW FROM date) > 5 AS est_weekend,
                false AS est_jour_ferie,
                EXTRACT(WEEK FROM date)::INTEGER AS numero_semaine_iso
        FROM GENERATE_SERIES(
            '2023-01-01'::DATE,
            '2025-12-31'::DATE,
            '1 day'::INTERVAL
        ) AS date   
            WHERE NOT EXISTS (
            SELECT 1 FROM dim_dates dd 
            WHERE dd.id_date = (EXTRACT(YEAR FROM date) * 10000 + EXTRACT(MONTH FROM date) * 100 + EXTRACT(DAY FROM date))::INTEGER
            )
        """
          cursor.execute(query)
          count = cursor.rowcount
          logger.info(f"✅ dim_dates : {count} dates créees (2023-2025)")
          return count
    except Exception as e:
        logger.error(f"Erreur dim_dates: {e}")
        raise 

def create_dim_statut(conn, cursor):
     try:
          logger.info("Rafraichissement dim_statut")
          create_table_query= """
          CREATE TABLE IF NOT EXISTS dim_statut (
            id_statut SERIAL PRIMARY KEY,
            code_statut VARCHAR(20),
            libelle_statut VARCHAR(50)
        );
        """
          cursor.execute(create_table_query)

          insert_query = """
          INSERT INTO dim_statut (id_statut, code_statut, libelle_statut)
        VALUES 
            (1, 'CONFIRMEE', 'Confirmée'),
            (2, 'ANNULEE', 'Annulée'),
            (3, 'EN_ATTENTE', 'En attente')
        ON CONFLICT (id_statut) DO NOTHING;
        """
          cursor.execute(insert_query)

          logger.info("✅ dim_statut : table créée/rafraîchie avec les statuts par défaut")
          return True
     except Exception as e :
          logger.error(f"Erreur dim_statut: {e}")
          raise
     
if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Processus terminé avec succès")
    else:
        logger.error("Processus terminé avec des erreurs")