-- SQL DDL for Goods Receipt Note (GRN) Module Tables

-- GoodsReceiptNoteHeaders Table: Header information for each GRN
CREATE TABLE GoodsReceiptNoteHeaders (
    GRN_ID VARCHAR(50) PRIMARY KEY, -- Generated ID, e.g., GRN-[StoreID]-[YY][MM][XXXX]
    PurchaseOrderID VARCHAR(50) NULL, -- Link to the Purchase Order if GRN is based on a PO
    SupplierID INT NULL, -- Can be derived from PO or entered directly for non-PO receipts
    StoreID VARCHAR(10) NOT NULL, -- The store receiving the goods

    ReceiptDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    SupplierDeliveryNoteNumber VARCHAR(50) NULL, -- Supplier's delivery note/challan number

    -- Status: e.g., 'Draft', 'PostedToInventory', 'Cancelled'
    Status VARCHAR(20) NOT NULL DEFAULT 'Draft',

    ReceivedByUserID INT NULL, -- FK to Users/Employees table (who received the goods)
    InspectedByUserID INT NULL, -- FK to Users/Employees table (who inspected the goods, optional)
    InspectionDate DATETIME NULL,

    Notes TEXT NULL,

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrderHeaders(PurchaseOrderID) ON DELETE SET NULL,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE RESTRICT,
    FOREIGN KEY (StoreID) REFERENCES Stores(StoreID) ON DELETE RESTRICT
    -- FOREIGN KEY (ReceivedByUserID) REFERENCES Users(UserID) ON DELETE SET NULL,
    -- FOREIGN KEY (InspectedByUserID) REFERENCES Users(UserID) ON DELETE SET NULL
);

-- GoodsReceiptNoteLines Table: Line items for each GRN, including batch and expiry details
CREATE TABLE GoodsReceiptNoteLines (
    GRNLineID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    GRN_ID VARCHAR(50) NOT NULL,
    PurchaseOrderLineID INT NULL, -- Link to the specific PO line if applicable
    ProductID INT NOT NULL,

    QuantityOrdered DECIMAL(10, 2) NULL, -- From PO line, for reference
    QuantityReceived DECIMAL(10, 2) NOT NULL,
    UnitOfMeasure VARCHAR(20) NULL, -- From Product or PO line

    UnitPriceAtReceipt DECIMAL(12, 2) NULL, -- Actual price from supplier at time of receipt (can be from PO or updated)
    LineTotalAtReceipt DECIMAL(12, 2) NULL, -- Calculated: QuantityReceived * UnitPriceAtReceipt
                                         -- This is for financial reconciliation with Purchase Invoice later.

    -- Batch and Expiry Date tracking, conditional based on Product settings
    BatchNumber VARCHAR(50) NULL,
    ExpiryDate DATE NULL,

    -- Quality/Inspection related fields (optional)
    AcceptedQuantity DECIMAL(10, 2) NULL, -- If different from QuantityReceived due to inspection
    RejectedQuantity DECIMAL(10, 2) NULL,
    RejectionReason TEXT NULL,

    Notes TEXT NULL,

    FOREIGN KEY (GRN_ID) REFERENCES GoodsReceiptNoteHeaders(GRN_ID) ON DELETE CASCADE,
    FOREIGN KEY (PurchaseOrderLineID) REFERENCES PurchaseOrderLines(PurchaseOrderLineID) ON DELETE SET NULL,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE RESTRICT,
    CONSTRAINT CHK_GRN_QuantityReceivedPositive CHECK (QuantityReceived > 0),
    CONSTRAINT CHK_GRN_AcceptedRejected CHECK (AcceptedQuantity IS NULL OR RejectedQuantity IS NULL OR (AcceptedQuantity + RejectedQuantity <= QuantityReceived))
);

-- Indexing suggestions
-- CREATE INDEX IDX_GRNHeaders_PurchaseOrderID ON GoodsReceiptNoteHeaders(PurchaseOrderID);
-- CREATE INDEX IDX_GRNHeaders_SupplierID ON GoodsReceiptNoteHeaders(SupplierID);
-- CREATE INDEX IDX_GRNHeaders_StoreID ON GoodsReceiptNoteHeaders(StoreID);
-- CREATE INDEX IDX_GRNHeaders_ReceiptDate ON GoodsReceiptNoteHeaders(ReceiptDate);
-- CREATE INDEX IDX_GRNLines_GRN_ID ON GoodsReceiptNoteLines(GRN_ID);
-- CREATE INDEX IDX_GRNLines_ProductID ON GoodsReceiptNoteLines(ProductID);
-- CREATE INDEX IDX_GRNLines_BatchNumber ON GoodsReceiptNoteLines(BatchNumber) WHERE BatchNumber IS NOT NULL;
-- CREATE INDEX IDX_GRNLines_ExpiryDate ON GoodsReceiptNoteLines(ExpiryDate) WHERE ExpiryDate IS NOT NULL;

-- Note on ProductStockBatches and InventoryTransactions:
-- When a GRN is 'PostedToInventory':
-- 1. Entries should be made into `ProductStockBatches` (or a similar detailed inventory table)
--    for each GRNLine, including BatchNumber and ExpiryDate if provided.
-- 2. An `InventoryTransaction` record should be created for each GRNLine to log the stock increase.
-- The DDL for `ProductStockBatches` and `InventoryTransactions` will be part of the detailed Inventory module.

-- Note on UnitPriceAtReceipt:
-- This field is important for accurately calculating the cost of goods received, which might
-- differ from the PO price due to supplier price changes or other factors.
-- This will be used when matching GRN with Purchase Invoice from supplier.

-- End of SQL DDL for Goods Receipt Note Module Tables.
