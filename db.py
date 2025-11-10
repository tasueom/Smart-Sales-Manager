import mysql.connector

base_config = {
    "host": "localhost",   # MySQL 서버 주소 (로컬)
    "user": "root",        # MySQL 계정
    "password": "1234"     # MySQL 비밀번호
}

# 사용할 데이터베이스 이름
DB_NAME = "salesdb"

# 커넥션과 커서 반환하는 함수
def get_conn():
    return mysql.connector.connect(database=DB_NAME, **base_config)

# 매출 목록 총 개수 조회
def get_sales_count():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_tbl")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

#전체 매출 목록 조회
def get_sales(page=1, per_page=20):
    offset = (page - 1) * per_page
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sale_id, sale_date, item_name, quantity, unit_price, total "
        "FROM sales_tbl ORDER BY sale_date DESC "
        "LIMIT %s OFFSET %s", (per_page, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# 매출 단건 조회
def get_sale(id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sale_id, sale_date, item_name, quantity, unit_price, total FROM sales_tbl WHERE sale_id = %s",
        (id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def insert_sale(saledate, name, quantity, price, total):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO sales_tbl
                    (sale_date, item_name, quantity, unit_price, total)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (saledate, name, quantity, price, total))
    conn.commit()
    cursor.close()
    conn.close()

def update_sale(id, saledate, name, quantity, price, total):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""UPDATE sales_tbl SET
                    sale_date = %s,
                    item_name = %s,
                    quantity = %s,
                    unit_price = %s,
                    total = %s
                    WHERE sale_id = %s""",
                    (saledate, name, quantity, price, total, id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_sale(id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales_tbl WHERE sale_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

# 연도+월의 목록을 반환하는 함수
def get_year_month_list():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT YEAR(sale_date), MONTH(sale_date) FROM sales_tbl ORDER BY YEAR(sale_date) DESC, MONTH(sale_date) DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_sales_by_year_month(year, month):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT sale_date, item_name, quantity, unit_price, total FROM sales_tbl WHERE YEAR(sale_date) = %s AND MONTH(sale_date) = %s ORDER BY sale_date DESC", (year, month))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_item_summary():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT item_name, SUM(quantity) AS total_quantity, SUM(total) AS total_amount "
        "FROM sales_tbl GROUP BY item_name ORDER BY item_name"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows