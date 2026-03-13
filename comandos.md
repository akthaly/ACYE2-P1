# Comandos

## Comandos para ejecutar el docker-compose:

### Crea los contenedores:

``` docker compose up -d --build ```

### Vemos los logs del consumer:

``` docker compose logs -f consumer ```


## Comandos para la DB

### Entrar a MongoDB:

``` docker exec -it park_db mongosh ```

### Ver las DB:

``` show dbs ``` 

### Seleccionar la DB correcta en este caso es park_db:

``` use park_db ```

### Ver los eventos de esta DB:

``` db.eventos.find() ```