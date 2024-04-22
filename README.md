## Prueba Tecnica Kuantaz
<p>Este repositorio contiene el desarrollo de la prueba tecnica realizada</p>

#### Configuracion del Proyecto
<p>Los siguiente pasos contienen toda las configuracion y los comandos que se debe seguir para ejecutar la aplicacion</p>

##### Primer Paso
<p>Creacion del proyecto, creacion del virtualenv y activacion, clonar el repositorio e instalar la librerias</p>

```
mkdir proyecto

cd proyecto/

virtualenv venv

venv/Scripts/activate

git clone https://github.com/Nohua/Kuantaz.git

pip install -r requirements.txt
```

##### Segundo Paso
<p>Se edita la siguiente linea de codigo con la informacion propia de la DDBB. Se asume que ya esta creada la DDBB en postgresql,
por consiguiente, solo se cambia la configuracion en el codigo con la data correspondiente.
</p>

<code> app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@localhost/mydatabase" </code>

<p>Se puede utilizar variables de entorno para la configuracion, pero para efectos de la prueba se realizo la configuracion mostrada</p>

##### Tercer Paso
<p>Se realizan ciertos comandos para configurar la DDBB en flask y luego se ejecuta el servidor de la aplicacion app.py</p>

```
flask db init

flask db migrate -m "descripcion de lo que contiene esta migracion"

flask db upgrade

python app.py
```

##### Cuarto Paso
<p>Como ultimo se debe importar el archivo "<em>Kuantaz Flask_api.postman_collection.json</em>" en la seccion de <em>My Workspace</em>.
Ya que este archivo contiene toda la configuracion de los endpoints, la estructura de bodys en los endpoints que son necesarios y 
algunos endpoint que hay que cambiar para ejecutar de manera mas rapida y sencilla cada uno de los puntos solicitados en la prueba tecnica
</p>
