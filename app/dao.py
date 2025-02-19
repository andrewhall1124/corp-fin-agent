from database import Database
from statements import IncomeStatement
from statements import BalanceSheet

def load_income_statement(company_id: int) -> IncomeStatement:

    with Database() as db:
        results = db.execute(
        """
        SELECT 
            year,
            COALESCE(net_sales, 0),
            COALESCE(cost_of_goods_sold, 0),
            COALESCE(operating_expense, 0),
            COALESCE(interest_expense, 0),
            COALESCE(taxes, 0)
        FROM income_statement
        WHERE company_id = ?
        ;
        """,
        (company_id,)
        )

        return IncomeStatement(
            year=[row[0] for row in results],
            net_sales=[row[1] for row in results],
            cost_of_goods_sold=[row[2] for row in results],
            operating_expense=[row[3] for row in results],
            interest_expense=[row[4] for row in results],
            taxes=[row[5] for row in results]
        )

def load_balance_sheet(company_id: int) -> IncomeStatement:

    with Database() as db:
        results = db.execute(
        """
        SELECT 
            year,
            COALESCE(cash, 0),
            COALESCE(accounts_recievable, 0),
            COALESCE(inventory, 0),
            COALESCE(propery_plant_and_equipment, 0),
            COALESCE(accounts_payable, 0),
            COALESCE(short_term_debt, 0),
            COALESCE(long_term_debt_current_portion, 0),
            COALESCE(other_current_liabilities, 0),
            COALESCE(long_term_debt, 0),
            COALESCE(share_holders_equity, 0)
        FROM balance_sheet
        WHERE company_id = ?
        ;
        """,
        (company_id,)
        )

        return BalanceSheet(
            year=[row[0] for row in results],
            cash=[row[1] for row in results],
            accounts_payable=[row[2] for row in results],
            inventory=[row[3] for row in results],
            property_plant_and_equipment=[row[4] for row in results],
            accounts_recievable=[row[5] for row in results],
            short_term_debt=[row[6] for row in results],
            long_term_debt_current_portion=[row[7] for row in results],
            other_current_liabilities=[row[8] for row in results],
            long_term_debt=[row[9] for row in results],
            share_holders_equity=[row[10] for row in results]
        )
