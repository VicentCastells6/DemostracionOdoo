# Módulo de Demostración y Pruebas para Odoo

Este módulo de Odoo está diseñado para **demostración y pruebas** de diversas funcionalidades. Permite explorar cómo se pueden implementar ciertas características en Odoo, proporcionando ejemplos básicos y fáciles de entender para su uso.

## Características

- **Demostración de Modelos**: El módulo crea modelos de ejemplo para mostrar cómo se pueden manejar datos en Odoo.
- **Vistas Personalizadas**: Incluye vistas como formularios, listas y kanban para ilustrar la personalización de la interfaz.
- **Pruebas de Funcionalidad**: Implementación de algunas pruebas básicas para verificar que el sistema se comporta como se espera.
- **Fáciles de Modificar**: Todo el código está documentado para que puedas modificarlo fácilmente según tus necesidades.

## Requisitos

- **Odoo 18+**: Este módulo está diseñado para funcionar con Odoo 18 o superior.
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
Este módulo no tiene un uso definido, esta creado para probar y experimentar con diferentes configuraciones de Odoo. Algunas de las funcionalidades de prueba que puedes probar son:

- Formularios: Crea y modifica registros a través de un formulario personalizado.

- Listas: Visualiza datos en una vista de lista.

- Kanban: Observa cómo los datos pueden organizarse en una vista de kanban.

- También puedes realizar algunas pruebas personalizadas utilizando las funciones que el módulo ofrece.

# Estructura del Módulo
Este módulo contiene los siguientes componentes principales:

## Modelos:

modelo.demostracion: Un modelo de ejemplo con campos personalizados.

## Vistas:

- Formularios: Para agregar y editar datos.

- Listas: Para ver los registros de los modelos en formato tabla.

- Kanban: Para una visualización más visual de los registros.

- Acciones: Configura acciones que se ejecutan cuando el usuario interactúa con los datos.

- Datos: Incluye datos de ejemplo que se cargan al instalar el módulo.

## Contribuciones
Esto es un proyecto standalone para probar funcionalidades añadibles en un módulo de odoo para mi formación de prácticas

## Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.


