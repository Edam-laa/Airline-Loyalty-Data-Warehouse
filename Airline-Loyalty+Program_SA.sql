
/* ============================================================
   TABLE 1 : Customer_History_SA
   Source : Customer Loyalty History.xlsx
   Types SSIS : DT_WSTR(255) pour les textes, DT_R8 pour les nombres
   ============================================================ */
CREATE TABLE Customer_History_SA (
    -- Les champs détectés comme numériques (DT_R8) par SSIS doivent être FLOAT ici
    [Loyalty Number] FLOAT, 
    
    -- Les champs textes (DT_WSTR 255)
    [Country] NVARCHAR(255), 
    [Province] NVARCHAR(255), 
    [City] NVARCHAR(255), 
    [Postal Code] NVARCHAR(255), 
    [Gender] NVARCHAR(255), 
    [Education] NVARCHAR(255), 
    
    -- Attention : Salary est souvent monétaire, mais Excel l'envoie souvent en FLOAT
    [Salary] FLOAT, 
    
    [Marital Status] NVARCHAR(255), 
    [Loyalty Card] NVARCHAR(255), 
    
    [CLV] FLOAT, 
    
    [Enrollment Type] NVARCHAR(255), 
    [Enrollment Year] FLOAT, 
    [Enrollment Month] FLOAT, 
    [Cancellation Year] FLOAT, 
    [Cancellation Month] FLOAT 
    
    -- Note : On ne met pas de PRIMARY KEY ici car c'est du vrac (Staging)
);
/* ============================================================
   TABLE 2 : Calendar_SA
   Source : Calendar.xlsx
   Types SSIS : Tout est détecté comme DT_WSTR(255) selon ton analyse
   ============================================================ */
CREATE TABLE Calendar_SA (
    -- Même si ce sont des dates, si SSIS voit du texte, on stocke du texte
    [Date] NVARCHAR(255),
    [Start of Year] NVARCHAR(255),
    [Start of Quarter] NVARCHAR(255),
    [Start of Month] NVARCHAR(255)
);

/* ============================================================
   TABLE 3 : Activity_SA
   Source : Customer Flight Activity.xlsx
   Types SSIS : Tout est détecté comme DT_R8 (Float double precision)
   ============================================================ */
CREATE TABLE Activity_SA (
    [Loyalty Number] FLOAT, -- Sera converti en INT ou VARCHAR plus tard vers le DW
    [Year] FLOAT,
    [Month] FLOAT,
    [Total Flights] FLOAT,
    [Distance] FLOAT,
    [Points Accumulated] FLOAT,
    [Points Redeemed] FLOAT,
    [Dollar Cost Points Redeemed] FLOAT
);