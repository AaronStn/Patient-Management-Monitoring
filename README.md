# Patient-Management-Monitoring
## Descripción general
Aplicación de escritorio desarrollada en Python con Tkinter para la gestión y visualización integral de pacientes hospitalarios. Permite consultar y administrar el historial clínico, visualizar pruebas diagnósticas con alertas visuales según sus valores, agregar nuevas pruebas y analizar la evolución del paciente mediante gráficos interactivos.

## Funcionalidades clave
- Gestión de usuarios:
Visualización completa de pacientes con filtros para buscar por número de historia clínica, nombre o camilla asignada.

- Historial de pruebas clínicas:
Listado ordenable por fecha, valores altos o bajos, con indicación visual (rojo/verde) para detectar resultados fuera de rangos normales.

- Añadir nuevas pruebas:
Formulario para registrar pruebas específicas vinculadas a cada paciente.

- Visualización gráfica avanzada:
Consulta de evolución de pruebas dentro de un rango de fechas definido, mostrando tendencias y progresiones en gráficos.

- Vista por planta y habitación:
Tablas organizadas por planta y habitación, destacando resultados máximos y mínimos en cada camilla, con codificación por colores. Desde allí, acceso rápido a detalles completos, pruebas recientes y gráfico evolutivo del paciente.

## Estructura del proyecto
- Interfaz gráfica: Tkinter

- Manipulación de datos: pandas (Excel como fuente de datos)

- Visualización gráfica: Matplotlib o similar (integrado en Tkinter)

## Requisitos
- Python 3.7+

- Librerías: pandas, openpyxl, matplotlib, tkinter (incluido en Python estándar)

## Futuras mejoras
- Integrar base de datos para mayor rendimiento y escalabilidad.

- Añadir autenticación de usuarios.

- Mejorar usabilidad y diseño de la interfaz.

- Soporte multiplataforma avanzado.
