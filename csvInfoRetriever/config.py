from celery.schedules import crontab


# CENTRY CONFIGURATION
CENTRY_CLIENT_ID = 'b1e3d3d638470d38930e24d228165fb9106f7374dd9661129aeadbbfbf72585e'
CENTRY_SECRET = '99795f66a71b16b996a76a54d77c72b18fa739036f52abc47ffd10e44858288a'

# CSV CONFIG
CSV_URL = 'https://intranet.ansaldo.cl/ws/woocommerce/productosCSV.php'
CSV_DELIMITER = ';'
SKU_HEADER = 'Codigo'
STOCK_HEADER = 'Stock critico'
NORMAL_PRICE_HEADER = 'Precio antes'
OFFER_PRICE_HEADER = 'Precio'

# INFO SYNCRONIZATION CONFIG
PRICES_UPDATE_TIME = crontab(minute='*/3')
STOCKS_UPDATE_TIME = crontab(minute='*/3')
UPDATE_IF_LOCAL_STOCK_NULL = False
UPDATE_WITH_MAX_PRICE = False
