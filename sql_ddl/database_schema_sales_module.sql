-- SQL DDL for Sales Invoice Module Tables

-- SalesInvoiceHeaders Table: Stores header information for each sales invoice
CREATE TABLE SalesInvoiceHeaders (
    SalesInvoiceID VARCHAR(50) PRIMARY KEY, -- Generated ID, e.g., CASDDMMYYYYXXXX or LAYXXXXX
    CustomerID INT NOT NULL,
    StoreID VARCHAR(10) NOT NULL, -- Assuming StoreID is VARCHAR(10)

    InvoiceDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    DueDate DATE NULL, -- Calculated based on payment terms or manually set

    InvoiceType VARCHAR(20) NOT NULL, -- e.g., 'Cash', 'Layby', 'Field' - influences numbering and potentially pricing/terms

    -- Amounts calculated from lines
    Subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,         -- Sum of (LineUnitPriceBeforeDiscount * Quantity)
    TotalProductDiscountAmount DECIMAL(12, 2) NOT NULL DEFAULT 0.00, -- Sum of product-specific discounts on lines
    TotalInvoiceDiscountAmount DECIMAL(12, 2) NOT NULL DEFAULT 0.00, -- Overall manual discount applied to the invoice total

    TaxableAmount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    TaxRate DECIMAL(5, 2) DEFAULT 0.00, -- Overall tax rate if applicable, or sum of line taxes
    TaxAmount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,

    ShippingCharges DECIMAL(10, 2) DEFAULT 0.00,
    OtherCharges DECIMAL(10, 2) DEFAULT 0.00,
    GrandTotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,      -- Final amount due

    AmountPaid DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    BalanceDue DECIMAL(12, 2) NOT NULL DEFAULT 0.00,      -- Calculated as GrandTotal - AmountPaid

    -- Status: e.g., 'Draft', 'Issued', 'PartiallyPaid', 'Paid', 'Void', 'Cancelled'
    Status VARCHAR(20) NOT NULL DEFAULT 'Draft',

    Notes TEXT NULL,
    SalespersonID INT NULL, -- FK to Employees table
    PaymentTermsID INT NULL, -- FK to PaymentTermsDefinitions table

    -- For linking to Sales Order if generated from one
    SalesOrderID VARCHAR(50) NULL, -- Assuming SalesOrderID is VARCHAR(50)

    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update

    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE RESTRICT,
    FOREIGN KEY (StoreID) REFERENCES Stores(StoreID) ON DELETE RESTRICT, -- Assumes Stores table exists
    -- FOREIGN KEY (SalespersonID) REFERENCES Employees(EmployeeID) ON DELETE SET NULL,
    -- FOREIGN KEY (PaymentTermsID) REFERENCES PaymentTermsDefinitions(PaymentTermsID) ON DELETE SET NULL,
    -- FOREIGN KEY (SalesOrderID) REFERENCES SalesOrderHeaders(SalesOrderID) ON DELETE SET NULL -- If SalesOrders module exists
    CONSTRAINT CHK_BalanceDue CHECK (BalanceDue >= 0) -- Balance due should not be negative usually
);

-- SalesInvoiceLines Table: Stores individual line items for each sales invoice
CREATE TABLE SalesInvoiceLines (
    SalesInvoiceLineID INT PRIMARY KEY AUTO_INCREMENT, -- Or SERIAL for PostgreSQL
    SalesInvoiceID VARCHAR(50) NOT NULL,
    ProductID INT NOT NULL,

    Description TEXT NULL, -- Can be product name, or overridden
    Quantity DECIMAL(10, 2) NOT NULL, -- Using DECIMAL for quantity to support fractional quantities if needed (e.g., kg)
    UnitOfMeasure VARCHAR(20) NULL, -- e.g., 'pcs', 'kg', 'box'

    -- Pricing details for clarity and audit
    UnitPriceBeforeDiscount DECIMAL(12, 2) NOT NULL, -- The base price (Shop, Field, Wholesale) before specific product discount
    ProductDiscountAmount DECIMAL(12, 2) DEFAULT 0.00, -- Discount amount applied specifically to this product line
    ProductDiscountPercentage DECIMAL(5, 2) DEFAULT 0.00, -- Or the percentage if discount was % based
    UnitPriceAfterProductDiscount DECIMAL(12, 2) NOT NULL, -- UnitPriceBeforeDiscount - ProductDiscountAmount

    LineSubtotal DECIMAL(12, 2) NOT NULL, -- Quantity * UnitPriceAfterProductDiscount (before any overall invoice discount or line taxes)

    -- Cost price at the time of sale for COGS calculation
    CostPriceAtSale DECIMAL(12, 2) NOT NULL,

    -- Line-specific tax if applicable (more flexible than a single invoice tax rate)
    LineTaxRate DECIMAL(5, 2) DEFAULT 0.00,
    LineTaxAmount DECIMAL(12, 2) DEFAULT 0.00,

    LineTotal DECIMAL(12, 2) NOT NULL, -- LineSubtotal + LineTaxAmount (This is the final amount for this line)

    Notes TEXT NULL,

    FOREIGN KEY (SalesInvoiceID) REFERENCES SalesInvoiceHeaders(SalesInvoiceID) ON DELETE CASCADE, -- If header is deleted, lines are deleted
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE RESTRICT,
    CONSTRAINT CHK_QuantityPositive CHECK (Quantity > 0)
);

-- Indexing suggestions
-- CREATE INDEX IDX_SalesInvoiceHeaders_CustomerID ON SalesInvoiceHeaders(CustomerID);
-- CREATE INDEX IDX_SalesInvoiceHeaders_StoreID ON SalesInvoiceHeaders(StoreID);
-- CREATE INDEX IDX_SalesInvoiceHeaders_InvoiceDate ON SalesInvoiceHeaders(InvoiceDate);
-- CREATE INDEX IDX_SalesInvoiceHeaders_Status ON SalesInvoiceHeaders(Status);
-- CREATE INDEX IDX_SalesInvoiceLines_SalesInvoiceID ON SalesInvoiceLines(SalesInvoiceID);
-- CREATE INDEX IDX_SalesInvoiceLines_ProductID ON SalesInvoiceLines(ProductID);

-- Note on Stores table:
-- The FK to Stores(StoreID) assumes a Stores table exists with StoreID as VARCHAR(10).
-- The DDL for Stores needs to be created if not already done as part of a core/config module.

-- Note on SalesOrderID:
-- If Sales Orders are implemented, SalesInvoiceHeaders can link to a SalesOrderID.

-- Note on Taxes:
-- Tax calculation can be complex (e.g., different rates per product, tax-on-tax).
-- This schema provides for a simple overall tax or line-item tax.
-- TotalInvoiceDiscountAmount is for manual discounts applied at the invoice level,
-- AFTER product-specific discounts are applied to lines.
-- The calculation sequence would typically be:
-- 1. Line: UnitPriceBeforeDiscount - ProductDiscountAmount = UnitPriceAfterProductDiscount
-- 2. Line: LineSubtotal = Quantity * UnitPriceAfterProductDiscount
-- 3. Invoice: Subtotal = SUM(LineSubtotal of all lines)
-- 4. Invoice: TaxableAmount = Subtotal - TotalInvoiceDiscountAmount (if discount is pre-tax)
-- 5. Invoice: TaxAmount = TaxableAmount * TaxRate (or SUM(LineTaxAmount))
-- 6. Invoice: GrandTotal = TaxableAmount + TaxAmount + ShippingCharges + OtherCharges (or Subtotal - TotalInvoiceDiscountAmount + TaxAmount + ...)

-- End of SQL DDL for Sales Invoice Module Tables.
