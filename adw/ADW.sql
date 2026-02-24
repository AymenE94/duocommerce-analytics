-- SQLBook: Code
DROP TABLE IF EXISTS commandes;
DROP TABLE IF EXISTS produits;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS fct_commandes;
DROP TABLE IF EXISTS dim_clients;
DROP TABLE IF EXISTS dim_produits;
DROP TABLE IF EXISTS dim_statut;
DROP TABLE IF EXISTS dim_dates;

CREATE TABLE produits (
    produit_id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    categorie VARCHAR(50),
    prix DECIMAL(10,2) NOT NULL,
    cout_production DECIMAL(10,2),
    est_actif BOOLEAN DEFAULT TRUE 
);


 --données produits 
INSERT INTO produits VALUES
(101, 'iPhone 15', 'Électronique', 999.99, 450.00, true),
(102, 'MacBook Pro', 'Électronique', 1999.99, 850.00, true),
(103, 'T-shirt Col V', 'Vêtement', 29.99, 8.50, true),
(104, 'Jeans Slim', 'Vêtement', 79.99, 22.00, true),
(105, 'Cafetière Deluxe', 'Électroménager', 149.99, 45.00, false),
(106, 'Échantillon Parfum', 'Beauté', 0.00, 2.50, true),
(107, 'Livre SQL Avancé', 'Livre', 39.99, 12.00, true);

-- tables dimension produits
CREATE TABLE dim_produits (
  id_produit SERIAL PRIMARY KEY,
    produit_id_original INTEGER NOT NULL,
    nom VARCHAR(100) NOT NULL,
    categorie VARCHAR(50),
    prix DECIMAL(10,2) NOT NULL,
    cout_production DECIMAL(10,2),
    est_actif BOOLEAN DEFAULT true,
    est_produit_phare BOOLEAN DEFAULT false,
    date_ajout DATE DEFAULT CURRENT_DATE,

    gamme_prix VARCHAR(20),
    taux_marge DECIMAL(5,2),
    marge_brut_unit DECIMAL (10,2)
);

INSERT INTO dim_produits(
    produit_id_original,
    nom,
    categorie,
    prix,
    cout_production,
    est_actif,
    gamme_prix,
    taux_marge,
    marge_brut_unit ,
    est_produit_phare, 
    date_ajout
)

SELECT 
	produit_id,
	nom,
	categorie,
	prix,
	cout_production,
	est_actif,
	CASE 
		WHEN prix >= 200 THEN 'haut de gamme'
		WHEN prix <= 50 THEN 'entrée de gamme'
			ELSE 'milieu de gamme'
	END as gamme_prix,

	CASE 
 		WHEN prix > 0 THEN (((prix - cout_production)/prix)*100.0) 
 			ELSE 0
	END as taux_marge,

	(prix - cout_production) AS marge_brut_unit,


	FALSE AS est_produit_phare,
	NULL AS date_ajout

FROM produits;


CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    ville VARCHAR(50),
    date_inscription DATE,
    categorie VARCHAR(20)  -- 'Premium', 'Standard', 'Basique'
);

-- Données
INSERT INTO clients VALUES
(1, 'Martin Dupont', 'martin@email.com', 'Paris', '2023-01-15', 'Premium'),
(2, 'Sophie Bernard', 'sophie@email.com', 'Lyon', '2023-03-22', 'Standard'),
(3, 'Thomas Leroy', 'thomas@email.com', 'Marseille', '2023-05-10', 'Basique'),
(4, 'Julie Petit', NULL, 'Paris', '2023-07-30', 'Standard'),
(5, 'Kevin Martin', 'kevin@email.com', NULL, '2023-09-05', NULL);


--tables dimension clients
CREATE TABLE dim_clients (
	id_client SERIAL PRIMARY KEY,
	client_id_original INTEGER,
    nom VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    ville VARCHAR(50),
    date_inscription DATE,
    categorie VARCHAR(20),
    anciennete_mois INTEGER,
    segment VARCHAR(20),
    email_present BOOLEAN,
    region_commercial VARCHAR(30)
);

INSERT INTO dim_clients(

	client_id_original,
	nom,
	email,
	ville,
	date_inscription,
	categorie,
	anciennete_mois,
	segment,
	email_present,
	region_commercial
)

SELECT
	client_id,
	nom,
	email,
	ville,
	date_inscription,
	categorie,
	DATE_PART('month', AGE(CURRENT_DATE, date_inscription)) as anciennete_mois,
	CASE
		WHEN DATE_PART('month', AGE(CURRENT_DATE, date_inscription)) <3 THEN 'Nouveau'
		WHEN DATE_PART('month', AGE(CURRENT_DATE, date_inscription)) >12 THEN 'Fidèle'
		ELSE 'Régulier'
	END as segment,
	email IS NOT NULL as email_present,
	CASE
		WHEN ville = 'Paris' THEN 'île-de-france'
			ELSE 'autre_regions'
	END as region_commercial
FROM clients;



CREATE TABLE commandes (
    commande_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(client_id),
    produit_id INTEGER REFERENCES produits(produit_id),
    quantite INTEGER,
    date_commande DATE,
    statut VARCHAR(20) DEFAULT 'Confirmée',  -- 'Confirmée', 'Annulée', 'En attente'
    reduction DECIMAL(5,2) DEFAULT 0
);

--Données
INSERT INTO commandes VALUES
(1001, 1, 101, 1, '2024-01-10', 'Confirmée', 0),
(1002, 1, 103, 3, '2024-01-10', 'Confirmée', 10),
(1003, 2, 102, 1, '2024-01-12', 'Annulée', 0),
(1004, 2, 104, 2, '2024-01-15', 'Confirmée', 15),
(1005, 3, 103, 5, '2024-01-18', 'Confirmée', 0),
(1006, 3, 105, 1, '2024-01-20', 'En attente', 20),
(1007, 4, 106, 10, '2024-01-22', 'Confirmée', 0),
(1008, 4, 107, 2, '2024-01-25', 'Confirmée', 5),
(1009, 5, 101, 2, '2024-01-28', 'Confirmée', 0),
(1010, NULL, 103, 1, '2024-01-30', 'Confirmée', 0),  -- Client inconnu !
(1011, 1, 102, NULL, '2024-02-01', 'Confirmée', 0),  -- Quantité NULL !
(1012, 2, NULL, 1, '2024-02-02', 'Confirmée', 0);    -- Produit NULL !






CREATE TABLE dim_dates (
	id_date INTEGER PRIMARY KEY,
	date_complete DATE,
	annee INTEGER,
	trimestre INTEGER,
	mois INTEGER,
	nom_mois VARCHAR(20),
	jour_mois INTEGER,
	jour_semaine INTEGER,
	nom_jour VARCHAR(20),
	est_jour_ferie BOOLEAN DEFAULT FALSE,
	est_weekend BOOLEAN DEFAULT FALSE,
	numero_semaine_iso INTEGER
);

INSERT INTO dim_dates
	SELECT
	   (EXTRACT(YEAR FROM d) * 10000 + EXTRACT(MONTH FROM d) * 100 + EXTRACT(DAY FROM d))::INTEGER AS id_date,
    d AS date_complete,
    EXTRACT(YEAR FROM d)::INTEGER AS annee,
    EXTRACT(QUARTER FROM d)::INTEGER AS trimestre,
    EXTRACT(MONTH FROM d)::INTEGER AS mois,
    TO_CHAR(d, 'TMMon') AS nom_mois,
    EXTRACT(DAY FROM d)::INTEGER AS jour_mois,
    EXTRACT(ISODOW FROM d)::INTEGER AS jour_semaine,
    TO_CHAR(d, 'TMDay') AS nom_jour,
    EXTRACT(ISODOW FROM d) > 5 AS est_weekend,
    false AS est_jour_ferie,
    EXTRACT(WEEK FROM d)::INTEGER AS numero_semaine_iso
FROM GENERATE_SERIES(
    '2023-01-01'::DATE,
    '2025-12-31'::DATE,
    '1 day'::INTERVAL
) AS d;

CREATE TABLE dim_statut (
	id_statut SERIAL PRIMARY KEY,
	code_statut VARCHAR (20),
	libelle_statut VARCHAR (50)
);

INSERT INTO dim_statut VALUES 

	(1, 'Confirmée', 'Commande confirmée'),
	(2, 'Annulée', 'Commande annulée'),
	(3, 'En attente', 'Commande en attente');

CREATE TABLE fct_commandes (
    id_fait SERIAL PRIMARY KEY,
    id_date INTEGER,
    id_client INTEGER,
    id_produit INTEGER,
    id_statut INTEGER,
    quantite INTEGER,
    prix_unitaire DECIMAL(10,2),      -- ← Prix unitaire du produit
    reduction DECIMAL(5,2),           -- ← Pourcentage de réduction
    montant_total DECIMAL(10,2),      -- ← SI, ELLE EST LÀ !
    marge DECIMAL(10,2),
FOREIGN KEY (id_date) REFERENCES  dim_dates(id_date),
FOREIGN KEY (id_client) REFERENCES dim_clients (id_client),
FOREIGN KEY (id_produit) REFERENCES dim_produits (id_produit),
FOREIGN KEY (id_statut) REFERENCES dim_statut(id_statut)
);

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
	(TO_CHAR (cmd.date_commande, 'YYYYMMDD') :: INTEGER) AS id_date,
	cli_dim.id_client AS id_client,
	prod_dim.id_produit AS id_produit,
	CASE cmd.statut
		WHEN 'Confirmée' THEN 1
		WHEN 'Annulée' THEN 2
		WHEN 'En attente' THEN 3
		ELSE NULL
	END AS id_statut,
	
	cmd.quantite,
	prod_source.prix AS prix_unitaire,
	cmd.reduction,
	COALESCE (cmd.quantite * prod_source.prix * (1- cmd.reduction/100.0), 0) AS montant_total,
	COALESCE ((cmd.quantite * prod_source.prix * (1- cmd.reduction/100.0)), 0) 
	- COALESCE((cmd.quantite * prod_source.cout_production), 0) AS marge

FROM commandes AS cmd

LEFT JOIN dim_clients AS cli_dim ON cmd.client_id = cli_dim.client_id_original
LEFT JOIN dim_produits AS prod_dim ON cmd.produit_id = prod_dim.produit_id_original
LEFT JOIN produits AS prod_source ON cmd.produit_id = prod_source.produit_id;



CREATE INDEX idx_clients_original ON dim_clients(client_id_original);
CREATE INDEX idx_produits_original ON dim_produits(produit_id_original);
CREATE INDEX idx_fct_date ON fct_commandes(id_date);
CREATE INDEX idx_fct_client ON fct_commandes(id_client);
CREATE INDEX idx_fct_produit ON fct_commandes(id_produit);
CREATE INDEX idx_fct_statut ON fct_commandes(id_statut);

