import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# 1. CONFIGURATION
server = 'LOCALHOST' 
database = 'DW_Flights' 
driver = 'ODBC Driver 17 for SQL Server'

# Chaîne de connexion
connection_string = f'mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes'
engine = create_engine(connection_string)

print("Connexion établie avec succès !")
sns.set_theme(style="whitegrid") # Pour un style propre
# --- QUESTION 1 : ADHÉSIONS (Évolution Temporelle) ---

# On utilise la fonction SQL YEAR() et MONTH() car ta colonne est une DATE complète
query_1 = """
SELECT 
    YEAR([Enrollment Date]) as Annee,
    MONTH([Enrollment Date]) as Mois,
    COUNT(Customer_PK) as Nombre_Inscriptions
FROM Dim_Customer
WHERE [Enrollment Date] IS NOT NULL
GROUP BY YEAR([Enrollment Date]), MONTH([Enrollment Date])
ORDER BY Annee, Mois
"""

df_enroll = pd.read_sql(query_1, engine)

# On crée une colonne 'Date' propre pour que le graphique comprenne l'axe du temps
df_enroll['Date'] = pd.to_datetime(df_enroll.assign(Year=df_enroll['Annee'], Month=df_enroll['Mois'], Day=1)[['Year', 'Month', 'Day']])

# Visualisation
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_enroll, x='Date', y='Nombre_Inscriptions', marker='o', linewidth=2.5, color='royalblue')

# Zone de la campagne (Février 2018 - Avril 2018)
plt.axvspan(pd.Timestamp('2018-02-01'), pd.Timestamp('2018-04-30'), color='orange', alpha=0.3, label='Période Promo')

plt.title("Impact de la Campagne sur les Nouvelles Adhésions", fontsize=16, fontweight='bold')
plt.xlabel("Date")
plt.ylabel("Nouveaux Membres")
plt.legend()
plt.tight_layout()
plt.show()
# --- QUESTION 2 : QUI S'EST INSCRIT PENDANT LA PROMO ? ---

query_2 = """
SELECT 
    d.Gender,
    d.Education,
    COUNT(c.Customer_PK) as Compte
FROM Dim_Customer c
JOIN Dim_Demographics d ON c.Demographics_FK = d.Demographics_PK
WHERE c.[Enrollment Date] BETWEEN '2018-02-01' AND '2018-04-30'
GROUP BY d.Gender, d.Education
ORDER BY Compte DESC
"""

df_demo = pd.read_sql(query_2, engine)

# Visualisation
plt.figure(figsize=(12, 6))
sns.barplot(data=df_demo, x='Education', y='Compte', hue='Gender', palette='viridis')

plt.title("Profil des Adhérents inscrits pendant la Promotion (Fév-Avr 2018)", fontsize=16, fontweight='bold')
plt.xlabel("Niveau d'Éducation")
plt.ylabel("Nombre d'Inscriptions")
plt.xticks(rotation=45)
plt.legend(title='Genre')
plt.tight_layout()
plt.show()
# --- QUESTION 3 : IMPACT SUR LES VOLS D'ÉTÉ ---

query_3 = """
SELECT 
    YEAR(d.[Start of Month]) as Annee,
    SUM(f.Total_Flights) as Total_Vols
FROM Fact_Flight_Activity f
JOIN Dim_Date d ON f.Date_FK = d.Date_PK
WHERE MONTH(d.[Start of Month]) IN (6, 7, 8) -- Juin, Juillet, Août
  AND YEAR(d.[Start of Month]) IN (2017, 2018)
GROUP BY YEAR(d.[Start of Month])
ORDER BY Annee
"""

df_summer = pd.read_sql(query_3, engine)

# Visualisation
plt.figure(figsize=(8, 6))
ax = sns.barplot(data=df_summer, x='Annee', y='Total_Vols', palette='coolwarm')

plt.title("Comparaison des Vols d'Été (Juin-Août) : 2017 vs 2018", fontsize=16, fontweight='bold')
plt.ylabel("Total des Vols")
plt.xlabel("Année")

# Ajouter les étiquettes de valeur sur les barres
for container in ax.containers:
    ax.bar_label(container, fmt='%.0f', padding=3)

plt.tight_layout()
plt.show()
# --- QUESTION 4: ANALYSE GÉOGRAPHIQUE (Dim_Location) ---

# Objectif : Voir quelle Province/Région vole le plus.
# Chemin de jointure : Fact -> Customer -> Location

query_location = """
SELECT TOP 10
    l.Province,
    SUM(Table_Nettoyee.Total_Flights) as Total_Vols
FROM (
    -- 1. On nettoie les doublons de la Fact (Même logique que Q3)
    SELECT DISTINCT 
        Customer_FK,
        Total_Flights
    FROM Fact_Flight_Activity
) as Table_Nettoyee
JOIN Dim_Customer c ON Table_Nettoyee.Customer_FK = c.Customer_PK
JOIN Dim_Location l ON c.Location_FK = l.Location_PK
GROUP BY l.Province
ORDER BY Total_Vols DESC
"""

df_loc = pd.read_sql(query_location, engine)

# --- VISUALISATION ---
plt.figure(figsize=(10, 6))

# On utilise un graphique à barres horizontales (mieux pour lire les noms de villes/provinces)
ax = sns.barplot(data=df_loc, x='Total_Vols', y='Province', palette='magma')

plt.title("Top 10 des Provinces par Volume de Vols", fontsize=16, fontweight='bold')
plt.xlabel("Nombre Total de Vols")
plt.ylabel("Province / État")

# Ajouter les chiffres au bout des barres pour faire pro
for i in ax.containers:
    ax.bar_label(i, fmt='%.0f', padding=3)

plt.tight_layout()
plt.show()
# --- QUESTION 5 : ANALYSE DU PROGRAMME DE FIDÉLITÉ (Dim_Loyalty_Profile) ---

# Objectif : Voir quel type de carte (Loyalty Card) accumule le plus de points en moyenne.
# Chemin : Fact -> Customer -> Loyalty_Profile
# Métrique : Moyenne des points accumulés (Points Accumulated)

query_loyalty = """
SELECT 
    lp.[Loyalty Card] as Statut_Carte,
    AVG(Table_Nettoyee.[Points Accumulated]) as Moyenne_Points
FROM (
    -- 1. Nettoyage des doublons (Crucial pour ne pas fausser la moyenne)
    SELECT DISTINCT 
        Customer_FK,
        Date_FK,
        [Points Accumulated]
    FROM Fact_Flight_Activity
    WHERE [Points Accumulated] > 0 -- On ignore les vols à 0 point
) as Table_Nettoyee
JOIN Dim_Customer c ON Table_Nettoyee.Customer_FK = c.Customer_PK
JOIN Dim_Loyalty_Profile lp ON c.Loyalty_Profile_FK = lp.Loyalty_Profile_PK
GROUP BY lp.[Loyalty Card]
ORDER BY Moyenne_Points DESC
"""

df_loyalty = pd.read_sql(query_loyalty, engine)

# --- VISUALISATION ---
plt.figure(figsize=(10, 6))

# Utilisation d'un barplot avec une palette différente pour distinguer les statuts
ax = sns.barplot(data=df_loyalty, x='Statut_Carte', y='Moyenne_Points', palette='rocket')

plt.title("Moyenne des Points Accumulés par Statut de Carte", fontsize=16, fontweight='bold')
plt.xlabel("Type de Carte de Fidélité")
plt.ylabel("Points Moyens par Vol")

# Ajout des étiquettes de valeur
for i in ax.containers:
    ax.bar_label(i, fmt='%.0f', padding=3)

plt.tight_layout()
plt.show()