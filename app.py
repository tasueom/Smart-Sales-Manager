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

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    """매출 분석"""
    year_month_list = db.get_year_month_list()

    default_year_month = None
    if year_month_list:
        default_year_month = f"{year_month_list[0][0]}-{year_month_list[0][1]:02d}"

    year_month = request.values.get('year_month') or default_year_month

    sales = []
    if year_month:
        try:
            year, month = year_month.split('-')
            sales = db.get_sales_by_year_month(year, month)
        except ValueError:
            year_month = default_year_month
            if year_month:
                year, month = year_month.split('-')
                sales = db.get_sales_by_year_month(year, month)
    
    df = pd.DataFrame(sales, columns=['sale_date', 'item_name', 'quantity', 'unit_price', 'total'])

    item_summary = db.get_item_summary()
    item_summary = sorted(item_summary, key=lambda row: row[2], reverse=True)
    data_by_item = {"labels": [], "quantities": [], "totals": []}
    top_items = []
    for name, quantity, total in item_summary:
        data_by_item["labels"].append(name)
        data_by_item["quantities"].append(int(quantity))
        data_by_item["totals"].append(int(total))
        if len(top_items) < 3:
            avg_amount = (total / quantity) if quantity else 0
            top_items.append({
                "name": name,
                "total": int(total),
                "quantity": int(quantity),
                "average": int(avg_amount)
            })

    if df.empty:
        data_by_date = {"label": [], "data": []}
    else:
        df['sale_date'] = pd.to_datetime(df['sale_date']).dt.strftime('%Y-%m-%d')
        grouped = (
            df.groupby('sale_date')['total']
            .sum()
            .reset_index()
            .sort_values('sale_date')
        )
        data_by_date = {
            "label": grouped['sale_date'].tolist(),
            "data": grouped['total'].tolist(),
        }

    return render_template(
        'analysis.html',
        year_month_list=year_month_list,
        selected_year_month=year_month,
        data_by_date=data_by_date,
        data_by_item=data_by_item,
        top_items=top_items,
    )

if __name__ == '__main__':
    app.run(debug=True)