-- SQL DDL for Discount Management Module Tables (Iteration 2 Design)

-- Discounts Table: Defines the core discount rules
CREATE TABLE Discounts (
    DiscountID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    DiscountName VARCHAR(100) NOT NULL UNIQUE,
    Description TEXT NULL,

    -- DiscountType: 'Percentage', 'FixedAmountOff', 'SpecialPrice'
    -- We'll use a VARCHAR here. In a real DB, an ENUM or a lookup table might be better.
    DiscountType VARCHAR(20) NOT NULL
        CHECK (DiscountType IN ('Percentage', 'FixedAmountOff', 'SpecialPrice')),

    Value DECIMAL(12, 2) NOT NULL, -- For Percentage, stores the percent (e.g., 10.00 for 10%). For FixedAmountOff, the amount. For SpecialPrice, the actual price.

    StartDate DATETIME NOT NULL,
    EndDate DATETIME NULL, -- NULL means ongoing until deactivated

    RequiresCouponCode BOOLEAN NOT NULL DEFAULT FALSE,
    CouponCode VARCHAR(50) NULL, -- Should be UNIQUE if RequiresCouponCode is TRUE and codes are globally unique.
                                 -- Consider a separate table for coupon codes if they can be many and have their own properties (e.g., usage limits).
                                 -- For now, keeping it simple here.

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- Consider trigger for auto-update
);

-- Add a unique constraint for CouponCode if it's required and should be unique when not NULL
-- This syntax varies by DB. Example for PostgreSQL (partial index):
-- CREATE UNIQUE INDEX UQ_CouponCode ON Discounts (CouponCode) WHERE CouponCode IS NOT NULL AND RequiresCouponCode = TRUE;
-- For MySQL, you might need a regular UNIQUE constraint and handle NULLs appropriately or use a trigger.

-- ProductDiscounts Table: Links Discounts to specific Products and defines applicability conditions
CREATE TABLE ProductDiscounts (
    ProductDiscountID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    ProductID INT NOT NULL,
    DiscountID INT NOT NULL,

    MinQuantity INT NOT NULL DEFAULT 1, -- Minimum quantity of the product for the discount to apply
    MaxQuantity INT NULL, -- Maximum quantity for which this discount applies (e.g., "10% off first 5 items")

    Priority INT NOT NULL DEFAULT 0, -- For resolving multiple applicable discounts (e.g., higher number = higher priority)
    IsCumulative BOOLEAN NOT NULL DEFAULT FALSE, -- Can this discount be combined with other product-level discounts? (Advanced)

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (DiscountID) REFERENCES Discounts(DiscountID) ON DELETE CASCADE,
    UNIQUE (ProductID, DiscountID) -- A specific discount rule should apply only once to a product directly
);

-- DiscountStoreApplicability Table: Specifies which stores a discount is valid for
-- If a DiscountID is not in this table, it might mean it's applicable to ALL stores,
-- or NOT applicable to any unless specified. Application logic will define this.
-- For clarity, let's assume if a discount is meant for specific stores, it will have entries here.
-- If it's for ALL stores, it might not have entries, or have a special 'ALL_STORES' marker if preferred.
CREATE TABLE DiscountStoreApplicability (
    DiscountStoreApplicabilityID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL
    DiscountID INT NOT NULL,
    StoreID VARCHAR(10) NOT NULL, -- Assuming StoreID is VARCHAR(10) as per previous designs

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (DiscountID) REFERENCES Discounts(DiscountID) ON DELETE CASCADE,
    FOREIGN KEY (StoreID) REFERENCES Stores(StoreID) ON DELETE CASCADE, -- Assumes Stores table exists with StoreID as PK
    UNIQUE (DiscountID, StoreID)
);

-- DiscountCustomerGroupApplicability Table: Specifies which customer groups a discount is valid for
-- Similar logic to DiscountStoreApplicability regarding 'ALL' applicability.
CREATE TABLE DiscountCustomerGroupApplicability (
    DiscountCustomerGroupApplicabilityID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL
    DiscountID INT NOT NULL,
    CustomerGroupID INT NOT NULL,

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (DiscountID) REFERENCES Discounts(DiscountID) ON DELETE CASCADE,
    FOREIGN KEY (CustomerGroupID) REFERENCES CustomerGroups(CustomerGroupID) ON DELETE CASCADE, -- Assumes CustomerGroups table exists
    UNIQUE (DiscountID, CustomerGroupID)
);

-- Indexing suggestions
-- CREATE INDEX IDX_Discounts_DateRange ON Discounts(StartDate, EndDate);
-- CREATE INDEX IDX_Discounts_CouponCode ON Discounts(CouponCode) WHERE CouponCode IS NOT NULL;
-- CREATE INDEX IDX_ProductDiscounts_DiscountID ON ProductDiscounts(DiscountID);
-- CREATE INDEX IDX_DiscountStoreApplicability_DiscountID ON DiscountStoreApplicability(DiscountID);
-- CREATE INDEX IDX_DiscountStoreApplicability_StoreID ON DiscountStoreApplicability(StoreID);
-- CREATE INDEX IDX_DiscountCustomerGroupApplicability_DiscountID ON DiscountCustomerGroupApplicability(DiscountID);
-- CREATE INDEX IDX_DiscountCustomerGroupApplicability_CustomerGroupID ON DiscountCustomerGroupApplicability(CustomerGroupID);

-- Note on Foreign Keys:
-- This DDL assumes that tables `Products`, `Stores`, and `CustomerGroups` (with their primary keys
-- `ProductID`, `StoreID`, `CustomerGroupID` respectively) have already been defined or will be defined
-- before these tables are created in your database. The DDL for `Products` and `CustomerGroups`
-- has been provided in previous files. `Stores` table DDL would be needed if not yet created.
-- For now, we assume `Stores(StoreID)` exists based on our overall ERP design.

-- End of SQL DDL for Discount Management Module Tables.
