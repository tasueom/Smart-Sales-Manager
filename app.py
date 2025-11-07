from flask import Flask, render_template, request, redirect, url_for
import db

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales')
def sales():
    """매출 목록 조회"""
    sales = db.get_sales()
    return render_template('sales.html', sales=sales)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """매출 정보를 직접 입력"""
    if request.method == 'POST':
        saledate = request.form['saledate']
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = int(request.form['price'])
        total = quantity * price
        
        db.insert_sale(saledate, name, quantity, price, total)
        
        return redirect(url_for('sales'))
    
    # GET 요청 처리
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)