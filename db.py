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