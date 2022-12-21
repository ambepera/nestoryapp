import sqlite3
import pandas as pd
import random
import datetime
import streamlit as st
from datetime import datetime,date,timedelta
import collections

## Function to Gnerate Horizontal Line
def Horizontal_Line(loc=st):
    return loc.markdown("<hr>",unsafe_allow_html=True)

# Main Variables
Today = date.today()
now = datetime.now().strftime("%d_%m_%y-%I-%M-%S-%p")
default_date_PY = Today - timedelta(days=365)

## Function to download data
def DownloadData(viewlabel,df,file_name,locator=st):
    return locator.download_button(label=f"{viewlabel}",
                             data= df.to_csv().encode('utf-8'),
                             file_name=f'{file_name}_{now}.csv',
                              mime='text/csv')

conn = sqlite3.connect("Transactiondatabase.db",check_same_thread=False)
cur = conn.cursor()

#Function to delete all Data in a Table
def DeleteAllData(tablename):
        cur.execute('DELETE FROM {}'.format(tablename))
        conn.commit()

#Function to delete a Table
def DeleteTable(tablename):
        cur.execute('DROP TABLE {}'.format(tablename))
        conn.commit()

# DeleteTable("TransactTable")
# DeleteTable("StocksTable")
# DeleteTable("SalesTable")
# DeleteTable("ClosingStockBalTable")

# DeleteAllData("TransactTable")
# DeleteAllData("StocksTable")
# DeleteAllData("SalesTable")
# DeleteAllData("COGSTable")
# DeleteAllData("ReceivablesAccount")
# DeleteAllData("CashAccount")
# DeleteAllData("PayablesAccount")

# DeleteAllData("ClosingStockBalTable")
# DeleteAllData("ExpensesTable")


# Main Business Class
class Business():

    def __init__(self,name):
        self.name = name
    
    # Method To Create Product/Items Table
    def ProductTable(self):
        cur.execute("""
            CREATE TABLE if not exists ItemTable
            (ID SERIAL, ItemName TEXT(50), ItemMeasure TEXT(500),Descriptions TEXT(1000), CreationDate date)
             """)
    # Method To Create Type of Transactions Table
    def TransactionTypeTable(self):
        cur.execute("""
            CREATE TABLE if not exists TransactionTypeTable
            (ID SERIAL, ActionName TEXT(50), TransactionCategory TEXT(500), StatePart TEXT(500), CreationDate date)
             """)
    # Method To Create Assets Table
    def AssetsTable(self):
        cur.execute("""
            CREATE TABLE if not exists AssetsTable
            (ID SERIAL, NameAsset TEXT(50), CurrentNonAsset TEXT(500), OriginalCost money,
             PurchaseDate date, Usefullife int, AssetStatus TEXT(50), CreationDate date)
             """)
    # Method To Create Expenses Table
    def ExpensesTable(self):
        cur.execute("""
            CREATE TABLE if not exists ExpensesTable
            (ID SERIAL, ExpenseName TEXT(50), ExpenseCategory TEXT(500), ExpenseAmount money, PaymentMode TEXT(500),
             TransactionDate date, Description TEXT(1000) )
             """)
    
    # Method To Create Liabilites Table
    def LiabilitiesTable(self):
        cur.execute("""
            CREATE TABLE if not exists LiabilitiesTable
            (ID SERIAL, NameLiability TEXT(50), CurrentNonLiability TEXT(500), OriginalValue money,
             EffectiveDate date, InterestRate int, LiabilityStatus TEXT(50), CreationDate date)
             """)

    # Method To Create Supplier/Customers Table
    def CustomersSuppliersTable(self):
        cur.execute("""
            CREATE TABLE if not exists CustomersSuppliersTable
            (ID SERIAL, Name TEXT(50), Location TEXT(500), Category TEXT(50),
             Email TEXT(50), Phone TEXT(50), CreationDate date)
             """)

    # All Transaction Table
    def TransactionTable(self):
        cur.execute("""
            CREATE TABLE if not exists TransactTable
            (ID SERIAL, ItemName TEXT(50), ItemQuantity int, UnitPrice money, ActionType TEXT(50), 
             TranasctionDate date, ItemMeasure TEXT(50), TotalValue money, Transactionescription TEXT(1000),SystemTransactDate date,CustomerSupplierName TEXT(50))
             """)
    # Create Other Transactions Tables
    def OtherTransactionTable(self,tablename):
        cur.execute("""
            CREATE TABLE if not exists {}
            (ID SERIAL, ItemName TEXT(50), ItemQuantity int, UnitPrice money, ActionType TEXT(50),
             TranasctionDate date, ItemMeasure TEXT(50), TotalValue money, Transactionescription TEXT(1000),SystemTransactDate date,CustomerSupplierName TEXT(50))
             """.format(tablename))

    # Method To View Data from Table (all tables)
    def ViewTable(self,tablename):
        Data = cur.execute('SELECT * FROM {}'.format(tablename)).fetchall()
        return Data

    # Method To select unique values from column (all tables)
    def SelectionFromTable(self,tablename,colName):
        NamesList = cur.execute("SELECT DISTINCT {} FROM {} ORDER BY {} DESC".format(colName,tablename,colName)).fetchall()
        Names = []
        for i in NamesList:
            Names.append(i[0])
        return Names

        # Method To select Ids of Transaction with 1 or more Stock Values (all tables)
    def SelectIDsFromTablewithQ(self, itemname):
        NamesList = cur.execute('''SELECT ID FROM StocksTable 
                                   WHERE ([ItemName] = ?)
                                   AND (ItemQuantity > 0)
                                   ''',(itemname,)).fetchall()
        Names = []
        for i in NamesList:
            Names.append(i[0])
        return Names
        
    # Method To select Data for edit/Update (all tables)
    def SelectDataPerID(self,tablename,colName,fil_ID):
        NamesList = cur.execute('SELECT * FROM {} WHERE {} = "{}" '.format(tablename,colName,fil_ID)).fetchall()
        return NamesList
    
    # Method To Delete Item in Table(All tables)
    def DeleteItem(self,tablename,refcol,refval):
        cur.execute('DELETE FROM {} WHERE {} = "{}" '.format(tablename,refcol,refval))
        conn.commit()
    
    # Method to calculate SUM based on Certain Value
    def Sum_Values(self,colVal,tablename,refcol,refval):
        sumdata = cur.execute('SELECT SUM("{}") FROM "{}" WHERE "{}" = "{}" '.format(colVal,tablename,refcol,refval)).fetchall()
        return sumdata
        
    
    # Method to calculate SUM of Closing Balance Value based on SD & ED
    def Sum_ClosingBal_Val(self):
        Bal = cur.execute('''SELECT SUM(TotalValue) FROM StocksTable''',).fetchall()[0][0]
        if Bal is None:
            return 0
        else:
            return Bal

     # Method to calculate SUM of Cost of Sales Value based on SD & ED
    def Sum_CostSales_Val(self,sd,ed):
        COGS = cur.execute('''SELECT SUM(TotalValue) FROM COGSTable
                                            WHERE ([TranasctionDate] between  ? and  ?)
                                            ''',(sd,ed)).fetchall()[0][0]
        if COGS is None:
            return 0
        else:
            return COGS

    # Method to calculate SUM of Operating Expenses based on SD & ED
    def Sum_OperatingExp_Val(self,sd,ed):
        Exp = cur.execute('''SELECT SUM(ExpenseAmount) FROM ExpensesTable
                                            WHERE ([TransactionDate] between  ? and  ?) and (ExpenseCategory = "Operating Expenses")
                                            ''',(sd,ed)).fetchall()[0][0]
        if Exp is None:
            return 0
        else:
            return Exp
    
    # Method to Select ID with the Recent Date from Given Table
    def Select_ID(self,colID,tablename,datecol,prnacol,prname):
        PrID = cur.execute('''SELECT "{}" FROM "{}" 
                              WHERE "{}" = (SELECT MAX("{}") FROM "{}" WHERE "{}" = "{}") 
                              '''.format(colID,tablename,datecol,datecol,tablename,prnacol,prname)).fetchall()
        return PrID
       
    # Method to calculate SUM All products based on Certain Value
    def Sum_Values_Bal(self,selcol, colVal,tablename):
        summarydata = cur.execute('''SELECT "{}",SUM(TotalValue), SUM("{}") as Total 
                                     FROM "{}" 
                                     GROUP BY "{}" 
                                     HAVING SUM("{}") > 0 
                                     ORDER BY Total DESC'''.format(selcol, colVal,tablename,selcol,colVal)).fetchall()
        return summarydata
    # Method to calculate SUM All Expenses based on Certain Value

    def Sum_Operating_Expenses(self,sd,ed):
        summarydata = cur.execute('''SELECT ExpenseName, SUM(ExpenseAmount) as Total 
                                     FROM ExpensesTable
                                     WHERE (TransactionDate between  ? and  ?) AND (ExpenseCategory = "Operating Expenses")
                                     GROUP BY ExpenseName 
                                     HAVING SUM(ExpenseAmount) > 0 
                                     ORDER BY Total DESC''',(sd,ed)).fetchall()
        return summarydata

    # Method to calculate SUM of SALES/TRANSACTION
    def Sum_Amount(self,Sale_Purchase,sd,ed):
        
        if Sale_Purchase == "Sale":
            try:
                sales = cur.execute('''SELECT SUM(TotalValue) FROM TransactTable
                                            WHERE ([ActionType] in ("Cash Sale","Credit Sale")) and 
                                            ([TranasctionDate] between  ? and  ?)
                                            ''',(sd,ed)).fetchall()[0][0]
                if sales is None:
                    return 0
                else:
                    return abs(sales)
            except TypeError: 
                pass
            
        elif Sale_Purchase == "Purchase":
            try:
                sum = cur.execute('''SELECT SUM(TotalValue) FROM TransactTable 
                                            WHERE ([ActionType] in ("Cash Purchase","Credit Purchase")) and 
                                            ([TranasctionDate] between  ? and  ?)
                                            ''',(sd,ed)).fetchall()[0][0]
                if sum is None:
                    return 0
                else:
                    return sum
            except TypeError:
                pass

    # Select Dates from Stocks Table for a given product ID
    def SelectDatesStocksTable(self,fil_ID):
        NamesList = cur.execute('SELECT SystemTransactDate FROM StocksTable WHERE ID = ? ',(fil_ID,)).fetchall()
        return NamesList
    
    # Select Data from Stocks Table where Q > 0
    def SelectClosingStocks(self):
        Data = cur.execute('SELECT * FROM StocksTable WHERE ItemQuantity > 0 ').fetchall()
        return Data

     # Method To select unique values from column based on value of other column (all tables)
    def Selection_as_perCol(self,seleCol,tablename,refCol,refval):
        Data = cur.execute('''SELECT "{}" FROM "{}" WHERE "{}" = "{}" '''.format(seleCol,tablename,refCol,refval)).fetchall()
        return Data

    # Method to Create ACCOUNTS
    def CreateAccount(self,accountname):
        cur.execute("""
            CREATE TABLE if not exists {}
            (ID SERIAL,TranasctionDate date, TransactionDetails TEXT(500), DebtAmount money, CreditAmount money,
             BookBalance money,CustomerSupplierName TEXT(50), SystemTransactDate date)
             """.format(accountname))
    
    # Method to Add Transaction into Account
    def AddTransAccount(self,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                             BookBalance,CustomerSupplierName, SystemTransactDate):
        cur.execute('''INSERT INTO "{}" VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'''
                   .format(accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                             BookBalance,CustomerSupplierName, SystemTransactDate))
        conn.commit()
    # Method to calculate SUM of DR/CR Transactions in Accounts
    def Sum_DR_CR(self,refcol,accountname):
        sum_val = cur.execute('SELECT SUM("{}") FROM "{}" as Total'.format(refcol,accountname)).fetchall()[0][0]
        if sum_val is None:
            return 0
        else:
            return sum_val
  
# Function to edit Data in Transaction Table
def EditTransactionFunc(new_itemname,new_itemq,new_unitprice,new_actiontype,new_itemmeasure,new_descrip,TotalValue,fil_ID):
    sqlite_update_query = '''Update TransactTable set ItemName = ?, ItemQuantity = ?,UnitPrice = ?, ActionType = ?,ItemMeasure = ?, Transactionescription = ?, TotalValue = ? where id = ?'''
    columnValues = (new_itemname,new_itemq,new_unitprice,new_actiontype,new_itemmeasure,new_descrip,TotalValue,fil_ID)
    cur.execute(sqlite_update_query, columnValues)
    conn.commit()


# Function to edit Product
def EditProductFunc(New_Productname,New_ProductMeasure,New_Description,fil_ID):
    sqlite_update_query = '''Update ItemTable set ItemName = ?, ItemMeasure = ?,Descriptions = ? where ID = ?'''
    columnValues = (New_Productname,New_ProductMeasure,New_Description,fil_ID)
    cur.execute(sqlite_update_query, columnValues)
    conn.commit()

# Function to edit TransactionType
def EditTransTypeFunc(New_TransTypeName,New_Trans_Category,New_State_part,fil_ID):
    sqlite_update_query = '''Update TransactionTypeTable set ActionName = ?, TransactionCategory = ?,StatePart = ? where ID = ?'''
    columnValues = (New_TransTypeName,New_Trans_Category,New_State_part,fil_ID)
    cur.execute(sqlite_update_query, columnValues)
    conn.commit()

# Function to Add Transaction
def AddTransaction(a,b,c,d,e,f,g,h,i,j,k):
        cur.execute('INSERT INTO TransactTable VALUES (?,?,?,?,?,?,?,?,?,?,?)',(a,b,c,d,e,f,g,h,i,j,k))
        conn.commit()

# Function to Edit Data in Other Transaction Table
def EditOtherTransactionFunc(tablename,new_itemname,new_itemq,new_unitprice,new_actiontype,new_itemmeasure,new_descrip,TotalValue,fil_ID):
    cur.execute('''Update "{}" set ItemName = "{}", ItemQuantity = "{}",UnitPrice = "{}", ActionType = "{}",ItemMeasure = "{}",Transactionescription = "{}", 
    TotalValue = "{}" where ID = "{}" '''.format(tablename,new_itemname,new_itemq,new_unitprice,new_actiontype,new_itemmeasure,new_descrip,TotalValue,fil_ID))
    conn.commit()

#Function to Edit Update Stocks after selling product
def UpdateTransaAfterSaleFunc(tablename,bal_itemq,cur_unitprice,UpdatedTotalValue,Rec_ID):
    cur.execute('''Update "{}" set ItemQuantity = "{}",UnitPrice = "{}",
                  TotalValue = "{}" where ID = "{}" '''.format(tablename,bal_itemq,cur_unitprice,UpdatedTotalValue,Rec_ID))
    conn.commit()

#Function to Remove Stock Balances from Transactionsafter selling product
def UpdateRemoveBalances(tablename,prodname,Rec_ID):
    cur.execute('''Update "{}" set ItemQuantity = 0,
                  TotalValue = 0 where (ItemName = "{}" and ID != "{}") '''.format(tablename,prodname,Rec_ID))
    conn.commit()

# Function to Add Transaction to other Tables (Sales/Stocks)
def AddTransactionOtherTable(tablename,a,b,c,d,e,f,g,h,i,j):
        cur.execute('INSERT INTO "{}" VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(tablename,a,b,c,d,e,f,g,h,i,j))
        conn.commit()

# Function to Add Product
def AddProductFunc(a,b,c,d,e):
        cur.execute('INSERT INTO ItemTable VALUES (?,?,?,?,?)',(a,b,c,d,e))
        conn.commit()

# Function to Transaction Type into Table
def AddTransTypeFunc(a,b,c,d,e):
        cur.execute('INSERT INTO TransactionTypeTable VALUES (?,?,?,?,?)',(a,b,c,d,e))
        conn.commit()

# Function to check whether a value is number
def isnumber(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

#Function to Update Closing Stock in Stocks Table
def UpdateClosingCOGS(new_itemq,New_TotalValue,TransactDateID):
    cur.execute('''Update StocksTable set  ItemQuantity = ?,TotalValue = ? 
                   where SystemTransactDate = ? ''',(new_itemq,New_TotalValue,TransactDateID))
    conn.commit()

#Function to Add Transaction in COGS Table
def AddTransactionCOGSTable(ID, ItemName, ItemQuantity, UnitPrice, ActionType,TranasctionDate, ItemMeasure, TotalValue, Transactionescription,SystemTransactDate):
        cur.execute('INSERT INTO COGSTable VALUES (?,?,?,?,?,?,?,?,?,?)',(ID, ItemName, ItemQuantity, UnitPrice, ActionType,TranasctionDate, ItemMeasure, TotalValue, Transactionescription,SystemTransactDate))
        conn.commit()

#Function to Add Transaction in Expenses Table
def AddExpensesTable(ID,ExpenseName, ExpenseCategory,ExpenseAmount, PaymentMode,TransactionDate, Description):
        cur.execute('INSERT INTO ExpensesTable VALUES (?,?,?,?,?,?,?)',(ID,ExpenseName, ExpenseCategory,ExpenseAmount, PaymentMode,TransactionDate, Description))
        conn.commit()

#Function to Create ClosingStockBalance Tables
def ClosingStockBalTable():
    cur.execute("""
            CREATE TABLE if not exists ClosingStockBalTable
            (ID SERIAL, TranasctionDate date, SystemTransDate date,ClosingBalance money)
             """)

# Function to Add Balance to Closing Stock Table
def AddClosingStock(ID,TranasctionDate,SystemTransDate,ClosingBalance):
        cur.execute('INSERT INTO ClosingStockBalTable VALUES (?,?,?,?)',(ID,TranasctionDate,SystemTransDate,ClosingBalance))
        conn.commit()

#Function to Add the Closing Balance
def StoreClosingStock(id):
    ClosingBalance = Business.Sum_ClosingBal_Val(Business)
    ID = id
    TranasctionDate = datetime.now().strftime("%Y-%m-%d")
    SystemTransDate = datetime.now()
    AddClosingStock(ID,TranasctionDate,SystemTransDate,ClosingBalance)

# Function to select a closing stock of a day
def DailyClosingStock(closingdate):
        Cl_Bal = cur.execute('''SELECT ClosingBalance FROM ClosingStockBalTable 
                              WHERE SystemTransDate = (SELECT MAX(SystemTransDate) FROM ClosingStockBalTable WHERE TranasctionDate = ? ) 
                              ''',(closingdate,)).fetchall()
        return Cl_Bal


# Function to select a Account Balance of a day
def DailyAccountBalance(accountname,closingdate):
        Cl_Bal = cur.execute('''SELECT BookBalance FROM "{}" 
                                 WHERE SystemTransactDate = (SELECT MAX(SystemTransactDate) FROM "{}" WHERE TranasctionDate = "{}" ) 
                              '''.format(accountname,accountname,closingdate)).fetchall()
        return Cl_Bal

# Function to Add Customer/Supplier
def AddCustomerSupplier(a,b,c,d,e,f,g):
        cur.execute('''INSERT INTO CustomersSuppliersTable VALUES ('{}','{}','{}','{}','{}','{}','{}')'''.format(a,b,c,d,e,f,g))
        conn.commit()

#================================================================================================================================#
#Function to check if the Cash Account has Balance
def CashAccount_Bal ():
    DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","CashAccount")
    CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","CashAccount")
    return DRBalance - CRBalance

#Function to Record Cash Receipt in Cash Account
def AddCash_Receipt(Value,id):
    accountname = "CashAccount"
    ID = id
    TranasctionDate = datetime.today().strftime("%Y-%m-%d")
    TransactionDetails = f"Cash Receipt {float(Value):,.0f} on {TranasctionDate}"
    DebtAmount = Value
    CreditAmount = 0
    DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","CashAccount")
    Cul_DRBalance = DRBalance + DebtAmount
    CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","CashAccount")
    Cul_CRBalance = CRBalance + CreditAmount
    BookBalance = Cul_DRBalance - Cul_CRBalance
    CustomerSupplierName = ""
    SystemTransactDate = datetime.today()
    return Business.AddTransAccount(Business,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                                         BookBalance,CustomerSupplierName, SystemTransactDate)

#Function to Record Cash Payment in Cash Account
def PayCash_Record(Value,id):
    accountname = "CashAccount"
    ID = id
    TranasctionDate = datetime.today().strftime("%Y-%m-%d")
    TransactionDetails = f"Cash Payment {float(Value):,.0f} on {TranasctionDate}"
    DebtAmount = 0
    CreditAmount = Value
    DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","CashAccount")
    Cul_DRBalance = DRBalance + DebtAmount
    CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","CashAccount")
    Cul_CRBalance = CRBalance + CreditAmount
    BookBalance = Cul_DRBalance - Cul_CRBalance
    CustomerSupplierName = ""
    SystemTransactDate = datetime.today()
    return Business.AddTransAccount(Business,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                                         BookBalance,CustomerSupplierName, SystemTransactDate)
# CREATE TABLE if not exists ItemTable
#             (ID SERIAL, ItemName TEXT(50), ItemMeasure TEXT(500),Descriptions TEXT(1000), CreationDate date)

# Auto Product Unit Measure
def Auto_ProductUnit(productName):
    Unit = Business.Selection_as_perCol(self=Business,seleCol="ItemMeasure",tablename ="ItemTable",refCol="ItemName",refval=productName)[0][0]
    return Unit

# Transactions Input Form
def TransactionInputForm():
    # Run Picklists 
    ProductPickList = Business.SelectionFromTable(self=Business,tablename="ItemTable",colName="ItemName")
    ProductMeasure = Business.SelectionFromTable(self=Business,tablename="ItemTable",colName="ItemMeasure")
    CustomersSupplierList = Business.SelectionFromTable(self=Business,tablename="CustomersSuppliersTable",colName="Name")
    
    # Record Receivable Amount after sale on Credit
    def UpdateReceivable_Sale():
        accountname = "ReceivablesAccount"
        ID = id
        TranasctionDate = TransDateNotime
        TransactionDetails = f"Receivable of {TotalValue:,.0f} for {CustomerSupplier} on {TranasctionDate}"
        DebtAmount = TotalValue
        CreditAmount = 0
        DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","ReceivablesAccount")
        Cul_DRBalance = DRBalance + DebtAmount
        CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","ReceivablesAccount")
        Cul_CRBalance = CRBalance + CreditAmount
        BookBalance = Cul_DRBalance - Cul_CRBalance
        CustomerSupplierName = CustomerSupplier
        SystemTransactDate = TrnsDate
        return Business.AddTransAccount(Business,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                                         BookBalance,CustomerSupplierName, SystemTransactDate)
    
    # Record Payable Amount after Purchase on Credit
    def UpdatePayable_Purchase():
        accountname = "PayablesAccount"
        ID = id
        TranasctionDate = TransDateNotime
        TransactionDetails = f"Payable of {TotalValue:,.0f} for {CustomerSupplier} on {TranasctionDate}"
        DebtAmount = 0
        CreditAmount = TotalValue
        DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","PayablesAccount")
        Cul_DRBalance = DRBalance + DebtAmount
        CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","PayablesAccount")
        Cul_CRBalance = CRBalance + CreditAmount
        BookBalance = Cul_CRBalance - Cul_DRBalance 
        CustomerSupplierName = CustomerSupplier
        SystemTransactDate = TrnsDate
        return Business.AddTransAccount(Business,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                                         BookBalance,CustomerSupplierName, SystemTransactDate)

    # Function to Check if the balance of product units do not exceed the available balance
    def Check_Bal():
        Bal = Business.Sum_Values(self=Business,colVal="ItemQuantity",tablename="TransactTable",refcol="ItemName",refval=Itemname[0])[0][0]
        if Bal is None:
            return 0
        else:
            return Bal

    # Func to update Stocks Table after selling products
    def UpdateStocks_FIFO(Item_name,ItemQ,id):
        # 1. Ids
        ProdIDs = Business.SelectIDsFromTablewithQ(Business,Item_name)    
        # 2. dates
        DateList = []
        for id in ProdIDs:
            IndDate = Business.SelectDatesStocksTable(Business,fil_ID =id)[0]
            DateList.append(IndDate[0])        
        DateList.sort(reverse=False)
        # 3. Prices & Sold Amount for each Transaction
        def COGSUpdate():
            # COGS Inputs.....
            ID = id
            ItemName = Values[1]
            ItemQuantity = amount-amountBal
            UnitPrice = Values[3]
            ActionType = "Cost of Sales"
            TranasctionDate = datetime.now().strftime("%Y-%m-%d")
            ItemMeasure = Values[6]
            TotalValue = (amount-amountBal) * Values[3]
            Transactionescription = f"Cost of Sales for: {Values[1]}"
            SystemTransactDate = datetime.now()
            return AddTransactionCOGSTable(ID, ItemName, ItemQuantity, UnitPrice, ActionType,TranasctionDate, ItemMeasure, TotalValue, Transactionescription,SystemTransactDate)

        sellQ_Bal = ItemQ
        amountBal = 0
        
        for dats in DateList: 
            Values = Business.SelectDataPerID(self=Business,tablename="StocksTable",colName="SystemTransactDate",fil_ID=dats)[0]
            amount, price = Values[2],Values[3]
            
            if amount < ItemQ:
                if sellQ_Bal == 0:
                    break
                else:
                    if amount >= sellQ_Bal:
                        amountBal = amount - sellQ_Bal
                        sellQ_Bal = 0
                        UpdateClosingCOGS(new_itemq=amountBal,New_TotalValue = amountBal * price,TransactDateID =dats)
                        COGSUpdate()
                              
                    else:
                        sellQ_Bal -= amount
                        amountBal = 0
                        UpdateClosingCOGS(new_itemq=amountBal,New_TotalValue = amountBal * price,TransactDateID =dats)
                        COGSUpdate() 

            elif amount >= ItemQ:
                amountBal = amount - ItemQ
                sellQ_Bal = 0
                UpdateClosingCOGS(new_itemq=amountBal,New_TotalValue = amountBal * price,TransactDateID =dats)
                COGSUpdate()
                break
    
    with st.form("TransactionInput",clear_on_submit=True):
        fil1,fil2,fil3 = st.columns(3)
        fil4,fil5,fil6 = st.columns(3)

        TransTypeList = ["Credit Purchase","Credit Sale","Cash Purchase","Cash Sale"]

        Itemname = fil1.multiselect("Product Name",ProductPickList)
        ItemQ= fil2.text_input("Product Quantity")
        UnitPrice = fil3.text_input("Product Unit Price")
        ActionType = fil4.multiselect("Transaction Type",TransTypeList)
        ItemMeasure = fil5.multiselect("Product Unit Measure",ProductMeasure)
        CustomerSupplier = fil6.multiselect("Customer/Supplier Name",CustomersSupplierList)
        description = st.text_area("Transaction Description")
        subbtn = st.form_submit_button("Post Transaction")

        if subbtn:

            Item_name = Itemname[0]
            #Check if all fields are completed
            if len(Itemname) == 1 and len(ItemQ) > 0 and len(UnitPrice) > 0 and len(ActionType) == 1 and len(ItemMeasure) == 1 and len(description) > 0 and len(CustomerSupplier) == 1 :
                
                 # check if numbers are filled and not TEXT
                if isnumber(num=ItemQ) and isnumber(num=UnitPrice):
                    rand = random.randint(10,100000)
                    TrnsDate = datetime.now()
                    TransDateNotime = datetime.now().strftime("%Y-%m-%d")
                            
                    UnitPrice = float(UnitPrice)
                    ItemQ = float(ItemQ)
                    ItemMeasure = Auto_ProductUnit(productName=Item_name)

                    TotalValue = float(UnitPrice) * float(ItemQ)
                    id = f"""{str(TrnsDate)}/Product={Item_name}/Price={UnitPrice:,.0f}/Q={ItemQ:,.0f}
                                /Trans={ActionType[0]}/id={str(rand)}/Value= {TotalValue:,.0f}"""

                    if "Credit" in ActionType[0]  and len(CustomerSupplier) != 1:
                        st.warning(f"Since the transaction is: {ActionType[0]}! Record the name of Customer or Supplier Above!")     
                    else:
                        CustomerSupplier = CustomerSupplier[0].replace("['", "").replace("']", "")
                        if "Sale" in ActionType[0]:

                            AvailProductsStocks = Business.SelectionFromTable(self=Business,tablename="StocksTable",colName="ItemName")
                            if Item_name in AvailProductsStocks:
                                        
                            # Check if the balance of product units do not exceed the available balance
                                TotalBal = Check_Bal()       
                                if float(ItemQ) <= TotalBal:
                                    
                                    AddTransaction(a=id,b=Item_name,c= -abs(ItemQ),d=UnitPrice,e=ActionType[0],
                                                f=TransDateNotime,g=ItemMeasure,h= -abs(TotalValue),i=description,j=TrnsDate,k=CustomerSupplier[0])
                                    st.success(f" The {ActionType[0]} for {Item_name} has been recorded successful!")
                                    st.balloons()

                                    AddTransactionOtherTable(tablename="SalesTable",a=id,b=Item_name,c=ItemQ,d=UnitPrice,e=ActionType[0],
                                                            f=TransDateNotime,g=ItemMeasure,h=TotalValue,i=description,j=TrnsDate)
                                    UpdateStocks_FIFO(Item_name,ItemQ,id)
                                    StoreClosingStock(id=id)
                                    

                                    # Receivable Updates
                                    if "Credit" in ActionType[0]:
                                        UpdateReceivable_Sale()
                                     # Cash Updates
                                    elif "Cash" in ActionType[0]:
                                        AddCash_Receipt(Value=TotalValue,id=id)
                                        
                                elif float(ItemQ) > TotalBal and TotalBal > 0:
                                    st.warning(f"You can not sell {int(ItemQ)} units for the Product ({Itemname[0]}). The maximum possible selling amount as per available balance is  {int(TotalBal)} units only")
                                elif float(ItemQ) > TotalBal and TotalBal <= 0:
                                    st.warning(f"Sorry! You can not sell {int(ItemQ)} units of {Itemname[0]} for now as the product has no balance!")
                            else:
                                st.warning(f"Sorry! There is no stock for the Product ({Itemname[0]}) you are trying to sell.")
                                    
                                    #Business.DeleteItem(self=Business,tablename="StocksTable",refcol="ItemName",refval=Item_name)
                    
                        elif "Purchase" in ActionType[0]:
                            def PurchaseUpdates():
                                AddTransaction(a=id,b=Item_name,c= ItemQ,d=UnitPrice,e=ActionType[0],
                                            f=TransDateNotime,g=ItemMeasure,h= TotalValue,i=description,j=TrnsDate,k=CustomerSupplier[0])
                                st.success(f" The {ActionType[0]} for {Item_name} has been recorded successful!")
                                st.snow()

                                AddTransactionOtherTable(tablename="StocksTable",a=id,b=Item_name,c=ItemQ,d=UnitPrice,e=ActionType[0],
                                                            f=TransDateNotime,g=ItemMeasure,h=TotalValue,i=description,j=TrnsDate)
                               
                            # Payables Updates
                            if "Credit" in ActionType[0]:
                                UpdatePayable_Purchase()
                                PurchaseUpdates()
                                StoreClosingStock(id=id) 

                            # Cash Purchase Updates in Cash Account   
                            elif "Cash" in ActionType[0]:
                                if CashAccount_Bal() >= TotalValue:
                                    PayCash_Record(Value=TotalValue,id=id)
                                    PurchaseUpdates()
                                    StoreClosingStock(id=id) 
                                else:
                                    st.warning(f"There is Insufficient Cash! The available Balance is:: {CashAccount_Bal():,.0f}.")

                else:
                    st.warning("Product Quantity and Product Unit Price should be numbers. Please correct & repost!")   
            else:
                st.warning("⚠️To proceed make sure that all the fields in the form above are completed")

# Transaction DELETE Form
def TransactionDeleteForm():
    Transact_id = Business.SelectionFromTable("Business","TransactTable","ID")
   
    ProductPickList = Business.SelectionFromTable(self=Business,tablename="ItemTable",colName="ItemName")
    # ProductMeasure = Business.SelectionFromTable(self=Business,tablename="ItemTable",colName="ItemMeasure")
    # TransTypeList = Business.SelectionFromTable(self=Business,tablename="TransactionTypeTable",colName="ActionName")
    # TransTypeList = ["Credit Purchase","Credit Sale","Cash Purchase","Cash Sale"]

    Transaction = st.multiselect("Pick Transaction You Want to DELETE",Transact_id)
    
    if len (Transaction) == 1:
        FirstValue = Transaction[0]
        data = Business.SelectDataPerID("Business","TransactTable","ID",FirstValue)
        
        fil_ID = data[0][0]
        sel_itemname = data[0][1]
        sel_itemq = data[0][2]
        sel_unitprice = data[0][3]
        sel_actiontype = data[0][4]
        sel_itemmeasure = data[0][6]
        sel_descrip = data[0][8]
        sel_customerSupp = data[0][10]

        if sel_itemname in ProductPickList:
        # A form to edit Transactions details
            with st.form("TransactionDelete",clear_on_submit=False):

                fil1_des,fil1,fil2_des,fil2,fil3_des,fil3 = st.columns(6)
                fil4_des,fil4,fil5_des,fil5,fil6_des,fil6 = st.columns(6)
                fil7_des,fil7 = st.columns([2,4])

                fil1_des.info("Product Name")
                fil1.success(f"{sel_itemname}")

                fil2_des.info("Product Quantity")
                fil2.success(f"{abs(sel_itemq)}")

                fil3_des.info("Price")
                fil3.success(f"{sel_unitprice}")

                fil4_des.info("Transaction Type")
                fil4.success(f"{sel_actiontype}")

                fil5_des.info("Measure")
                fil5.success(f"{sel_itemmeasure}")

                fil6_des.info("Cust/Supplier")
                fil6.success(f"{sel_customerSupp}")

                fil7_des.info("Transaction Description")
                fil7.success(f"{sel_descrip}")
    
                del_btn = st.form_submit_button("Click to DELETE the Transaction Above")

                if del_btn:
                    Business.DeleteItem(self=Business,tablename="TransactTable",refcol="ID",refval=fil_ID)
                    Business.DeleteItem(self=Business,tablename="SalesTable",refcol="ID",refval=fil_ID)
                    Business.DeleteItem(self=Business,tablename="StocksTable",refcol="ID",refval=fil_ID)
                    
                    Business.DeleteItem(self=Business,tablename="COGSTable",refcol="ID",refval=fil_ID)
                    Business.DeleteItem(self=Business,tablename="ReceivablesAccount",refcol="ID",refval=fil_ID)
                    Business.DeleteItem(self=Business,tablename="CashAccount",refcol="ID",refval=fil_ID)
                    Business.DeleteItem(self=Business,tablename="PayablesAccount",refcol="ID",refval=fil_ID)
                    Business.DeleteItem(self=Business,tablename="ClosingStockBalTable",refcol="ID",refval=fil_ID)

                    st.warning(f"The Transaction with product: {sel_itemname} has been DELETED succesfuly!")
        else:
            st.warning(f"Transaction you are trying to DELETE contain a product ({sel_itemname}) which is not in our database! Add the product before you proceed")


# Add PRODUCT Function
def AddProductForm():
    with st.form("ProductAdd",clear_on_submit=True):
        fil1,fil2 = st.columns(2)
        
        Productname= fil1.text_input("Product Name")
        ProductMeasure= fil2.text_input("Product Measure(Unit)")
        Description = st.text_area("Product Descriptions")
        subbtn = st.form_submit_button("Submit")
        if subbtn:

            if len(Productname) > 0 and len(ProductMeasure) > 0 and len(Description) > 0:

                ProductPickList = Business.SelectionFromTable(self=Business,tablename="ItemTable",colName="ItemName")
                products_list_cap = [product.capitalize() for product in ProductPickList]
                new_product_cap = Productname.capitalize()
 
                if new_product_cap in products_list_cap:
                   st.info(f"The product ( {Productname}) you are trying to create is already Created! Please create new product.")

                else:
                    rand = random.randint(10,100000)
                    CreationDate = datetime.now()
                    id = str(CreationDate) + "/"+ Productname + "/" + str(ProductMeasure) + "/"+ str(rand)
                    AddProductFunc(a=id,b=Productname,c=ProductMeasure,d=Description,e=CreationDate)
                    st.success(f" Congratulation! An item: {Productname} has been successful created in Database!")
            else:
                st.warning("⚠️Please complete all the fields above, before you proceed")
                

# Product Edit Form
def ProductEditForm():

    ProductPickList = Business.SelectionFromTable(self=Business,tablename="ItemTable",colName="ItemName")
   
    Products = st.multiselect("Pick Product to Edit",ProductPickList)
    if len (Products) == 1:
        FirstValue = Products[0]
        data = Business.SelectDataPerID("Business","ItemTable","ItemName",FirstValue)
  
        fil_ID = data[0][0]
        sel_itemname = data[0][1]
        sel_ItemMeasure = data[0][2]
        sel_Descriptions = data[0][3]
     
       # A form to edit Product details
        with st.form("ProductEdit",clear_on_submit=True):
            fil1,fil2 = st.columns(2)
                
            New_Productname= fil1.text_input("Product Name",value=sel_itemname)
            New_ProductMeasure= fil2.text_input("Product Measure(Unit)",value=sel_ItemMeasure)
            New_Description = st.text_area("Product Descriptions",value=sel_Descriptions)

            subbtn = st.form_submit_button("Click to UPDATE the Product Above")

            if subbtn:
                    
                if len(New_Productname) > 0 and len(New_ProductMeasure) > 0 and len(New_Description) >0:
                        
                    sel_list = [sel_itemname,sel_ItemMeasure,sel_Descriptions]
                    new_list = [New_Productname,New_ProductMeasure,New_Description]
                    
                    if collections.Counter(sel_list) != collections.Counter(new_list):
                
                        EditProductFunc(New_Productname,New_ProductMeasure,New_Description,fil_ID)     
                        st.success(f"Congratulations! You have successful updated Product:: {sel_itemname}")
                            
                    else:
                        st.error(f"No changes commited on Product for:: {sel_itemname}")
                else:
                    st.warning("⚠️To proceed make sure that all the fields in the form above are completed!")   
        
# Product Delete Form
def ProductDeleteForm():

    ProductPickList = Business.SelectionFromTable(self=Business,tablename="ItemTable",colName="ItemName")
   
    Products = st.multiselect("Pick Product You Want to Delete",ProductPickList)
    if len (Products) == 1:
        FirstValue = Products[0]
        data = Business.SelectDataPerID("Business","ItemTable","ItemName",FirstValue)
  
        fil_ID = data[0][0]
        sel_itemname = data[0][1]
        sel_ItemMeasure = data[0][2]
        sel_Descriptions = data[0][3]
     
       # A form to edit Product details
        with st.form("ProductDelete",clear_on_submit=True):
            fil1,fil2 = st.columns(2)
                
            fil1.text_input("Product Name",value=sel_itemname,disabled=True)
            fil2.text_input("Product Measure(Unit)",value=sel_ItemMeasure,disabled=True)
            st.text_area("Product Descriptions",value=sel_Descriptions,disabled=True)

            subbtn = st.form_submit_button("Click to DELETE the Product Above")

            if subbtn:
                Business.DeleteItem(self=Business,tablename="ItemTable",refcol="ID",refval=fil_ID)
                st.warning(f"The product: {sel_itemname} has been DELETED succesfuly!")   

# List for Transaction Categories
List_Trans_Category = ["Drawings","Sales Related Expenses","Operating Expenses","Purchases Related Expenses"]
# Add Transaction Type Func
def AddTransactionTypeForm():
    with st.form("Transaction_Type_Add",clear_on_submit=True):
        fil1,fil2,fil3 = st.columns(3)

        TransTypeName= fil1.text_input("Name of the Transaction Type")
        Trans_Category= fil2.multiselect("Transaction Category",List_Trans_Category)
        State_part = fil3.multiselect("Financial Statement Part",["Assets","Liability","Income","Expenses","Drawings"])

        subbtn = st.form_submit_button("Submit")
        if subbtn:

            if len(TransTypeName) > 0 and len(Trans_Category) == 1 and len(State_part) == 1:

                TransTypeList = Business.SelectionFromTable(self=Business,tablename="TransactionTypeTable",colName="ActionName")
                TransTyp_list_cap = [product.capitalize() for product in TransTypeList]
                new_transtype_cap = TransTypeName.capitalize()
 
                if new_transtype_cap in TransTyp_list_cap:
                   st.info(f"The Transaction Type ( {TransTypeName}) you are trying to create is already Created! Please create new Transaction Type.")

                else:
                    rand = random.randint(10,100000)
                    CreationDate = datetime.now()
                    id = str(CreationDate) + "/"+ TransTypeName + "/" + str(Trans_Category[0]) + str(State_part[0]) +"/"+ str(rand)

                    AddTransTypeFunc(a=id,b=TransTypeName,c=Trans_Category[0],d=State_part[0],e=CreationDate)

                    st.success(f" Congratulation! Transaction Type: {TransTypeName} has been successful created in Database!")

            else:
                st.warning("⚠️Please complete all the fields above, before you proceed")


# Edit Transaction Type Form
def EditTransactionTypeForm():

    TransTypePickList = Business.SelectionFromTable(self=Business,tablename="TransactionTypeTable",colName="ActionName")
    TransTypes = st.multiselect("Pick Transaction Type You Want to Edit",TransTypePickList)

    if len (TransTypes) == 1:
        FirstValue = TransTypes[0]

        TransTypeData = Business.SelectDataPerID("Business","TransactionTypeTable","ActionName",FirstValue)

        fil_ID = TransTypeData[0][0]
        sel_name = TransTypeData[0][1]
        sel_category = TransTypeData[0][2]
        sel_StatePart = TransTypeData[0][3]
     
       # A form to edit Product details
        with st.form("Transaction_Type_Edit",clear_on_submit=True):
            fil1,fil2,fil3 = st.columns(3)
            
            New_TransTypeName= fil1.text_input(label="Name of the Transaction Type",value=sel_name)
            New_Trans_Category= fil2.multiselect(label="Transaction Category",options=List_Trans_Category,default=sel_category)
            New_State_part = fil3.multiselect(label="Financial Statement Part",options=["Assets","Liability","Income","Expenses","Drawings"],default=sel_StatePart)

            subbtn = st.form_submit_button("Click to UPDATE the Transaction Type Above")

            if subbtn:
                    
                if len(New_TransTypeName) > 0 and len(New_Trans_Category) == 1 and len(New_State_part)==1:
                        
                    sel_list = [sel_name,sel_category,sel_StatePart]
                    new_list = [New_TransTypeName,New_Trans_Category[0],New_State_part[0]]
                    
                    if collections.Counter(sel_list) != collections.Counter(new_list):
                
                        EditTransTypeFunc(New_TransTypeName,New_Trans_Category[0],New_State_part[0],fil_ID)     
                        st.success(f"Congratulations! You have successful updated Transaction Type:: {sel_name}")
                            
                    else:
                        st.error(f"No changes commited on Transaction Type:: {sel_name}")
                else:
                    st.warning("⚠️To proceed make sure that all the fields in the form above are completed!")   


# Delete Transaction Type Form
def DeleteTransactionTypeForm():

    TransTypePickList = Business.SelectionFromTable(self=Business,tablename="TransactionTypeTable",colName="ActionName")
    TransTypes = st.multiselect("Pick Transaction Type You Want to Edit",TransTypePickList)

    if len (TransTypes) == 1:
        FirstValue = TransTypes[0]

        TransTypeData = Business.SelectDataPerID("Business","TransactionTypeTable","ActionName",FirstValue)

        fil_ID = TransTypeData[0][0]
        sel_name = TransTypeData[0][1]
        sel_category = TransTypeData[0][2]
        sel_StatePart = TransTypeData[0][3]
     
       # A form to Delete Transaction Type
        with st.form("Transaction_Type_Delete",clear_on_submit=True):
            fil1,fil2,fil3 = st.columns(3)
            
            fil1.text_input(label="Name of the Transaction Type",value=sel_name,disabled=True)
            fil2.multiselect(label="Transaction Category",options=List_Trans_Category,default=sel_category,disabled=True)
            fil3.multiselect(label="Financial Statement Part",options=["Assets","Liability","Income","Expenses","Drawings"],default=sel_StatePart,disabled=True)

            subbtn = st.form_submit_button(f"Click to DELETE the Transaction Type ({sel_name}) Above")

            if subbtn:
                Business.DeleteItem(self=Business,tablename="TransactionTypeTable",refcol="ID",refval=fil_ID)
                st.warning(f"The Transaction Type: {sel_name} has been DELETED succesfuly!") 


# Add Expenses Func

# Def Auto Expense Category
def Auto_ExpenseCategory(ExpenseName):
    TransCategory = Business.Selection_as_perCol(self=Business,seleCol="TransactionCategory",tablename ="TransactionTypeTable",refCol="ActionName",refval=ExpenseName)[0][0]
    return TransCategory

def AddExpensesForm():

    # Record PayableExpenses
    def PayableExpenses_Record(id):
        accountname = "PayablesAccount"
        ID = id
        TranasctionDate = datetime.today().strftime("%Y-%m-%d")
        TransactionDetails = f"Record of Payable of {ExpenseAmount:,.0f} for {ExpenseName} on {TranasctionDate}"
        DebtAmount = 0
        CreditAmount = ExpenseAmount
        DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","PayablesAccount")
        Cul_DRBalance = DRBalance + DebtAmount
        CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","PayablesAccount")
        Cul_CRBalance = CRBalance + CreditAmount
        BookBalance = Cul_CRBalance - Cul_DRBalance
        CustomerSupplierName = SupllierName
        SystemTransactDate = datetime.today()
        return Business.AddTransAccount(Business,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                                         BookBalance,CustomerSupplierName, SystemTransactDate)

    TransType = Business.SelectionFromTable(self=Business,tablename="TransactionTypeTable",colName="ActionName")
    TransCategory = Business.SelectionFromTable(self=Business,tablename="TransactionTypeTable",colName="TransactionCategory")

    with st.form("Expenses",clear_on_submit=True):
        fil1,fil2,fil3 = st.columns(3)
        fil4,fil5 = st.columns(2)

        ExpenseName = fil1.multiselect("Type of Expense",TransType)
        ExpenseCategory = fil2.multiselect("Transaction Category",TransCategory)
        ExpenseAmount = fil3.text_input("Expenses Amount")
        PaymentMode = fil4.multiselect("Payment Mode",["Cash","Credit"])
        SupllierName = fil5.text_input("Name of Supplier")
        Description = st.text_area("Description of Expenses")
        subbtn = st.form_submit_button("Record Expenses")

        if subbtn:

            if len(ExpenseName)  == 1 and len(ExpenseCategory) == 1 and len(PaymentMode) == 1 and len(ExpenseAmount)  > 0:
             
                if PaymentMode[0] == "Credit" and len(SupllierName) < 1:
                    st.warning(f"Since this is a Credit Expenses! Record the name of Supplier Above before you proceed!") 
                else:
                    if isnumber(ExpenseAmount):
                        rand = random.randint(10,100000)
                        TransactionDate = datetime.now().strftime("%Y-%m-%d")

                        ExpenseCategory = Auto_ExpenseCategory(ExpenseName[0])
                        ID = str(TransactionDate) + "/"+ ExpenseName[0] + "/" + str(ExpenseCategory) + str(ExpenseAmount) +"/"+ str(rand) + str(PaymentMode[0])
                        ExpenseName = ExpenseName[0]
                        PaymentMode = PaymentMode[0]
                        ExpenseAmount = float(ExpenseAmount)
                        
                        def AddExpense():
                            AddExpensesTable(ID,ExpenseName, ExpenseCategory,ExpenseAmount, PaymentMode,TransactionDate, Description)
                            st.success(f" Congratulation! The Expense: {ExpenseName} ==> {ExpenseAmount:,.0f} has been successful Recorded in Database!")
                            
                        if PaymentMode == "Cash":
                            if CashAccount_Bal() >= ExpenseAmount:
                                    PayCash_Record(Value=ExpenseAmount,id=ID)
                                    AddExpense()

                            else:
                                st.warning(f"There is Insufficient Cash! The available Balance is:: {CashAccount_Bal():,.0f}.")
                        elif PaymentMode == "Credit":
                            PayableExpenses_Record(id=ID)
                            AddExpense()
                    else:
                        st.warning("Expense Amount should contain a number value!!")
            else:
                st.warning("⚠️Please complete all the fields above, before you proceed")

# Delete Expenses Form
def DeleteExpensesForm():
    
    ID_List = Business.SelectionFromTable(self=Business,tablename="ExpensesTable",colName="ID")
    #Transcategories = Business.SelectionFromTable(self=Business,tablename="ExpensesTable",colName="ExpenseCategory")
    
    Exp_ID = st.selectbox("Select Expense You Want to DELETE",ID_List)
    
    if len (Exp_ID) > 1:
        nam_label,exp_name = st.columns(2)
        col1,col2,col3,col4 = st.columns(4)
        col_1,col_2,col_3,col_4 = st.columns(4)

        ExpenseDetails = Business.SelectDataPerID("Business","ExpensesTable","ID",Exp_ID)
            
        ID = ExpenseDetails[0][0]
        Expense_Name = ExpenseDetails[0][1]
        Expense_Category = ExpenseDetails[0][2]
        Expense_Amount = ExpenseDetails[0][3]
        Payment_Mode = ExpenseDetails[0][4]
        Transaction_Date = ExpenseDetails[0][5]
        # Transaction_Date = datetime.strftime(Transaction_Date,"%d_%m_%y-%I-%M-%S-%p")
        Des_cription = ExpenseDetails[0][6]
        
        nam_label.info("Expense Name")
        exp_name.success(f"{Expense_Name}")
        col1.info("Transaction Category")
        col2.success(f"{Expense_Category}")
        col3.info("Expenses Amount")
        col4.success(f"{Expense_Amount:,.0f}")
        col_1.info("Payment Mode")
        col_2.success(f"{Payment_Mode}")
        col_3.info("Transaction Date")
        col_4.success(f"{Transaction_Date}")
        st.info(f"DESCRIPTIONS: {Des_cription}")

        sub_btn = st.button("Delete Expenses")

        if sub_btn:
            Business.DeleteItem(self=Business,tablename="ExpensesTable",refcol="ID",refval=ID)
            st.warning(f"The Expense: {Expense_Name[0]} has been DELETED succesfuly!")  

# Collecting Receivables Form
def ReceivablesColloectionForm():
    debtorsel, recamount = st.columns(2)
    DebtorsList = Business.SelectionFromTable(self=Business,tablename="ReceivablesAccount",colName="CustomerSupplierName")

    # Cal Customer Outstanding Balance
    def CustomerOutstandingBal(debtorname):
        DR_Value = Business.Sum_Values(self=Business,colVal="DebtAmount",tablename="ReceivablesAccount",refcol="CustomerSupplierName",refval=debtorname)[0][0]
        CR_Value = Business.Sum_Values(self=Business,colVal="CreditAmount",tablename="ReceivablesAccount",refcol="CustomerSupplierName",refval=debtorname)[0][0]
        return  DR_Value - CR_Value

    # select customer
    Debtors = []
    for debtor in DebtorsList:
        BalVal = CustomerOutstandingBal(debtor)
        if BalVal > 0:
            debtor = debtor.replace("['", "").replace("']", "")
            Debtors.append(debtor)
        else:
            pass 

    SelDebtor = debtorsel.multiselect("Select A Debtor Who has Settled Outstanding",options=Debtors)
      
    # Record Receivable Amount after sale on Credit
    def UpdateReceivable_Recovery():
        accountname = "ReceivablesAccount"
        ID = str(datetime.today()) + "_" + str(random.randint(10,100000))
        TranasctionDate = datetime.today().strftime("%Y-%m-%d")
        TransactionDetails = f"Repayment of Receivable of {TotalValue:,.0f} for {SelDebtor[0]} on {TranasctionDate}"
        DebtAmount = 0
        CreditAmount = TotalValue
        DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","ReceivablesAccount")
        Cul_DRBalance = DRBalance + DebtAmount
        CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","ReceivablesAccount")
        Cul_CRBalance = CRBalance + CreditAmount
        BookBalance = Cul_DRBalance - Cul_CRBalance
        CustomerSupplierName = SelDebtor[0]
        SystemTransactDate = datetime.today()
        return Business.AddTransAccount(Business,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                                         BookBalance,CustomerSupplierName, SystemTransactDate)
    if len(SelDebtor)== 1:
        with st.form("ReceivablesForm",clear_on_submit=True):
            def Input_Recovery(custname):
                TotalValue = 0  
                try:
                    TotalValue = float(recamount.text_input(f"Enter Amount Recovered From : {custname}"))
                except ValueError:
                    pass
                finally:
                    return TotalValue

            TotalValue = Input_Recovery(SelDebtor[0])   
            name_label,name_value = st.columns(2)
            debt_label,debt_value = st.columns(2)
            
            debt_label.info("Total Outstanding Debt Amount")
            DebtBal = CustomerOutstandingBal(SelDebtor[0])
            debt_value.success(f"{DebtBal:,.0f}")
            name_label.info("Customer Name")
            name_value.success(f"{SelDebtor[0]}")
                        
            RepayButton = st.form_submit_button("Receive Payment")

            if RepayButton:

                if isnumber(TotalValue):
                    if float(TotalValue) > 0 and float(TotalValue) <= float(DebtBal) and float(DebtBal) != 0:
                        UpdateReceivable_Recovery()
                        st.success(f'''Congratulations! You have successful recovered {TotalValue:,.0f} from {SelDebtor[0]}
                                        The Remaining Balance is {CustomerOutstandingBal(SelDebtor[0]):,.0f}.''')
                        # Re-update Balance after recording the recovered amount
                        DebtBal = CustomerOutstandingBal(SelDebtor[0])
                        debt_label.warning(f"Remaining Balance After Recovering: {TotalValue:,.0f}")
                        debt_value.error(f"{DebtBal:,.0f}")
                        # Record the recovered amount into Cash Account
                        ID = str(datetime.today()) + "_" + str(random.randint(10,100000))
                        AddCash_Receipt(Value=TotalValue,id=ID)
                        st.balloons()

                    elif float(DebtBal) == 0:
                        st.warning(f"The Customer {SelDebtor[0]} has no OUTSTANDING DEBT")
                    else:
                         st.warning(f"Recovery Amount Should be Between {1} and {DebtBal:,.0f}.")
                else:
                    st.warning("Recovery Amount field Should be filled with a Number.")

# Settling Payable Form
def SettlingPayableForm():
    paysel, sel_amount = st.columns(2)
    CreditorsList = Business.SelectionFromTable(self=Business,tablename="PayablesAccount",colName="CustomerSupplierName")

    # Cal Customer Outstanding Balance
    def CreditorOutstandingBal(creditorname):
        DR_Value = Business.Sum_Values(self=Business,colVal="DebtAmount",tablename="PayablesAccount",refcol="CustomerSupplierName",refval=creditorname)[0][0]
        CR_Value = Business.Sum_Values(self=Business,colVal="CreditAmount",tablename="PayablesAccount",refcol="CustomerSupplierName",refval=creditorname)[0][0]
        return  CR_Value - DR_Value

    # select customer
    Creditors = []
    for creditor in CreditorsList:
        BalVal = CreditorOutstandingBal(creditor)
        if BalVal > 0:
            creditor = creditor.replace("['", "").replace("']", "")
            Creditors.append(creditor)
        else:
            pass 

    SelCreditor = paysel.multiselect("Select A Creditor Whose Payable is Being Settled",options=Creditors)
      
    # Record Repayment of Payment
    def UpdatePayable_Repayment():
        accountname = "PayablesAccount"
        ID = str(datetime.today()) + "_" + str(random.randint(10,100000))
        TranasctionDate = datetime.today().strftime("%Y-%m-%d")
        TransactionDetails = f"Repayment of Payable of {TotalValue:,.0f} for {SelCreditor[0]} on {TranasctionDate}"
        DebtAmount = TotalValue
        CreditAmount = 0
        DRBalance = Business.Sum_DR_CR(Business,"DebtAmount","PayablesAccount")
        Cul_DRBalance = DRBalance + DebtAmount
        CRBalance = Business.Sum_DR_CR(Business,"CreditAmount","PayablesAccount")
        Cul_CRBalance = CRBalance + CreditAmount
        BookBalance = Cul_CRBalance - Cul_DRBalance
        CustomerSupplierName = SelCreditor[0]
        SystemTransactDate = datetime.today()
        return Business.AddTransAccount(Business,accountname,ID,TranasctionDate, TransactionDetails, DebtAmount, CreditAmount,
                                         BookBalance,CustomerSupplierName, SystemTransactDate)
    if len(SelCreditor)== 1:
        with st.form("PayablesForm",clear_on_submit=True):
            def Input_Repayment(suppname):
                TotalValue = 0  
                try:
                    TotalValue = float(sel_amount.text_input(f"Enter Amount Paid To : {suppname}"))
                except ValueError:
                    pass
                finally:
                    return TotalValue

            TotalValue = Input_Repayment(SelCreditor[0])   
            name_label,name_value = st.columns(2)
            creditor_label,creditor_value = st.columns(2)
            
            creditor_label.info("Total Payable Amount")
            CreditorBal = CreditorOutstandingBal(SelCreditor[0])
            creditor_value.success(f"{CreditorBal:,.0f}")
            name_label.info("Supplier Name")
            name_value.success(f"{SelCreditor[0]}")
                        
            RepayButton = st.form_submit_button("Submit Payment")

            if RepayButton:
                if isnumber(TotalValue):
                    if float(TotalValue) > 0 and float(TotalValue) <= float(CreditorBal) and float(CreditorBal) != 0:

                        if CashAccount_Bal() >= float(TotalValue):

                            ID = str(datetime.today()) + "_" + str(random.randint(10,100000))
                            PayCash_Record(Value=TotalValue,id=ID)
                            UpdatePayable_Repayment()
                            st.success(f'''Congratulations! You have successful Paid {TotalValue:,.0f} to {SelCreditor[0]}
                                            The Remaining Balance is {CreditorOutstandingBal(SelCreditor[0]):,.0f}.''')
                            # Re-update Balance after recording the recovered amount
                            creditorBal = CreditorOutstandingBal(SelCreditor[0])
                            creditor_label.warning(f"Remaining Balance After Repaying: {TotalValue:,.0f}")
                            creditor_value.error(f"{creditorBal:,.0f}")
                            
                            st.balloons()

                        else:
                            st.warning(f"There is Insufficient Cash! The available Balance is:: {CashAccount_Bal():,.0f}.")
                        

                    elif float(CreditorBal) == 0:
                        st.warning(f"There is no OUTSTANDING for Supplier {SelCreditor[0]}")
                    else:
                         st.warning(f"Repayment Amount Should be Between {1} and {CreditorBal:,.0f}.")
                else:
                    st.warning("Repayment Amount field! Should be filled with a Number.")

def Add_CustomersSuplliersForm():

     with st.form("Customer_Suplier",clear_on_submit=True):
        fil1,fil2,fil3 = st.columns(3)
        fil4,fil5 = st.columns(2)

        Name = fil1.text_input("Name of Customer/Supplier")
        Location = fil2.text_input("Location")
        Type = fil3.multiselect("Category",["Customer","Supplier"])
        Email = fil4.text_input("Email")
        Phone = fil5.text_input("Phone")
        sub = st.form_submit_button(f"Add to the List")

        if sub:
            if len(Name) > 0 and len(Location) > 0 and len(Type) == 1 and len(Email)  > 0 and len(Phone)  > 0:

                ID = str(datetime.today()) + "_" + str(random.randint(10,100000))+ str(Name)
                CreationDate = datetime.today()
                AddCustomerSupplier(ID,Name,Location,Type[0],Email,Phone,CreationDate)
                st.balloons()
                st.success(f"You have successfully created {Name}")
            else:
                st.warning("⚠️Please complete all the fields above, before you proceed")
   

# Delete CustomersSuplliers Form
def Delete_CustomersSuplliersForm():
    
    List = Business.SelectionFromTable(self=Business,tablename="CustomersSuppliersTable",colName="Name")
    #Transcategories = Business.SelectionFromTable(self=Business,tablename="ExpensesTable",colName="ExpenseCategory")
    
    CustSup = st.multiselect("Select Customer or Suplier You Want to DELETE",List)
    
    if len (CustSup) == 1:
        nam_label,exp_name = st.columns(2)
        col1,col2,col3,col4 = st.columns(4)
        col_1,col_2,col_3,col_4 = st.columns(4)

        CustomerSupDetails = Business.SelectDataPerID("Business","CustomersSuppliersTable","Name",CustSup[0])

        ID = CustomerSupDetails[0][0]
        Name = CustomerSupDetails[0][1]
        Location = CustomerSupDetails[0][2]
        Type = CustomerSupDetails[0][3]
        Email = CustomerSupDetails[0][4]
        Phone = CustomerSupDetails[0][5]
        
        
        nam_label.info("Customer or Supplier Name")
        exp_name.success(f"{Name}")
        col1.info("Location")
        col2.success(f"{Location}")
        col3.info("Customer/Supplier")
        col4.success(f"{Type}")
        col_1.info("Email")
        col_2.success(f"{Email}")
        col_3.info("Phone")
        col_4.success(f"{Phone}")

        sub_btn = st.button("Delete Customer/Supplier")

        if sub_btn:
            Business.DeleteItem(self=Business,tablename="CustomersSuppliersTable",refcol="ID",refval=ID)
            st.warning(f"{Name} has been DELETED succesfuly!")  


# REPORTING & ANALYTICS
# Function to view Stocks Balance
def ViewBal():
     data = Business.Sum_Values_Bal(self=Business,selcol="ItemName", colVal="ItemQuantity",tablename="StocksTable")
     return data

#View Stocks Reports
def View_StocksReports():
    StocksBal = ViewBal()
    with st.expander("Real Time Stock Updates",expanded=True):
        
        if len(StocksBal) > 0:
            # st.error("Available Stocks")
            leav,name,bal,stockvalue = st.columns([1,1,1,1])
            leav,TotalDes,Totalstockvalue = st.columns([1,2,1])
            TotalDes.warning("Total")
            Total =Business.Sum_ClosingBal_Val(Business)
            Totalstockvalue.warning(f"{Total:,.0f}")
        
            name.warning("Name of Stock")
            bal.warning("Product Balance")
            stockvalue.warning("Stock Value")

            for prod in StocksBal:
                name.info(f"{prod[0]}")
                stockvalue.success(f"{prod[1]:,.0f}")
                bal.info(f"{prod[2]}")
            
            # Extract & Download Stock Bal
            Stocks = Business.SelectClosingStocks(Business)
            Names = []
            ProductQ = []
            ProductP = []
            TransaValue = []
            for Val in Stocks:
                Names.append(Val[1])
                ProductQ.append(Val[2])
                ProductP.append(Val[3])
                TransaValue.append(Val[7])
            
            StockDic = {"Product Name": Names,"Product Q":ProductQ,"Product Unit Price":ProductP,"Transaction Value":TransaValue}
            StocksDF = pd.DataFrame.from_dict(StockDic).set_index("Product Name")
            
            DownloadData(viewlabel="Download Available Stock Balance",df=StocksDF,file_name="EndingStock",locator=st)
            #st.table(StocksDF.head(5))
        else:
            st.info("Currently, There is no stock to Report! 😢")

# Fetching Closing Stock
# Create Table
ClosingStockBalTable()

# Function to get the closing stock as per selected Reporting Start Date
def LatestClosingStock(date):
    ClosingStock = []
    PossibleDates = range(0,2000)
    for PreDate in PossibleDates:
        if len(ClosingStock) > 0:
            break
        try:
            ClosingStock = DailyClosingStock(closingdate=date - timedelta(days=PreDate))
            return ClosingStock[0][0]
        except IndexError:
            continue

#View P & L Report
def View_Profit_Loss():
    # calculate profit
    def cal_profit(sale,cost):
        if sale is None or cost is None:
            return 0
        else:
            profit = sale - cost
            if profit >= 0:
                return f"{profit:,.0f}"
            else:
                return f"({abs(profit):,.0f})"
    # Display None == 0
    def get_display(val):
        if val is None:
            return 0
        else:
            return val
    StocksBal = ViewBal()
    with st.expander("Real Time Profit & Loss Statement",expanded=True):    
        st.success("Besiness Key Metrices & Profit/Loss Statement")
        space,sd,ed = st.columns([1,1,1])
        metr1,metr2,metr3 = st.columns([1,1,1])

        if len(StocksBal) > 0:

            sd = sd.date_input(label="Start Date",value=default_date_PY)
            ed = ed.date_input("End Date")

            # get Ending Stock as per Ed
            TotalClosingStock = LatestClosingStock(date=ed)
            # TotalClosingStock = Business.Sum_ClosingBal_Val(Business)

            TotalSales = Business.Sum_Amount(self=Business,Sale_Purchase="Sale",sd=sd,ed=ed)
            TotalPurchases = Business.Sum_Amount(Business,"Purchase",sd,ed)
            TotalCOGS = Business.Sum_CostSales_Val(Business,sd,ed)
            TotalOperatingExp = Business.Sum_OperatingExp_Val(Business,sd,ed)
            
            def showloss_profit():
                if TotalSales >= 0 and TotalCOGS >= 0:
                    TotalProfit = TotalSales-TotalCOGS
                    if TotalProfit >= 0:
                        return f"Profit: Tshs.{TotalProfit:,.0f}"
                    else:
                        return f"Loss: Tshs.{abs(TotalProfit):,.0f}"

            # and (ActionType in ("Cash Sale","Credit Sale")
            if TotalSales and TotalCOGS:
                
                metr1.metric(label="Total Sales",value=f"Tshs.{get_display(TotalSales):,.0f}")
                metr2.metric(label="Total Purchases",value=f" Tshs.{get_display(TotalPurchases):,.0f}")
                metr3.metric(label="Total Cost of Sales",value=f" Tshs.{get_display(TotalCOGS):,.0f}")
                #Line---2
                metr1.metric(label="Total Closing Stock",value=f"Tshs.{get_display(TotalClosingStock):,.0f}")
                metr2.metric(label="Gross Profit/Loss",value=showloss_profit())
                metr3.metric(label="Total Operating Expenses",value=f" Tshs.{get_display(TotalOperatingExp):,.0f}")
            
                st.markdown("<hr>",unsafe_allow_html=True)

                # Profit & Loss Statement
                st.markdown('''<p class="PL_MainHeader">NESTORY'S BUSINESS</p>''',unsafe_allow_html=True)
                st.markdown('''<p class="PL_SecondHeader">Statement of Profit & Loss</p>''',unsafe_allow_html=True)
                st.markdown(f'''<p class="PL_ThirdHeader">For the Period Between {sd.strftime("%d %B %Y")} and {ed.strftime("%d %B %Y")}</p>''',unsafe_allow_html=True)
                
                # Top Labels
                emptop_label,amnttop_value = st.columns([5,0.8])
                amnttop_value.markdown('''**Amount in TZS**''')
            
                # Sales Revenue
                revenue_label,revenue_value = st.columns([5,0.8])
                revenue_label.info("Sales Revenue")
                revenue_value.success(f"{get_display(TotalSales):,.0f}")
            
                # Cost of Goods Sold
                st.markdown('''***Cost of Goods Sold***''')
                fistempt,descr,descr_value,lastempt = st.columns([1,3.2,0.8,0.8])
                
                val_sd = sd - timedelta(days=1)
                OpenStock = LatestClosingStock(date=val_sd)
                descr.info("Opening Stock")
                descr.info("Purchases")
                descr_value.warning(f"{get_display(val=OpenStock):,.0f}")
                descr_value.warning(f"{get_display(TotalPurchases):,.0f}")
                fistempt,closingdescr,closing_value,COGS_value = st.columns([1,3.2,0.8,0.8])
                closingdescr.info("Closing Stock")
                closing_value.warning(f"({get_display(TotalClosingStock):,.0f})")
                COGS_value.success(f"({get_display(TotalCOGS):,.0f})")
                
                # Gross Profit
                GP_label,GP_value = st.columns([5,0.8])
                GP_label.info("Gross Profit/Loss")
                TotalProfit = cal_profit(TotalSales,TotalCOGS)
                GP_value.success(f"{TotalProfit}")
                
                # Operating Expenses
                OperatExp = Business.Sum_Operating_Expenses(Business,sd,ed)
                if len(OperatExp) > 0:
                    st.markdown('''***Operating Expenses***''')
                    fistempt,Expdescr,expval = st.columns([1,4,0.8])
                    for Exp in OperatExp:
                        Expdescr.info(f"{Exp[0]}")
                        expval.success(f"({Exp[1]:,.0f})")
                    
                    # Net Profit
                    NP_label,NP_value = st.columns([5,0.8])
                    def net_profit_val(TotalSales,TotalCOGS,TotalOperatingExp):
                        if TotalProfit is None or TotalOperatingExp is None:
                            return 0
                        else:
                            NetProfit = TotalSales-TotalCOGS-TotalOperatingExp
                            if NetProfit >= 0:
                                return f"{NetProfit:,.0f}"
                            else:
                                return f"({abs(NetProfit):,.0f})"
                    #--------------------------------------------------------------
                    def net_desc(TotalSales,TotalCOGS,TotalOperatingExp):
                        if TotalProfit is None or TotalOperatingExp is None:
                            return ""
                        else:
                            NetProfit = TotalSales-TotalCOGS-TotalOperatingExp
                            if NetProfit >= 0:
                                return "Net Profit"
                            else:
                                return "Net Loss"

                    NP_label.info(f"{net_desc(TotalSales,TotalCOGS,TotalOperatingExp)}")
                    NP_value.success(f"{net_profit_val(TotalSales,TotalCOGS,TotalOperatingExp)}")
            else:
                st.info(f'''Sorry! There is no Reporting Information for the Selected Period:
                           Between {sd.strftime("%d %B %Y")} and {ed.strftime("%d %B %Y")}''')
        else:
            st.info("Currently, There is no transactions to Report!")

# Financial Statement

# Function to get the closing Balance of an Account as per selected Reporting Start Date
def LatestClosingAccountBal(accname, date):
    ClosingBal = []
    PossibleDates = range(0,2000)
    for PreDate in PossibleDates:
        if len(ClosingBal) > 0:
            break
        try:
            ClosingBal = DailyAccountBalance(accountname=accname,closingdate=date - timedelta(days=PreDate))
            return ClosingBal[0][0]         
        except IndexError:
            continue

def AccountClosingBalance(accname, date):
    Bal = LatestClosingAccountBal(accname, date)
    if Bal is None:
        return 0
    else:
        return Bal

def EndingStockBal(ed):
    Bal = LatestClosingStock(date=ed)
    if Bal is None:
        return 0
    else:
        return Bal



# Retained Earnings
def equity_RetainedEarnings(TotalSales_All,TotalCOGS_All,TotalOperatingExp_All):
    TotalProfit = TotalSales_All - TotalCOGS_All
    if TotalProfit is None or TotalOperatingExp_All is None:
        return 0
    else:
        RetainedEarnings = TotalSales_All-TotalCOGS_All-TotalOperatingExp_All
        if RetainedEarnings >= 0:
            return RetainedEarnings
        

def FinancialStatement():

    space,end = st.columns([2,1])

    ed = end.date_input("When You Want To See A Financial Position of The Business!")

    # Compute All
    start = "1900-01-01"
    end = ed
    TotalSales_All = Business.Sum_Amount(self=Business,Sale_Purchase="Sale",sd=start,ed=end)
    TotalCOGS_All = Business.Sum_CostSales_Val(Business,sd=start,ed=end)
    TotalOperatingExp_All = Business.Sum_OperatingExp_Val(Business,sd=start,ed=end)

    # Statement of Financial Position
    st.markdown('''<p class="PL_MainHeader">NESTORY'S BUSINESS</p>''',unsafe_allow_html=True)
    st.markdown('''<p class="PL_SecondHeader">Statement of Financial Positions</p>''',unsafe_allow_html=True)
    st.markdown(f'''<p class="PL_ThirdHeader">As at {ed.strftime("%d %B %Y")}</p>''',unsafe_allow_html=True)            
    Cash_balance = AccountClosingBalance(accname="CashAccount",date=ed)
    Receivable_balance = AccountClosingBalance(accname="ReceivablesAccount",date=ed)
    Payable_balance = AccountClosingBalance(accname="PayablesAccount",date=ed)

    assets,equity = st.columns([1,1])

    assets.markdown("**Total Assets**")
    Horizontal_Line(loc=assets)
    equity.markdown("**Total Liabilites & Equity**")
    Horizontal_Line(loc=equity)
    
    asset_des,asset_val,space, eq_des,eq_val = st.columns([1.5,0.8,0.5,1.5,0.8])

    # Current Assets
    asset_des.info("***Cash & Cash Equivalents***")
    asset_val.success(f"**{Cash_balance:,.0f}**")

    asset_des.info("***Account Receivables***")
    asset_val.success(f"**{Receivable_balance:,.0f}**")
    
    asset_des.info("***Ending Stock***")
    asset_val.success(f"**{EndingStockBal(ed):,.0f}**")

    # Total Assets
    TotalAssets = Cash_balance + Receivable_balance + EndingStockBal(ed)
    asset_des.warning("Total Assets")
    asset_val.error(f"{TotalAssets:,.0f}")
    
    # Current Liabilities
    eq_des.info("***Account Payables & Accrued Expenses***")
    eq_val.success(f"**{Payable_balance:,.0f}**")

    # Retained Earnings
    TotalEquity=equity_RetainedEarnings(TotalSales_All,TotalCOGS_All,TotalOperatingExp_All)
    eq_des.info("***Retained Earnings***")
    eq_val.success(f"**{TotalEquity:,.0f}**")

    # Total Retained & Liabilites
    Total_RE_LI = Payable_balance + TotalEquity
    eq_des.warning("Total Equity & Liabilities")
    eq_val.error(f"{Total_RE_LI:,.0f}")
