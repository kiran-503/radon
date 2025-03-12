from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from services.risk_management.var import calculate_var
from data_service.yahoo_finance import get_stock_price
# Flask App Setup
app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "*"}})  # Restrict CORS to /api routes

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://radon:radon@localhost/radon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Stock(db.Model):
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True, index=True)
    token = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    lotsize = db.Column(db.Integer, nullable=True)
    exch_seg = db.Column(db.String, nullable=False)
    sector = db.Column(db.String, nullable=True)
    industry = db.Column(db.String, nullable=True)
    short_name = db.Column(db.String, nullable=True)
    long_name = db.Column(db.String, nullable=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    return jsonify(data)

@app.route('/api/search_stocks', methods=['GET'])
def search_stocks():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])  # Return empty list if query is empty

    # Perform a case-insensitive search in the database
    results = Stock.query.filter(
        (Stock.token.ilike(f'%{query}%')) | 
        (Stock.name.ilike(f'%{query}%')) | 
        (Stock.short_name.ilike(f'%{query}%')) |
        (Stock.long_name.ilike(f'%{query}%'))
    ).all()

    return jsonify([
        {
            'id': stock.id,
            'token': stock.token,
            'name': stock.name,
            'sector': stock.sector,
            'industry': stock.industry,
            'exch_seg': stock.exch_seg,
            'lotsize': stock.lotsize,
            'short_name': stock.short_name,
            'long_name': stock.long_name
        }
        for stock in results
    ])

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    industries = Stock.query.with_entities(distinct(Stock.industry)).all()
    sectors = Stock.query.with_entities(distinct(Stock.sector)).all()
    
    return jsonify({
        'industries': [i[0] for i in industries],
        'sectors': [s[0] for s in sectors]
    })

@app.route('/api/metrics', methods=['POST'])
def metrics():
    stock = request.args.get('stock', 'SBIN')
    confidence_level = float(request.args.get('confidence', 0.95))
    periods = ['1mo','3mo','6mo', '1y', '5y', '10y']
    results = {"Var": {}}
    for period in periods:
        data = get_stock_price(stock, None,None,period=period)
        print(data)
        results['Var'][period] = calculate_var(data,stock, period,confidence_level)
    # data = get_stock_price(stock)
    # results = {period: calculate_var(stock, confidence_level, period=period) for period in periods}
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
