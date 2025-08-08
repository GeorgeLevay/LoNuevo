# Sistema de Rifas - Aplicación Web en Python

Una aplicación web completa para la gestión y venta de rifas online, desarrollada con Python Flask.

## 🚀 Características Principales

### Para Usuarios
- **Registro e Inicio de Sesión**: Sistema de autenticación seguro
- **Explorar Rifas**: Ver todas las rifas activas disponibles
- **Comprar Boletos**: Sistema de compra con múltiples métodos de pago
- **Historial de Compras**: Seguimiento de todas las compras realizadas
- **Notificaciones**: Alertas sobre el estado de las compras

### Para Administradores
- **Panel de Administración**: Dashboard con estadísticas en tiempo real
- **Gestión de Compras**: Aprobar o rechazar compras pendientes
- **Gestión de Rifas**: Crear, editar y eliminar rifas
- **Historial Completo**: Ver todas las transacciones y usuarios
- **Estadísticas**: Métricas detalladas de ventas y participación

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python Flask
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Autenticación**: Flask-Login
- **Formularios**: Flask-WTF
- **ORM**: SQLAlchemy

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd rifa-py
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu-clave-secreta-aqui
FLASK_ENV=development
DATABASE_URL=sqlite:///rifas.db
```

### 5. Ejecutar la Aplicación
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 👤 Credenciales por Defecto

### Usuario Administrador
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Email**: `admin@rifas.com`

⚠️ **Importante**: Cambia estas credenciales después de la primera instalación.

## 📁 Estructura del Proyecto

```
rifa-py/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── index.html        # Página principal
│   ├── login.html        # Página de login
│   ├── register.html     # Página de registro
│   ├── raffle_detail.html # Detalles de rifa
│   ├── my_purchases.html # Mis compras
│   └── admin/            # Plantillas de administración
│       ├── dashboard.html
│       ├── purchases.html
│       ├── raffles.html
│       └── create_raffle.html
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   ├── js/
│   │   └── main.js       # JavaScript principal
│   └── images/           # Imágenes
└── rifas.db             # Base de datos SQLite (se crea automáticamente)
```

## 🎯 Funcionalidades Detalladas

### Sistema de Usuarios
- Registro con validación de email
- Inicio de sesión seguro
- Perfiles de usuario
- Historial de actividades

### Gestión de Rifas
- Crear rifas con imágenes
- Establecer precios y cantidades
- Fechas de finalización
- Estados activo/inactivo

### Sistema de Compras
- Múltiples métodos de pago
- Aprobación manual por administrador
- Notificaciones automáticas
- Historial detallado

### Panel de Administración
- Dashboard con métricas
- Gestión de usuarios
- Aprobación de compras
- Reportes y estadísticas

## 🔒 Seguridad

- Contraseñas hasheadas con bcrypt
- Protección CSRF en formularios
- Validación de entrada de datos
- Control de acceso por roles
- Sesiones seguras

## 🚀 Despliegue en Producción

### Usando Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Usando Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Opción 100% gratuita: Firebase Hosting (estático) + Backend en Render y BD en Supabase

1) Supabase (Postgres gestionado gratis)
- Crea un proyecto en supabase.com
- Copia la URL y credenciales de conexión Postgres
- En `.env` del backend define `DATABASE_URL=postgresql+psycopg://<user>:<pass>@<host>:5432/<db>`

2) Render (servicio gratis para Flask)
- Conecta el repo a Render y crea un Web Service
- En "Build Command": `pip install -r requirements.txt`
- En "Start Command": `gunicorn app:app`
- Variables de entorno: `SECRET_KEY`, `DATABASE_URL`

3) Firebase Hosting
- Solo sirve `static/` y HTML. En `firebase.json` puedes apuntar a tu backend público de Render con rewrites si usas rutas SPA o simplemente enlazar botones a URLs de backend.

Con esto evitas tarjeta/créditos: todo con planes gratuitos (según límites de cada servicio).

### Configuración de Base de Datos
Para producción, se recomienda usar PostgreSQL:
```env
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
```

## 📊 Base de Datos

### Modelos Principales

#### User (Usuario)
- id, username, email, password_hash
- is_admin, created_at
- Relación con Purchase

#### Raffle (Rifa)
- id, title, description, price
- total_tickets, available_tickets
- is_active, created_at, end_date
- Relación con Purchase

#### Purchase (Compra)
- id, user_id, raffle_id
- quantity, total_amount, status
- payment_method, created_at
- approved_at, approved_by

## 🔧 Personalización

### Cambiar Tema
Edita `static/css/style.css` para personalizar colores y estilos.

### Agregar Métodos de Pago
Modifica el formulario en `templates/raffle_detail.html` y la lógica en `app.py`.

### Configurar Notificaciones
Implementa integración con servicios de email o SMS en las funciones de aprobación.

## 🐛 Solución de Problemas

### Error de Base de Datos
```bash
# Eliminar base de datos corrupta
rm rifas.db
# Reiniciar aplicación (se creará automáticamente)
```

### Error de Dependencias
```bash
# Actualizar pip
pip install --upgrade pip
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de Puerto
Si el puerto 5000 está ocupado, cambia en `app.py`:
```python
app.run(debug=True, port=5001)
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al desarrollador principal

## 🔄 Actualizaciones

Para actualizar la aplicación:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Desarrollado con ❤️ usando Python Flask** 