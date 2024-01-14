# Transfer Recommender

Transfer Recommender es una aplicación web que permite realizar consultas sobre los equipos y jugadores de LaLiga, así como también realiza recomendaciones de equipos y jugadores.

## Configuración

Para configurar e iniciar la aplicación, seguir los siguientes pasos:

1. Crear un entorno virtual para instalar las dependencias del proyecto (opcional).
2. Situarse en la carpeta del proyecto e instalar las dependencias con el comando `pip install -r requirements.txt`.
3. Realizar las migraciones con el comando: `python manage.py migrate`.
4. Crear un superusuario de Django ejecuntando el comando `python manage.py createsuperuser` e introduciendo las credenciales.
5. Ejecutar la aplicación con el comando `python manage.py runserver`.
6. Navegar a http://127.0.0.1:8000/.

## Carga de datos

Antes de poder utilizar la aplicación, es necesario cargar los datos, el índice de Whoosh y el sistema de recomendación. Para ello, seguir los siguientes pasos:

1. Iniciar sesión con el superusuario creado previamente.
2. Desde el deplegable Administración, realizar las siguientes acciones en orden:
    - Cargar datos actualizados (duración aproximada de 1 minuto): extrae la información y la almacena en la base de datos.
    - Cargar índice de Whoosh (duración aproximada de 5 segundos): almacena la información en índices de Whoosh.
    - Cargar sistema de recomendación (duración aproximada de 20 segundos): almacena las matrices necesarias para realizar las recomendaciones.

## Uso de la aplicación

Desde el desplegable Consultas, se pueden realizar las siguientes consultas implementadas mediante Whoosh:

- **Listar equipos**.
- **Listar jugadores**.
- **Equipos por posición necesitada y edad promedio máxima**: selecciona una posición y una edad promedio máxima para obtener los equipos que necesitan jugadores en esa posición y cuya edad promedio no supere el valor ingresado.
- **Jugadores por equipo y valor de mercado**: selecciona un equipo y un rango de valor de mercado para obtener los jugadores que pertenecen a ese equipo y que tienen un valor de mercado dentro del rango seleccionado.
- **Jugadores por nombre o nacionalidad**: introduce una frase para buscar hasta 5 jugadores que contengan esa frase en su nombre o nacionalidad.
- **Modificar posición** (duración aproximada de 15 segundos): selecciona un jugador y una posición para modificar la posición del jugador. Además de cambiar la posición y etiquetas del jugador, esta función cambia las etiquetas correspondientes al equipo del jugador en caso de que se pase a cumplir alguna de las condiciones necesarias.

Desde el desplegable Recomendaciones, se pueden obtener las siguientes recomendaciones:

- **Recomendación de equipos**: selecciona un jugador para obtener los 3 equipos recomendados para él. Es decir, se recomiendan equipos en los que el jugador encajaría bien.
- **Recomendación de jugadores**: selecciona un equipo para obtener los 10 jugadores recomendados para él. Es decir, se recomiendan jugadores que encajarían bien en el equipo.
- **Equipos similares**: selecciona un equipo para obtener 3 equipos similares. Es decir, se obtienen equipos a los que les puede interesar el mismo tipo de jugador.
- **Jugadores similares**: selecciona un jugador para obtener 5 jugadores similares. Es decir, se obtienen jugadores que les pueden interesar a los mismos clubes.