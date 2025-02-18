CREATE TABLE IF NOT EXISTS balance_sheet (
    company_id INTEGER,
    year INTEGER,
    -- ids

    cash REAL,
    accounts_recievable REAL,
    inventory REAL,
    -- total non-current assets

    propery_plant_and_equipment REAL,
    -- total assets

    accounts_payable REAL,
    short_term_debt REAL,
    long_term_debt_current_portion REAL,
    accrued_taxes REAL,
    other_current_liabilities REAL,
    -- total current liabilities

    long_term_debt REAL,
    -- total liabilities

    share_holders_equity REAL,
    -- total equity
    
    PRIMARY KEY (company_id, year)
);