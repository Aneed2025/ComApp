-- SQL DDL for CustomerGroups and Customers Tables (Iteration 2 Design)
-- Timestamp columns default to CURRENT_TIMESTAMP on creation.
-- For UpdatedAt, many databases require a trigger or application-level logic
-- to update it automatically on row modification.

-- CustomerGroups Table
CREATE TABLE CustomerGroups (
    CustomerGroupID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    GroupName VARCHAR(100) NOT NULL UNIQUE,
    Description TEXT NULL,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- Consider trigger for auto-update
);

-- Customers Table
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    CustomerName VARCHAR(150) NOT NULL,
    CustomerGroupID INT NULL, -- Can be NULL if a customer doesn't belong to a specific group initially

    -- Unique Identifier
    NationalID VARCHAR(30) NULL UNIQUE, -- Or TaxID, UniqueIdNumber. Length might vary. Made UNIQUE.

    -- Contact Details
    ContactPerson VARCHAR(100) NULL,
    Email VARCHAR(100) NULL UNIQUE, -- Made UNIQUE as it's often a login or key identifier
    Phone VARCHAR(30) NULL,
    SecondaryPhone VARCHAR(30) NULL,

    -- Address Details
    Address TEXT NULL, -- Using TEXT for longer addresses, VARCHAR(255) is also common
    AddressLine2 VARCHAR(255) NULL,
    City VARCHAR(50) NULL,
    StateOrProvince VARCHAR(50) NULL,
    Country VARCHAR(50) NULL,
    PostalCode VARCHAR(20) NULL,

    -- Financial Information
    CreditLimit DECIMAL(12, 2) DEFAULT 0.00,
    -- CurrentBalance will be a calculated field or managed by transactions, not stored directly here usually
    -- Or if stored, it's for denormalization and needs careful updates.
    -- For now, we assume it's calculated. If needed as a stored field:
    -- CurrentBalance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    DefaultPaymentTermsID INT NULL, -- FK to a future PaymentTermsDefinitions table
    DefaultCurrencyID INT NULL, -- FK to a future Currencies table
    DefaultSalespersonID INT NULL, -- FK to Employees table

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update

    FOREIGN KEY (CustomerGroupID) REFERENCES CustomerGroups(CustomerGroupID) ON DELETE SET NULL
    -- FOREIGN KEY (DefaultPaymentTermsID) REFERENCES PaymentTermsDefinitions(PaymentTermsID) ON DELETE SET NULL; -- Add when table exists
    -- FOREIGN KEY (DefaultCurrencyID) REFERENCES Currencies(CurrencyID) ON DELETE SET NULL; -- Add when table exists
    -- FOREIGN KEY (DefaultSalespersonID) REFERENCES Employees(EmployeeID) ON DELETE SET NULL; -- Add when table exists
);

-- Indexing suggestions
-- CREATE INDEX IDX_Customers_CustomerName ON Customers(CustomerName);
-- CREATE INDEX IDX_Customers_CustomerGroupID ON Customers(CustomerGroupID);
-- CREATE INDEX IDX_Customers_Email ON Customers(Email);
-- CREATE INDEX IDX_Customers_NationalID ON Customers(NationalID);

-- Note on CurrentBalance:
-- Storing CurrentBalance directly in the Customers table is a form of denormalization.
-- It can improve read performance for customer listings but requires careful management
-- to keep it synchronized with actual invoice and payment transactions (e.g., using triggers or application logic).
-- The alternative is to calculate it on-the-fly when needed, which ensures accuracy but might be slower for reports on many customers.
-- For this DDL, I've commented it out, assuming it will be a calculated value. If you prefer to store it, uncomment the line.

-- Note on DefaultPaymentTermsID and DefaultCurrencyID:
-- These reference tables (PaymentTermsDefinitions, Currencies) that are not yet defined in our current scope
-- but are common in ERP systems. The FK constraints are commented out until those tables are created.

-- End of SQL DDL for CustomerGroups and Customers Tables.
