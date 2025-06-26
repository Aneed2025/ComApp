-- SQL DDL for Stores Module Table

-- Stores Table: Manages information about different warehouses, shops, or field locations.
CREATE TABLE Stores (
    StoreID VARCHAR(10) PRIMARY KEY, -- e.g., 'SH01', 'WH-MAIN', 'FLD-EAST'. Using VARCHAR as per earlier design.
    StoreName VARCHAR(100) NOT NULL,

    -- StoreType: 'Shop', 'Warehouse', 'Field', or other user-defined types.
    -- Consider an ENUM or a separate lookup table for StoreTypes if they become complex.
    StoreType VARCHAR(20) NOT NULL DEFAULT 'Shop'
        CHECK (StoreType IN ('Shop', 'Warehouse', 'Field', 'Office', 'Other')), -- Example types

    -- Address Details
    Address TEXT NULL,
    City VARCHAR(50) NULL,
    StateOrProvince VARCHAR(50) NULL,
    Country VARCHAR(50) NULL,
    PostalCode VARCHAR(20) NULL,

    -- Contact Details
    Phone VARCHAR(30) NULL,
    Email VARCHAR(100) NULL,

    -- Invoice Numbering Prefixes (as per detailed specification)
    -- These are crucial for the custom invoice ID generation.
    CashPrefix VARCHAR(5) NULL UNIQUE, -- e.g., 'CAS'. Made UNIQUE to ensure no two stores try to generate same cash invoice series start.
    LaybyPrefix VARCHAR(5) NULL UNIQUE, -- e.g., 'LAY'. Made UNIQUE.
    FieldPrefix VARCHAR(5) NULL UNIQUE, -- e.g., 'FLD'. Made UNIQUE.
    -- If prefixes are not globally unique but per store type, then uniqueness constraint would be different or handled at app level.
    -- The original requirement: "Prefix is determined by the user...not reserved for another store"
    -- implies the prefix itself should be unique across stores for that type of document.
    -- For simplicity, making them unique here. If a store doesn't handle a type, prefix can be NULL.

    ManagerID INT NULL, -- FK to Employees table (to be added when Employees module is implemented)
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update

    -- FOREIGN KEY (ManagerID) REFERENCES Employees(EmployeeID) ON DELETE SET NULL
    CONSTRAINT CHK_StoreEmail_Format CHECK (Email IS NULL OR Email LIKE '%_@__%.__%') -- Basic email format check
);

-- Indexing suggestions
-- CREATE INDEX IDX_Stores_StoreName ON Stores(StoreName);
-- CREATE INDEX IDX_Stores_StoreType ON Stores(StoreType);
-- CREATE INDEX IDX_Stores_City ON Stores(City);
-- CREATE INDEX IDX_Stores_Country ON Stores(Country);

-- Note on Prefixes:
-- The UNIQUE constraint on CashPrefix, LaybyPrefix, FieldPrefix assumes that if a prefix like 'CAS'
-- is used, it's unique across all stores for that document context.
-- If a store does not use a particular type of invoicing (e.g., a warehouse might not have cash sales),
-- the corresponding prefix field can be NULL.
-- The application logic for generating invoice IDs will fetch these prefixes from the store's record.

-- Note on ManagerID:
-- The FK to Employees table will be added when the Employees module is created.

-- End of SQL DDL for Stores Module Table.
