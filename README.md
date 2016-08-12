#pyTaringa

Una librería para realizar acciones en Taringa.net

#Requerimientos
* Python2
* requests

Para instalar en su proyecto:
```bash

pip install pytaringa

```
##Ejemplo
Todos los ejemplos tienen el siguiente encabezado

```python
# -*- coding: utf-8 -*-
import time
import sys
from pytaringa import Taringa, Shout, Kn3

if __name__ == '__main__':
    username = "USERNAME"
    password = "PASSWORD"
    taringa = Taringa(username,password)
    shout =  Shout(taringa.cookie)
    print taringa.username
    print taringa.password
    print taringa.user_key
    print taringa.user_id
    print taringa.cookie
    
    #Crear un shout
    print shout.add("Hola a todos")
    time.sleep(10)

    #Crear un shout con una imagen
    print shout.add("#PyT ImageShout",1,0,Kn3.import_to_kn3("http://traduccionesyedra.files.wordpress.com/2012/04/testing.jpg"))

    #Obtener el id de un usuario
    print taringa.get_user_id_from_nick("anpep")

    #Dar like a un shout
    print shout.like("50735408","19963011")

    #Eliminar un shout
    print shout.delete("50735241")

    #Obtener los datos de un shout
    print shout.get_object("47420358")["body"]

    #Obtener el último shout de un usuario
    lastShout = shout.get_last_shout_from_id("19963011")
    print lastShout
    print shout.get_object(lastShout)["body"]

    #Importar una imagen a kn3
    print Kn3.import_to_kn3("http://conociendogithub.readthedocs.org/en/latest/_images/GitHub.png")

```

Todos los ejemplos están en el archivo `examples/test.py`


Para probar ejecuta:

 USERNAME=taringo PASSWORD=shalala python -m pytaringa.examples.test


##TODO
* Comentar el código
* Añadir funcionalidades para los post