-- SQL DDL for Purchase Order Module Tables

-- PurchaseOrderHeaders Table: Stores header information for each purchase order
CREATE TABLE PurchaseOrderHeaders (
    PurchaseOrderID VARCHAR(50) PRIMARY KEY, -- Generated ID, e.g., PO-[StoreID]-[YY][MM][XXXX]
    SupplierID INT NOT NULL,
    StoreID VARCHAR(10) NOT NULL, -- The store where goods are expected to be delivered

    OrderDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ExpectedDeliveryDate DATE NULL,

    -- Status: e.g., 'Draft', 'PendingApproval', 'Approved', 'SentToSupplier',
    --                'PartiallyReceived', 'FullyReceived', 'Cancelled', 'Closed'
    Status VARCHAR(30) NOT NULL DEFAULT 'Draft',

    -- Amounts calculated from lines
    Subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    TaxAmount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    ShippingCost DECIMAL(10, 2) DEFAULT 0.00,
    OtherCharges DECIMAL(10, 2) DEFAULT 0.00,
    TotalAmount DECIMAL(12, 2) NOT NULL DEFAULT 0.00, -- Grand total of the PO

    Notes TEXT NULL,
    PaymentTermsID INT NULL, -- FK to PaymentTermsDefinitions table
    ShippingAddress TEXT NULL, -- Can be different from store address, or default to store address
    BillingAddress TEXT NULL,  -- Can be different from company default, or default

    CreatedByUserID INT NULL, -- FK to Users/Employees table
    ApprovedByUserID INT NULL, -- FK to Users/Employees table
    ApprovalDate DATETIME NULL,

    -- Link to Purchase Requisition if this PO was generated from one
    PurchaseRequisitionID VARCHAR(50) NULL, -- Assuming RequisitionID is VARCHAR(50)
                                            -- FK constraint to be added when PurchaseRequisitions table is defined.

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update

    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE RESTRICT,
    FOREIGN KEY (StoreID) REFERENCES Stores(StoreID) ON DELETE RESTRICT
    -- FOREIGN KEY (PaymentTermsID) REFERENCES PaymentTermsDefinitions(PaymentTermsID) ON DELETE SET NULL,
    -- FOREIGN KEY (CreatedByUserID) REFERENCES Users(UserID) ON DELETE SET NULL,
    -- FOREIGN KEY (ApprovedByUserID) REFERENCES Users(UserID) ON DELETE SET NULL,
    -- FOREIGN KEY (PurchaseRequisitionID) REFERENCES PurchaseRequisitionHeaders(RequisitionID) ON DELETE SET NULL
);

-- PurchaseOrderLines Table: Stores individual line items for each purchase order
CREATE TABLE PurchaseOrderLines (
    PurchaseOrderLineID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    PurchaseOrderID VARCHAR(50) NOT NULL,
    ProductID INT NOT NULL,

    Description TEXT NULL, -- Can be product name, or overridden
    QuantityOrdered DECIMAL(10, 2) NOT NULL, -- Using DECIMAL for quantity
    UnitOfMeasure VARCHAR(20) NULL,

    UnitPrice DECIMAL(12, 2) NOT NULL, -- Price per unit from supplier quotation/agreement
    LineTotal DECIMAL(12, 2) NOT NULL, -- Calculated: QuantityOrdered * UnitPrice

    -- For tracking received quantity against this PO line
    QuantityReceived DECIMAL(10, 2) DEFAULT 0.00,

    ExpectedLineDeliveryDate DATE NULL, -- If different lines have different expected dates
    Notes TEXT NULL,

    -- Link to Purchase Requisition Line if this PO line was generated from one
    PurchaseRequisitionLineID INT NULL, -- Assuming RequisitionLineID is INT
                                        -- FK constraint to be added when PurchaseRequisitionLines table is defined.

    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrderHeaders(PurchaseOrderID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE RESTRICT,
    -- FOREIGN KEY (PurchaseRequisitionLineID) REFERENCES PurchaseRequisitionLines(RequisitionLineID) ON DELETE SET NULL,
    CONSTRAINT CHK_PO_QuantityOrderedPositive CHECK (QuantityOrdered > 0),
    CONSTRAINT CHK_PO_QuantityReceivedNotNegative CHECK (QuantityReceived >= 0)
);

-- Indexing suggestions
-- CREATE INDEX IDX_POHeaders_SupplierID ON PurchaseOrderHeaders(SupplierID);
-- CREATE INDEX IDX_POHeaders_StoreID ON PurchaseOrderHeaders(StoreID);
-- CREATE INDEX IDX_POHeaders_OrderDate ON PurchaseOrderHeaders(OrderDate);
-- CREATE INDEX IDX_POHeaders_Status ON PurchaseOrderHeaders(Status);
-- CREATE INDEX IDX_POLines_PurchaseOrderID ON PurchaseOrderLines(PurchaseOrderID);
-- CREATE INDEX IDX_POLines_ProductID ON PurchaseOrderLines(ProductID);

-- Note on PurchaseRequisitionID and PurchaseRequisitionLineID:
-- Foreign key constraints for these will be added when the PurchaseRequisitions module DDL is created.

-- End of SQL DDL for Purchase Order Module Tables.
