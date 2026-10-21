# Puertos y Adaptadores (Ports and Adapters / Hexagonal Architecture)

Este ejemplo demuestra el desacoplamiento de la lógica de dominio respecto a la infraestructura
de persistencia y la configuración del entorno.

## El Problema

En `before.py`, la clase `UserService` instancia directamente `ConcreteDatabase` dentro de su constructor
e invoca `os.environ` dentro de los métodos de negocio. Este diseño acopla el dominio a implementaciones
específicas de almacenamiento y a variables de proceso globales, impidiendo pruebas unitarias aisladas
y forzando el uso de mocks o mutación de estado global.

## Qué Cambió

En `after.py`, se implementa una arquitectura hexagonal pura:

- Se define el puerto `UserRepository` mediante `typing.Protocol` para modelar el contrato de persistencia.
- El servicio de dominio `UserService` recibe el repositorio e invariantes de configuración vía inyección.
- Se implementa el adaptador `InMemoryUserRepository` para ejecutar pruebas deterministas sin dependencias externas.
- Se aísla la lectura de `os.environ` en la función de raíz de composición (`create_user_service`).

## Qué Demuestran las Pruebas

El archivo `test_ports_adapters.py` demuestra que el servicio de dominio se verifica de forma completa
utilizando el adaptador falso en memoria (`InMemoryUserRepository`), validando reglas de negocio e
invariantes de dominio sin recurrir a librerías de simulación (*mocks*).
