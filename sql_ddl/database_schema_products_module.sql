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
    FOREIGN KEY (ParentCategoryID) REFERENCES Categories(CategoryID) ON DELETE SET NULL
);

-- Products Table
CREATE TABLE Products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    SKU VARCHAR(50) NOT NULL UNIQUE,
    ProductName VARCHAR(255) NOT NULL,
    Description TEXT,
    CategoryID INT,
    SupplierID INT,

    StandardCostPrice DECIMAL(12, 2) DEFAULT 0.00,
    LastPurchasePrice DECIMAL(12, 2) NULL,
    ShopSellingPrice DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    FieldSellingPrice DECIMAL(12, 2) NULL,
    WholesalePrice DECIMAL(12, 2) NULL,

    UnitOfMeasure VARCHAR(20),
    ReorderLevel INT DEFAULT 0,

    RequiresExpiryDate BOOLEAN NOT NULL DEFAULT FALSE,
    RequiresBatchNumber BOOLEAN NOT NULL DEFAULT FALSE,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID) ON DELETE SET NULL
    -- FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE SET NULL -- Add when Suppliers table is defined
);

-- ProductImages Table
CREATE TABLE ProductImages (
    ProductImageID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    ProductID INT NOT NULL,
    ImagePath VARCHAR(255) NULL,
    ImageURL VARCHAR(2048) NULL,
    IsPrimaryImage BOOLEAN NOT NULL DEFAULT FALSE,
    Caption VARCHAR(255) NULL,
    SortOrder INT DEFAULT 0,
    UploadedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
    CONSTRAINT CHK_ImagePathOrURL CHECK (ImagePath IS NOT NULL OR ImageURL IS NOT NULL)
);

-- Indexing suggestions
-- CREATE INDEX IDX_Products_CategoryID ON Products(CategoryID);
-- CREATE INDEX IDX_Products_SupplierID ON Products(SupplierID);
-- CREATE INDEX IDX_Products_ProductName ON Products(ProductName);
-- CREATE INDEX IDX_ProductImages_ProductID ON ProductImages(ProductID);

-- Note on AUTO_INCREMENT:
-- MySQL: INT PRIMARY KEY AUTO_INCREMENT
-- PostgreSQL: SERIAL PRIMARY KEY or INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
-- SQLite: INTEGER PRIMARY KEY AUTOINCREMENT
-- SQL Server: INT IDENTITY(1,1) PRIMARY KEY

-- End of SQL DDL for Products Module Tables.
