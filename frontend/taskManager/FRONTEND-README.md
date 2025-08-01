# Task Manager Frontend

Una aplicación Angular para gestión de tareas con autenticación JWT.

## Características

- ✅ **Login seguro** con JWT y soporte para cookies
- 📝 **Gestión completa de tareas** (crear, editar, marcar como completada, eliminar)
- 👤 **Perfil de usuario** con edición de datos y cambio de contraseña
- 🔒 **Guards de autenticación** para proteger rutas
- 🔄 **Interceptor HTTP** para manejo automático de tokens
- 👑 **Funciones de administrador** (gestión de usuarios)
- 🎨 **Interfaz responsive** y moderna
- 📱 **Diseño mobile-first**

## Estructura del Proyecto

```
src/app/
├── components/
│   ├── login/           # Componente de autenticación
│   ├── todo/            # Componente de gestión de tareas
│   └── profile/         # Componente de perfil de usuario
├── models/              # Interfaces TypeScript
│   ├── user.model.ts    # Modelos de usuario
│   └── task.model.ts    # Modelos de tareas
├── services/            # Servicios de datos
│   ├── auth.service.ts  # Servicio de autenticación
│   └── task.service.ts  # Servicio de tareas
├── guards/              # Guards de rutas
│   └── auth.guard.ts    # Guard de autenticación
└── interceptors/        # Interceptores HTTP
    └── auth.interceptor.ts
```

## Endpoints de la API

### Autenticación
- `POST /api/auth/token` - Login con token Bearer
- `POST /api/auth/token-cookie` - Login con cookies
- `POST /api/auth/logout` - Logout
- `GET /api/auth/users/me` - Obtener usuario actual
- `PUT /api/auth/users/me` - Actualizar perfil
- `POST /api/auth/users/me/change-password` - Cambiar contraseña

### Gestión de Usuarios (Admin)
- `GET /api/auth/users` - Listar todos los usuarios
- `POST /api/auth/users` - Crear nuevo usuario
- `PATCH /api/auth/users/{id}/toggle-status` - Habilitar/deshabilitar usuario
- `PATCH /api/auth/users/{id}/toggle-admin` - Otorgar/quitar permisos admin
- `DELETE /api/auth/users/{id}` - Eliminar usuario

### Tareas
- `GET /api/task/` - Obtener tareas del usuario
- `GET /api/task/{id}` - Obtener tarea específica
- `POST /api/task/` - Crear nueva tarea
- `PUT /api/task/{id}` - Actualizar tarea completa
- `PATCH /api/task/{id}/toggle` - Marcar/desmarcar como completada
- `PATCH /api/task/{id}/complete` - Marcar como completada
- `DELETE /api/task/{id}` - Eliminar tarea
- `GET /api/task/stats/summary` - Obtener estadísticas

## Configuración

### 1. URLs de la API

Cambia las URLs base en los servicios:

**auth.service.ts:**
```typescript
private readonly baseUrl = 'http://localhost:8000/api/auth'; // ← Cambia esta URL
```

**task.service.ts:**
```typescript
private readonly baseUrl = 'http://localhost:8000/api/task'; // ← Cambia esta URL
```

### 2. Funcionalidades Adicionales

Los componentes incluyen métodos placeholder para funcionalidades adicionales que puedes implementar:

**En LoginComponent:**
- `navigateToRegister()` - Para ir a página de registro
- `forgotPassword()` - Para recuperación de contraseña

**En TodoComponent:**
- `navigateToProfile()` - ✅ **YA IMPLEMENTADO** - Va al perfil del usuario
- `navigateToSettings()` - Para ir a configuraciones (pendiente de implementar)

## Instalación y Ejecución

### Prerrequisitos
- Node.js 16+
- Angular CLI 15+

### Pasos

1. **Instalar dependencias:**
   ```bash
   npm install
   ```

2. **Ejecutar en desarrollo:**
   ```bash
   ng serve
   ```

3. **Compilar para producción:**
   ```bash
   ng build --prod
   ```

## Uso

### Login
1. Navega a `/login`
2. Ingresa credenciales válidas
3. Serás redirigido automáticamente a `/tasks`

### Gestión de Tareas
- **Nueva tarea:** Clic en "➕ Nueva Tarea"
- **Editar:** Clic en "✏️ Editar" en cualquier tarea
- **Completar:** Clic en "✅ Completar" para marcar como hecha
- **Eliminar:** Clic en "🗑️ Eliminar" (con confirmación)

### Gestión de Perfil
- **Ver perfil:** Clic en "Perfil" desde el dashboard
- **Editar datos:** Email y nombre completo
- **Cambiar contraseña:** Con validación de contraseña actual
- **Ver información:** Tipo de usuario, estado, fechas

### Funciones de Administrador
Si eres administrador, tendrás acceso a funciones adicionales a través del AuthService:
- Listar todos los usuarios
- Crear nuevos usuarios
- Habilitar/deshabilitar usuarios
- Otorgar/quitar permisos de administrador
- Eliminar usuarios

### Características de la Interfaz

- **Dashboard responsivo** con grid de tareas
- **Modales** para crear y editar tareas
- **Estados visuales** para tareas completadas/pendientes
- **Fechas** de creación y actualización
- **Logout** desde cualquier página

## Seguridad

- **JWT Tokens** almacenados en localStorage
- **Auto-logout** en caso de token expirado
- **Guards** protegen rutas autenticadas
- **Interceptor** agrega automáticamente headers de auth
- **Headers CSRF** incluidos para API compatible

## Personalización

### Estilos
Los componentes usan CSS modular. Puedes personalizar:
- Colores en las variables CSS
- Layout responsivo
- Temas y animaciones

### Validaciones
Agrega validaciones adicionales en:
- Formularios de login
- Formularios de tareas
- Campos requeridos

### Estados
Extiende los estados de tareas:
- Prioridades
- Categorías
- Fechas de vencimiento
- Asignaciones

## Notas de Desarrollo

- El proyecto usa **Angular 15** con las últimas características
- **RxJS** para manejo de estado reactivo
- **HttpClient** para comunicación con API
- **FormsModule** para formularios template-driven
- **RouterModule** para navegación

## Próximos Pasos

1. **Cambiar las URLs** de los servicios por las de tu API
2. **Implementar páginas adicionales** (perfil, configuraciones, etc.)
3. **Agregar validaciones** más robustas
4. **Personalizar estilos** según tu marca
5. **Agregar testing** unitario e integración

¡Tu aplicación está lista para funcionar! Solo necesitas conectarla a tu API backend.
