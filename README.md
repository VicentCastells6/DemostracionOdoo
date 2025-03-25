# Módulo de Demostración, prestamos de equipos internos para Odoo

Este módulo de Odoo está diseñado para **ser una prueba de programación** he añadido diversas funcionalidades para ir probando todo lo que odoo permite. Permite explorar cómo se pueden implementar ciertas características en Odoo, proporcionando ejemplos básicos y fáciles de entender para su uso.

## Características

- **Demostración de Modelos**: El módulo crea modelos de préstamo y equipo para mostrar cómo se pueden manejar datos en Odoo.
- **Vistas Personalizadas**: Incluye vistas como formularios, listas, kanban y graph para ilustrar la personalización de la interfaz.
- **Pruebas de Funcionalidad**: Implementación de algunas pruebas básicas para verificar que el sistema se comporta como se espera.
- **Fáciles de Modificar**: Todo el código está documentado para que puedas modificarlo fácilmente según tus necesidades.

## Requisitos

- **Odoo 18**: Este módulo está diseñado para funcionar con Odoo 18.
- **Acceso a un Servidor de Odoo**: Necesitarás un servidor de Odoo en funcionamiento para instalar y probar el módulo.
  
## Instalación

Sigue estos pasos para instalar el módulo en tu instancia de Odoo:

1. **Clonar el Repositorio**:
   ```bash
   git clone https://github.com/TuUsuario/ModuloDemostracionOdoo.git
Colocar el Módulo en la Carpeta de Addons: Copia el módulo a la carpeta de addons de tu instalación de Odoo. Si estás utilizando una instalación local, la ruta típica suele ser:

bash
Copiar
Editar
cp -r ModuloDemostracionOdoo /ruta/a/tu/odoo/addons/
Actualizar la Lista de Módulos en Odoo: Entra en Odoo y ve a Apps > Update Apps List. Luego, actualiza la lista de módulos para que Odoo reconozca el módulo recién agregado.

Instalar el Módulo: Una vez que la lista de aplicaciones esté actualizada, busca el módulo "Modulo de Demostración y Pruebas" en la interfaz de Odoo y haz clic en Instalar.

## Uso
Este módulo está planteado para ser una versión simple de prestamos de equipos internos, como teléfonos de empresa, portátiles, etc... Algunas de las funcionalidades de prueba que puedes probar son:

- Formularios: Crea y modifica tanto equipos como prestamos a través de formularios personalizados.

- Listas: Visualiza datos en una vista de lista y edita registros desde ahi.

- Kanban: Observa cómo los datos pueden organizarse en una vista de kanban.


# Estructura del Módulo
Este módulo contiene los siguientes componentes principales:

## Modelos:

equipo.equipo = modelo de registro de equipos y sus características
equipo.prestamo = modelo de creacrión de prestamos y la fecha de devolución
equipo.tags = modelo de utilidad **creado manualmente** para gestionar las caracteristicas por etiquetas y la gestión de colores
## Vistas:

- Formularios: Para agregar y editar datos.

- Listas: Para ver los registros de los modelos en formato tabla y devolver o cancelar devolucion de un equipo en la vista de prestamos.

- Kanban: Para una visualización más visual de los registros.

- Acciones: Configura acciones que se ejecutan cuando el usuario interactúa con los datos.

- Datos: Incluye datos de ejemplo que se cargan al instalar el módulo.

## Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.


