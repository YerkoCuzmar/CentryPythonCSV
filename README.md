# CentryPythonCSV #

Este proyecto actualiza stock y precios desde un CSV hacia Centry a través de dos Cron Jobs, uno para stock y otro para
 precios, con tiempos de inicio de ejecución configurables e independientes entre sí. 

 El CSV se obtiene a través de un link de descarga, y todos los movimientos quedan registrados en una base de datos 
 local del proyecto.


### Requerimientos ###

- [Python 3.6](https://www.python.org/).
- [Django 2.2](https://www.djangoproject.com/).
- [SQLite3](https://www.sqlite.org/index.html).
- [Celery](http://docs.celeryproject.org/en/master/index.html).
- [Redis](https://redis.io/).
- Cuenta en [Centry](https://www.centry.cl).


### Vista General ###

Este proyecto consta principalmente de:

- **Modelos**
     * **Producto**: Contiene información para relacionar productos entre la integración y Centry.
     
     
- **Aplicaciones**
    * **Centry_Python_CSV**: Aplicación encargada de toda la configuración del proyecto (Django, Celery).
    * **csvInfoRetriever**: Aplicación encargada de recopilar información desde CSV, guardarla en la BD local y enviarla
    a Centry.
    
    
- **Tareas**
    Están ubicadas en `csvInfoRetriever/tasks.py`
    * `ask_for_inventory()`: Tarea encargada de obtener los productos desde el csv y guardarlos en la BD local.
    * `centry_stock_save()`: Tarea encargada de enviar los stocks de los productos desde la BD local a Centry.
    * `centry_price_save()`: Tarea encargada de enviar los productos desde la BD local a Centry.
    
    
- **Archivo de Configuración**
    Está ubicado en `csvInfoRetriever/config.py`
    
    * Centry
        * `CENTRY_CLIENT_ID`: Id de perfil en Centry.
        * `CENTRY_SECRET`: Token secreto de tu perfil de Centry.
                
    * CSV
        * `CSV_URL`: URL desde donde se descarga el archivo .csv con los productos.
        * `CSV_DELIMITER`: Delimitador usado para separar las columnas en el archivo .csv (comúnmente se usa `;` o `,`).
        * `SKU_HEADER`: Nombre de la columna que contiene el sku del producto.
        * `STOCK_HEADER`: Nombre de la columna que contiene el stock del producto.
        * `NORMAL_PRICE_HEADER`: Nombre de la columna que contiene el precio normal del producto.
        * `OFFER_PRICE_HEADER`: Nombre de la columna que contiene el precio oferta del producto.
    
    * Sincronización (Solo valores *booleanos* `True` o `False`)
        * `PRICES_UPDATE_TIME`: [crontab](http://docs.celeryproject.org/en/master/reference/celery.schedules.html#celery.schedules.crontab) 
        en el cual se define cada cuanto tiempo se ejecuta la tarea de actualización de precios.
        * `STOCKS_UPDATE_TIME`: [crontab](http://docs.celeryproject.org/en/master/reference/celery.schedules.html#celery.schedules.crontab)
         en el cual se define cada cuanto tiempo se ejecuta la tarea de actualización de stocks.
        * `UPDATE_IF_LOCAL_STOCK_NULL`: Si es `True`, los productos que tengan stock nulo en la BD local se envían a Centry 
        con stock 0. Si es `False` se envían solamente los productos con stock no nulo.
        * `UPDATE_WITH_MAX_PRICE`: actualiza un producto en Centry, por ende todas variantes, con el precio máximo (`True`) o 
        mínimo (`False`) del grupo de productos con el mismo `id_product_centry` presentes en la base de datos local al momento de 
        actualizar.
    
### Preparación Proyecto ###

1. Descargar proyecto
2. Instalar paquetes: en carpeta raíz del proyecto ejecutar comando `pip install requirements.txt`    
3. En Centry crear aplicación en la sección *Api & Apps* para obtener los tokens *App Id* y *Secret*
4. Configurar variables en `csvInfoRetriever/config.py`


### Iniciar Proyecto ###

1. Iniciar Redis: `../{redisFolder}/src$ ./redis-server`
2. Iniciar celery beat scheduler: `celery -A Centry_Python_CSV beat -l info`
3. Iniciar celery worker: `iniciar worker celery -A Centry_Python_CSV worker --loglevel=info`
4. Iniciar proyecto: `../Centry_Python_CSV$ python manage.py run server`  


### Uso del proyecto ###
**Actualización de productos**:
Para que se haga efectiva la actualización de productos desde el CSV a Centry debes verificar que **el SKU del producto
en el CSV debe coincidir con el SKU de la variante correspondiente en Centry** (relación mediante SKU). Una vez que 
se inicie el *cron job* esta actualización se hará automáticamente.


### Extensibilidad ###
El fin de este proyecto es generar una base que se pueda expandir según las necesidades de cada integración, por lo que 
para hacer esto lo que se puede hacer es complementar lo que hace cada tarea ya definida, crear nuevos workers con
 nuevas tareas, extender los atributos de los modelos, etc.\
**Nada de esto es obligatorio y queda a criterio de cada integración que haga uso de este proyecto como extenderá 
sus funcionalidades.** 

 
### Referencias ###
- https://www.python.org/
- https://www.djangoproject.com/
- http://docs.celeryproject.org/en/latest/
- https://www.sqlite.org/index.html
- https://redis.io
- https://crontab.guru
- https://centrycl.github.io/centry-rest-api-docs
