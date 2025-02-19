CREATE TABLE IF NOT EXISTS income_statement (
        company_id INTEGER,
        year INTEGER,
        -- ids

        net_sales REAL,
        cost_of_goods_sold REAL,
        -- gross profit

        operating_expense REAL,
        -- operating income (EBIT)

        interest_expense REAL,
        -- pre-tax income (EBT)
        
        taxes REAL,
        -- net income
        
        PRIMARY KEY (company_id, year)
    );