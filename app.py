from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import db

app = Flask(__name__)

app.secret_key = 'secret_key1234'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales')
def sales():
    """매출 목록 조회"""
    per_page = 20
    total_count = db.get_sales_count()
    total_pages = (total_count + per_page - 1) // per_page if total_count else 1

    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages))

    sales = db.get_sales(page, per_page)
    return render_template('sales.html', sales=sales, page=page, total_pages=total_pages)

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

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """CSV 파일 업로드"""
    file = request.files['file']
    df = pd.read_csv(file, encoding='utf-8-sig')
    
    required_columns = ['sale_date', 'item_name', 'quantity', 'unit_price']
    if list(df.columns) != required_columns:
        flash('CSV 파일 형식이 올바르지 않습니다.')
        return redirect(url_for('add'))
    
    df = df.dropna(axis=0).reset_index(drop=True)
    for index, row in df.iterrows():
        saledate = row['sale_date']
        name = row['item_name']
        quantity = row['quantity']
        price = row['unit_price']
        total = quantity * price
        db.insert_sale(saledate, name, quantity, price, total)
    
    flash('CSV 파일이 성공적으로 업로드되었습니다.')
    return redirect(url_for('sales'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """매출 정보 수정"""
    if request.method == 'POST':
        saledate = request.form['saledate']
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = int(request.form['price'])
        total = quantity * price
        db.update_sale(id, saledate, name, quantity, price, total)
        return redirect(url_for('sales'))
    sale = db.get_sale(id)
    return render_template('edit.html', sale=sale)

@app.route('/delete/<int:id>')
def delete(id):
    """매출 정보 삭제"""
    db.delete_sale(id)
    return redirect(url_for('sales'))

@app.route('/analysis')
def analysis():
    """매출 분석"""
    sales = db.get_sales()
    return render_template('analysis.html', sales=sales)

if __name__ == '__main__':
    app.run(debug=True)