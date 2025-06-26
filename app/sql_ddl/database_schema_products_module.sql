-- SQL DDL for Products Module Tables (Iteration 2 Design)
-- Timestamp columns default to CURRENT_TIMESTAMP on creation.
-- For UpdatedAt, many databases require a trigger or application-level logic
-- to update it automatically on row modification.

-- Categories Table
CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    CategoryName VARCHAR(100) NOT NULL UNIQUE,
    Description TEXT,
    ParentCategoryID INT,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update
    FOREIGN KEY (ParentCategoryID) REFERENCES Categories(CategoryID) ON DELETE SET NULL -- Allows parent to be deleted without deleting children
);

-- Products Table
CREATE TABLE Products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    SKU VARCHAR(50) NOT NULL UNIQUE,
    ProductName VARCHAR(255) NOT NULL,
    Description TEXT,
    CategoryID INT,
    SupplierID INT, -- Assuming a Suppliers table exists or will be created later. FK constraint can be added then.

    -- Pricing Fields from Iteration 2
    StandardCostPrice DECIMAL(12, 2) DEFAULT 0.00,
    LastPurchasePrice DECIMAL(12, 2) NULL,
    ShopSellingPrice DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    FieldSellingPrice DECIMAL(12, 2) NULL,
    WholesalePrice DECIMAL(12, 2) NULL,

    UnitOfMeasure VARCHAR(20),
    ReorderLevel INT DEFAULT 0,

    -- Fields for Expiry and Batch Tracking
    RequiresExpiryDate BOOLEAN NOT NULL DEFAULT FALSE,
    RequiresBatchNumber BOOLEAN NOT NULL DEFAULT FALSE,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update

    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID) ON DELETE SET NULL
    -- FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE SET NULL -- Add when Suppliers table is defined
);

-- ProductImages Table
CREATE TABLE ProductImages (
    ProductImageID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    ProductID INT NOT NULL,
    ImagePath VARCHAR(255) NULL, -- Path for locally stored images
    ImageURL VARCHAR(2048) NULL, -- URL for externally hosted images (CDN, etc.)
    IsPrimaryImage BOOLEAN NOT NULL DEFAULT FALSE,
    Caption VARCHAR(255) NULL,
    SortOrder INT DEFAULT 0,
    UploadedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE, -- If product is deleted, its images are also deleted
    CONSTRAINT CHK_ImagePathOrURL CHECK (ImagePath IS NOT NULL OR ImageURL IS NOT NULL) -- Ensure at least one path/URL is provided
);

-- Indexing suggestions (can be added after table creation for performance)
-- CREATE INDEX IDX_Products_CategoryID ON Products(CategoryID);
-- CREATE INDEX IDX_Products_SupplierID ON Products(SupplierID);
-- CREATE INDEX IDX_Products_ProductName ON Products(ProductName); -- For searching by name
-- CREATE INDEX IDX_ProductImages_ProductID ON ProductImages(ProductID);

-- Note on AUTO_INCREMENT:
-- MySQL: INT PRIMARY KEY AUTO_INCREMENT
-- PostgreSQL: SERIAL PRIMARY KEY or INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
-- SQLite: INTEGER PRIMARY KEY AUTOINCREMENT
-- SQL Server: INT IDENTITY(1,1) PRIMARY KEY

-- Note on Foreign Key to Suppliers:
-- The Products table has a SupplierID. The FOREIGN KEY constraint for it
-- should be added once the Suppliers table is defined.
-- Example:
-- ALTER TABLE Products
-- ADD CONSTRAINT FK_Products_Suppliers
-- FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE SET NULL;

-- Application logic should ensure that for a given ProductID, only one ProductImage has IsPrimaryImage = TRUE.
-- This can be handled via unique partial indexes in some DBs (e.g., PostgreSQL) or application-level checks.
-- Example for PostgreSQL:
-- CREATE UNIQUE INDEX UQ_ProductPrimaryImage ON ProductImages (ProductID, IsPrimaryImage) WHERE IsPrimaryImage = TRUE;
-- (This specific syntax might vary or not be supported directly in all SQL databases.
--  If not, application logic during image update/creation must enforce this rule.)

-- Reminder: The 'Suppliers' table and other related tables like 'CustomerGroups', 'Discounts', etc.,
-- are not included in this specific DDL set, as the current step focuses on the core Product module tables.
-- They will be generated in subsequent steps when we focus on those modules.
-- Also, the 'StoreInventory' and 'ProductStockBatches' tables, which are critical for actual stock quantities,
-- are part of the broader Inventory module and will be detailed when implementing that section.
-- This DDL focuses on the product definition itself.
-- The `SupplierID` in `Products` is a placeholder for a default/preferred supplier.
-- Actual supplier links for purchases happen through Purchase Orders and GRNs.
-- The `StandardCostPrice` is the theoretical/standard cost. `LastPurchasePrice` can be updated from GRNs.
-- `ShopSellingPrice`, `FieldSellingPrice`, `WholesalePrice` are the defined selling prices before dynamic discounts.
-- `RequiresExpiryDate` and `RequiresBatchNumber` are flags to inform other modules (like GRN and Stock Adjustments)
-- that these details are mandatory for this product.
-- The `ProductStockBatches` table (to be designed with Inventory module) will hold actual stock with batch/expiry.
-- `StoreInventory` (also Inventory module) would then either be a summary or replaced by `ProductStockBatches` for queries.
-- For now, `Products` table defines the product's characteristics.

-- End of SQL DDL for Products Module Tables.
