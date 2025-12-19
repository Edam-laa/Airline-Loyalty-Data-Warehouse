/* ==========================================================================
   SCRIPT DE CRÉATION DU DATA WAREHOUSE (OPTIMISÉ FLOCON + MENSUEL)
   
   Ordre de suppression (Drop) : Du centre vers l'extérieur
   Ordre de création (Create) : De l'extérieur vers le centre
   ========================================================================== */


/* ============================================================
   ETAPE 1 : LES PETITES DIMENSIONS (Niveau 1)
   Elles ne dépendent de personne.
   Types larges (NVARCHAR 255) pour avaler facilement le Staging.
   ============================================================ */

CREATE TABLE Dim_Location (
    Location_PK INT IDENTITY(1,1) PRIMARY KEY,  -- Clé technique (1, 2, 3...)
    City NVARCHAR(255),
    Province NVARCHAR(255),
    Country NVARCHAR(255),
    [Postal Code] NVARCHAR(255)
);

CREATE TABLE Dim_Demographics (
    Demographics_PK INT IDENTITY(1,1) PRIMARY KEY,
    Gender NVARCHAR(255),
    Education NVARCHAR(255),
    [Marital Status] NVARCHAR(255)
);


CREATE TABLE Dim_Loyalty_Profile (
    Loyalty_Profile_PK INT IDENTITY(1,1) PRIMARY KEY,
    [Loyalty Card] NVARCHAR(255),
    [Enrollment Type] NVARCHAR(255)
);

/* ============================================================
   ETAPE 2 : LA DIMENSION DATE (MENSUELLE)
   Conformément à ta demande : 1 ligne par mois, Clé auto-incrémentée.
   ============================================================ */

CREATE TABLE Dim_Date (
    Date_PK INT IDENTITY(1,1) PRIMARY KEY,      -- Clé technique (1, 2, 3...)
    [Start of Month] DATE,                         -- Ex: 2018-01-01
    [Start of Quarter] DATE,                       -- Ex: 2018-01-01
    [Start of Year] DATE                           -- Ex: 2018-01-01
);


/* ============================================================
   ETAPE 3 : LA DIMENSION CUSTOMER (LE HUB)
   Elle lie les infos clients aux petites dimensions.
   ============================================================ */

CREATE TABLE Dim_Customer (
    Customer_PK INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Business Key (Venant du fichier source)
    -- IMPORTANT : Convertir le FLOAT du Staging en NVARCHAR dans SSIS
    [Loyalty Number] FLOAT NOT NULL, 

    -- Clés étrangères (Le Flocon)
    Location_FK INT,
    Demographics_FK INT,
    Loyalty_Profile_FK INT,

    -- Attributs Client
    Salary FLOAT,        -- Mieux que FLOAT pour l'argent
    CLV FLOAT,
    
    -- Dates (Reconstruites)
    [Enrollment Date] DATE,         
    [Cancellation Date] DATE,

    -- Relations (FK)
    FOREIGN KEY (Location_FK) REFERENCES Dim_Location(Location_PK),
    FOREIGN KEY (Demographics_FK) REFERENCES Dim_Demographics(Demographics_PK),
    FOREIGN KEY (Loyalty_Profile_FK) REFERENCES Dim_Loyalty_Profile(Loyalty_Profile_PK)
);

/* ============================================================
   ETAPE 4 : LA TABLE DE FAITS
   Elle lie l'activité au Client et à la Période (Mois).
   ============================================================ */

CREATE TABLE Fact_Flight_Activity (
    Fact_ID INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Clés étrangères vers les dimensions principales
    Customer_FK INT NOT NULL,
    Date_FK INT NOT NULL,

    -- Mesures (Faits)
    Total_Flights Float,
    Distance Float,
    [Points Accumulated] Float,
    [Points Redeemed] Float,
    [Dollar Cost Points Redeemed] FLOAT ,

    -- Relations (FK)
    FOREIGN KEY (Customer_FK) REFERENCES Dim_Customer(Customer_PK),
    FOREIGN KEY (Date_FK) REFERENCES Dim_Date(Date_PK)
);
