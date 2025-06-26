
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
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
);

-- Customers Table
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    CustomerName VARCHAR(150) NOT NULL,
    CustomerGroupID INT NULL, 
    
    NationalID VARCHAR(30) NULL UNIQUE, 

    ContactPerson VARCHAR(100) NULL,
    Email VARCHAR(100) NULL UNIQUE, 
    Phone VARCHAR(30) NULL,
    SecondaryPhone VARCHAR(30) NULL,

    Address TEXT NULL, 
    AddressLine2 VARCHAR(255) NULL,
    City VARCHAR(50) NULL,
    StateOrProvince VARCHAR(50) NULL,
    Country VARCHAR(50) NULL,
    PostalCode VARCHAR(20) NULL,

    CreditLimit DECIMAL(12, 2) DEFAULT 0.00,
    -- CurrentBalance is typically calculated. If stored:
    -- CurrentBalance DECIMAL(12, 2) NOT NULL DEFAULT 0.00, 
    DefaultPaymentTermsID INT NULL, 
    DefaultCurrencyID INT NULL, 
    DefaultSalespersonID INT NULL, 

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (CustomerGroupID) REFERENCES CustomerGroups(CustomerGroupID) ON DELETE SET NULL
    -- FOREIGN KEY (DefaultPaymentTermsID) REFERENCES PaymentTermsDefinitions(PaymentTermsID) ON DELETE SET NULL;
    -- FOREIGN KEY (DefaultCurrencyID) REFERENCES Currencies(CurrencyID) ON DELETE SET NULL;
    -- FOREIGN KEY (DefaultSalespersonID) REFERENCES Employees(EmployeeID) ON DELETE SET NULL; 
);

-- End of SQL DDL for CustomerGroups and Customers Tables.