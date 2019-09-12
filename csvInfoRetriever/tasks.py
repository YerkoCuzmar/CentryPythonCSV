from celery import shared_task
from django.db.models import F, Q, Max, Min
from celery.utils.log import get_task_logger
from django.contrib import messages
from csvInfoRetriever.config import *
from csvInfoRetriever.models import Product
from Centry_Python_CSV.centry import CentrySdk
import csv
import requests
import concurrent.futures
import threading


MAX_THREADS = 10

logger = get_task_logger(__name__)
centry = CentrySdk()


# Obtiene informacion de csv desde url
@shared_task
def ask_for_inventory():
    with requests.Session() as session:
        download = session.get(CSV_URL, timeout=120)
        if download.status_code == 200:
            decoded_content = download.content.decode('utf-8')
            data = csv.reader(decoded_content.splitlines(), delimiter=CSV_DELIMITER)
            products = list(data)
            save_csv_products(products)
        else:
            messages.error(download, 'Failed to download .csv info.')


@shared_task
# Guarda los productos de un csv en la BD local
# lines -> list(header_y_productos)
# header_y_productos -> lista de campos del csv
def save_csv_products(lines):
    # TODO: Generar reporte de errores
    logger.info('Inicio save_csv_products task')
    header = clean_line(lines.pop(0))
    positions = {
        'sku_pos': header.index(SKU_HEADER),
        'stock_pos': header.index(STOCK_HEADER),
        'normal_price_pos': header.index(NORMAL_PRICE_HEADER),
        'offer_price_pos': header.index(OFFER_PRICE_HEADER)
    }
    print("Inicio lectura CSV")
    errors = []
    for line in lines:
        line = clean_line(line)
        if len(line) != len(header):
            errors.append(line[positions['sku_pos']])
        else:
            product, created = Product.objects.get_or_create(sku=line[positions['sku_pos']])
            product.sku = line[positions['sku_pos']]
            product.stock = mk_int(line[positions['stock_pos']])
            product.price = mk_int(line[positions['normal_price_pos']])
            product.save()
    print("Fin lectura CSV")


@shared_task
def centry_stock_save():
    # TODO: Generar reporte de errores
    dif_stock = ~Q(stock=F('last_stock_reported_centry')) & Q(stock__isnull=False)
    local_stock_present = Q(stock__isnull=False) & Q(last_stock_reported_centry__isnull=True)
    update_null = Q(stock__isnull=True) & Q(last_stock_reported_centry__isnull=False)
    if UPDATE_IF_LOCAL_STOCK_NULL:
        products = Product.objects.filter(dif_stock | local_stock_present | update_null)
    else:
        products = Product.objects.filter(dif_stock | local_stock_present)
    sliced_products = slice_products(products)
    # print(f"Total threads: {len(sliced_products)}")
    print(f"products:\n {products}")
    print(f"sliced_products:\n {sliced_products}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(centry_stock_save_thread, sliced_products)


@shared_task
def centry_stock_save_thread(products):
    print(f"Stock save thread iniciado : {threading.get_ident()}")
    print(f"id:{threading.get_ident()}\n {products}\n")
    for product in products:
        resp = centry.sdk().put('conexion/v1/variants/sku.json', None, {"sku": product.sku, "quantity": product.stock})
        print(f"SS: thread: {threading.get_ident()} - prod: {products.index(product)} - producto : {product.id} - resp_code: {resp.status_code}")
        if resp.status_code == 200:
            product.last_stock_reported_centry = resp.json()['quantity']
            product.id_product_centry = resp.json()['product_id']
            product.save()
    print(f"Stock save thread terminado : {threading.get_ident()}")


@shared_task
def centry_price_save():
    products = Product.objects.exclude(Q(id_product_centry__isnull=True) | Q(id_product_centry=""))
    if UPDATE_WITH_MAX_PRICE:
        products = products.values('id_product_centry').annotate(price=Max('price'))
    else:
        products = products.values('id_product_centry').annotate(price=Min('price'))
    sliced_products = slice_products(products)
    print(f"products:\n {products}")
    print(f"sliced_products:\n {sliced_products}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(centry_price_save_thread, sliced_products)


@shared_task
def centry_price_save_thread(products):
    print(f"Price save thread iniciado : {threading.get_ident()}")
    print(f"products {products}")
    # print(f"id:{threading.get_ident()}\n {products}\n")
    for product in products:
        resp = centry.sdk().put(f"conexion/v1/products/{product['id_product_centry']}.json", None, {"price_compare": product['price']})
        print(f"resp: {resp}")
        if resp.status_code == 200:
            print('200')
            update_products = Product.objects.filter(id_product_centry=product['id_product_centry'])
            for up_product in update_products:
                up_product.last_price_reported_centry = resp.json()['price_compare']
                up_product.save()
    print(f"Stock save PRICE terminado : {threading.get_ident()}")


def clean_line(line):
    for i in range(len(line)):
        line[i] = line[i].strip()
    return line


def mk_int(s):
    s = s.strip()
    return int(s) if s else 0


def sectors(total_prod, thread_num=MAX_THREADS):
    import math
    range_list = []
    chunk_size = math.ceil(total_prod/thread_num)
    sectors_num = thread_num  # create number of sectors
    for i in range(sectors_num):
        if i < (sectors_num - 1):
            range_list.append((chunk_size*i, chunk_size*(i+1)))  # All will chunk equal size except the last one.
        else:
            range_list.append((chunk_size*i, total_prod))  # Takes rest at the end.
    return range_list


def slice_products(products):
    range_list = sectors(len(products))
    sliced_products = []
    for tpl in range_list:
        start, end = tpl
        sliced_products.append(products[start:end])
    return sliced_products
