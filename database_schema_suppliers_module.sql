-- SQL DDL for Suppliers Module Tables (Iteration 2 Design)
-- Timestamp columns default to CURRENT_TIMESTAMP on creation.
-- For UpdatedAt, many databases require a trigger or application-level logic
-- to update it automatically on row modification.

-- Suppliers Table
CREATE TABLE Suppliers (
    SupplierID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    SupplierName VARCHAR(150) NOT NULL UNIQUE, -- Made UNIQUE as supplier names are often distinct identifiers

    -- Unique Identifier (e.g., Tax ID)
    TaxID VARCHAR(30) NULL UNIQUE, -- Or UniqueIdNumber. Length might vary. Made UNIQUE.

    -- Contact Details
    ContactPerson VARCHAR(100) NULL,
    Email VARCHAR(100) NULL UNIQUE, -- Made UNIQUE
    Phone VARCHAR(30) NULL,
    SecondaryPhone VARCHAR(30) NULL,
    Website VARCHAR(255) NULL,

    -- Address Details
    Address TEXT NULL,
    AddressLine2 VARCHAR(255) NULL,
    City VARCHAR(50) NULL,
    StateOrProvince VARCHAR(50) NULL,
    Country VARCHAR(50) NULL,
    PostalCode VARCHAR(20) NULL,

    -- Financial Information
    -- CurrentBalance is typically calculated or managed by transactions.
    -- If stored: CurrentBalance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    DefaultPaymentTermsID INT NULL, -- FK to a future PaymentTermsDefinitions table
    DefaultCurrencyID INT NULL,     -- FK to a future Currencies table

    -- Bank Details (for payments to supplier)
    BankName VARCHAR(100) NULL,
    BankAccountNumber VARCHAR(50) NULL,
    BankSwiftCode VARCHAR(20) NULL, -- Or BIC
    BankAccountHolderName VARCHAR(150) NULL,
    IBAN VARCHAR(50) NULL,          -- International Bank Account Number

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update

    -- Foreign Key constraints to be added when referenced tables are created:
    -- FOREIGN KEY (DefaultPaymentTermsID) REFERENCES PaymentTermsDefinitions(PaymentTermsID) ON DELETE SET NULL,
    -- FOREIGN KEY (DefaultCurrencyID) REFERENCES Currencies(CurrencyID) ON DELETE SET NULL
    CONSTRAINT CHK_SupplierEmail_Format CHECK (Email IS NULL OR Email LIKE '%_@__%.__%') -- Basic email format check
);

-- SupplierProducts Table (Linking table for products typically supplied by this supplier)
-- This supports the "Products Supplied" tab in the UI design
CREATE TABLE SupplierProducts (
    SupplierProductID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    SupplierID INT NOT NULL,
    ProductID INT NOT NULL,

    SupplierProductCode VARCHAR(50) NULL, -- The supplier's own code for this product
    DefaultLeadTimeDays INT NULL,         -- Typical lead time in days from this supplier for this product
    LastPurchasePriceFromSupplier DECIMAL(12, 2) NULL, -- Last price paid to THIS supplier for THIS product

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE CASCADE, -- If supplier is deleted, these links are removed
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,   -- If product is deleted, these links are removed
    UNIQUE (SupplierID, ProductID) -- A product can be linked to a supplier only once in this context
);

-- Indexing suggestions
-- CREATE INDEX IDX_Suppliers_SupplierName ON Suppliers(SupplierName);
-- CREATE INDEX IDX_Suppliers_TaxID ON Suppliers(TaxID);
-- CREATE INDEX IDX_Suppliers_Email ON Suppliers(Email);
-- CREATE INDEX IDX_SupplierProducts_SupplierID ON SupplierProducts(SupplierID);
-- CREATE INDEX IDX_SupplierProducts_ProductID ON SupplierProducts(ProductID);

-- Note on Products(ProductID) Foreign Key in SupplierProducts:
-- This assumes the Products table (from database_schema_products_module.sql)
-- has already been created or will be created before this table.

-- Note on Email Format Check:
-- The CHK_SupplierEmail_Format is a very basic check. More robust email validation
-- is typically handled at the application level (e.g., by Pydantic's EmailStr).
-- Some databases might not support LIKE for check constraints effectively or have better regex support.

-- End of SQL DDL for Suppliers Module Tables.
