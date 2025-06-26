-- SQL DDL for Suppliers Module Tables (Iteration 2 Design)
-- Timestamp columns default to CURRENT_TIMESTAMP on creation.
-- For UpdatedAt, many databases require a trigger or application-level logic
-- to update it automatically on row modification.

-- Suppliers Table
CREATE TABLE Suppliers (
    SupplierID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    SupplierName VARCHAR(150) NOT NULL UNIQUE,

    TaxID VARCHAR(30) NULL UNIQUE,

    ContactPerson VARCHAR(100) NULL,
    Email VARCHAR(100) NULL UNIQUE,
    Phone VARCHAR(30) NULL,
    SecondaryPhone VARCHAR(30) NULL,
    Website VARCHAR(255) NULL,

    Address TEXT NULL,
    AddressLine2 VARCHAR(255) NULL,
    City VARCHAR(50) NULL,
    StateOrProvince VARCHAR(50) NULL,
    Country VARCHAR(50) NULL,
    PostalCode VARCHAR(20) NULL,

    DefaultPaymentTermsID INT NULL,
    DefaultCurrencyID INT NULL,

    BankName VARCHAR(100) NULL,
    BankAccountNumber VARCHAR(50) NULL,
    BankSwiftCode VARCHAR(20) NULL,
    BankAccountHolderName VARCHAR(150) NULL,
    IBAN VARCHAR(50) NULL,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT CHK_SupplierEmail_Format CHECK (Email IS NULL OR Email LIKE '%_@__%.__%')
);

-- SupplierProducts Table (Linking table for products typically supplied by this supplier)
-- This assumes Products table already exists.
CREATE TABLE SupplierProducts (
    SupplierProductID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    SupplierID INT NOT NULL,
    ProductID INT NOT NULL,

    SupplierProductCode VARCHAR(50) NULL,
    DefaultLeadTimeDays INT NULL,
    LastPurchasePriceFromSupplier DECIMAL(12, 2) NULL,

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
    UNIQUE (SupplierID, ProductID)
);

-- Indexing suggestions
-- CREATE INDEX IDX_Suppliers_SupplierName ON Suppliers(SupplierName);
-- CREATE INDEX IDX_Suppliers_TaxID ON Suppliers(TaxID);
-- CREATE INDEX IDX_Suppliers_Email ON Suppliers(Email);
-- CREATE INDEX IDX_SupplierProducts_SupplierID ON SupplierProducts(SupplierID);
-- CREATE INDEX IDX_SupplierProducts_ProductID ON SupplierProducts(ProductID);

-- End of SQL DDL for Suppliers Module Tables.
