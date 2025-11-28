import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from cliente import Cliente
from entrenador import Entrenador
from ejercicio_fuerza import EjercicioFuerza
from ejercicio_cardio import EjercicioCardio
from sesion_entrenamiento import SesionEntrenamiento
from plan_entrenamiento import PlanEntrenamiento
from ejercicio import Ejercicio

# Variables globales
current_user = None  # objeto Usuario autenticado (Cliente o Entrenador)

# --------------------------
# Funciones de la aplicación 
# --------------------------

def login_inicial():
    """Solicita credenciales al iniciar la aplicación."""
    global current_user

    # Preguntar si el usuario ya tiene cuenta
    tiene = messagebox.askyesno("Bienvenido a Fit Coach Pro", "¿Tienes una cuenta en el sistema?")
    if tiene is None:
        salir()
        return

    if not tiene:
        # Permitir registro público
        try:
            u = registrar_usuario_publico()
            if u:
                current_user = u
                lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({type(current_user).__name__})")
                ajustar_menu_por_rol()
                mostrar_dashboard()
                return
            else:
                messagebox.showinfo("Info", "Registro cancelado. Se solicitará inicio de sesión.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el registro:\n{e}")

    # Intentar iniciar sesión (3 intentos)
    for intento in range(3):
        user_id_str = simpledialog.askstring("Inicio de sesión", "ID de usuario (número):")
        if user_id_str is None:
            salir()
            return
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
            continue
        
        # Buscar usuario en la base de datos
        try:
            # Buscar como cliente
            usuario = Cliente.buscar_por_id(user_id)
            if not usuario:
                # Buscar como entrenador
                usuario = Entrenador.buscar_por_id(user_id)
            
            if usuario:
                current_user = usuario
                lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({type(current_user).__name__})")
                ajustar_menu_por_rol()
                mostrar_dashboard()
                return
            else:
                if intento < 2:
                    retry = messagebox.askretrycancel("Error", "Usuario no encontrado. ¿Deseas intentar de nuevo?")
                    if not retry:
                        want_reg = messagebox.askyesno("Registro", "¿Deseas registrarte ahora?")
                        if want_reg:
                            try:
                                u = registrar_usuario_publico()
                                if u:
                                    current_user = u
                                    lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({type(current_user).__name__})")
                                    ajustar_menu_por_rol()
                                    mostrar_dashboard()
                                    return
                            except Exception as e:
                                messagebox.showerror("Error", f"Error durante el registro:\n{e}")
                else:
                    messagebox.showerror("Error", "Demasiados intentos fallidos. Saliendo.")
                    salir()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar usuario:\n{e}")

def registrar_usuario_publico():
    """Permite registrar un usuario desde la pantalla de inicio."""
    tipo = simpledialog.askstring("Registrar usuario", "Tipo (cliente/entrenador):", initialvalue="cliente")
    if not tipo:
        return None
    
    tipo = tipo.strip().lower()
    if tipo not in ('cliente', 'entrenador'):
        messagebox.showwarning("Tipo inválido", "Tipo inválido. Se usará 'cliente'.")
        tipo = 'cliente'
    
    nombre = simpledialog.askstring("Registrar usuario", "Nombre completo:")
    if not nombre:
        return None
    
    email = simpledialog.askstring("Registrar usuario", "Email:")
    if not email:
        return None

    try:
        if tipo == 'cliente':
            nivel = simpledialog.askstring("Registrar cliente", "Nivel de fitness:", initialvalue="Principiante")
            usuario = Cliente.crear(
                nombre.strip(), 
                email.strip(), 
                nivel.strip() if nivel else "Principiante"
            )
        else:
            especialidad = simpledialog.askstring("Registrar entrenador", "Especialidad:", initialvalue="General")
            experiencia = simpledialog.askinteger("Registrar entrenador", "Años de experiencia:", initialvalue=1)
            usuario = Entrenador.crear(
                nombre.strip(), 
                email.strip(),
                especialidad.strip() if especialidad else "General", 
                experiencia if experiencia else 1
            )
        
        messagebox.showinfo("OK", f"Usuario registrado: {usuario.nombre} (id={usuario.id})")
        return usuario
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar usuario:\n{e}")
        return None

def requiere_entrenador(func):
    """Decorador para funciones que requieren rol Entrenador."""
    def wrapper(*args, **kwargs):
        if current_user is None or not isinstance(current_user, Entrenador):
            messagebox.showerror("Permisos", "Acción restringida: se requiere usuario Entrenador.")
            return
        return func(*args, **kwargs)
    return wrapper

def requiere_cliente(func):
    """Decorador para funciones que requieren rol Cliente."""
    def wrapper(*args, **kwargs):
        if current_user is None or not isinstance(current_user, Cliente):
            messagebox.showerror("Permisos", "Acción restringida: se requiere usuario Cliente.")
            return
        return func(*args, **kwargs)
    return wrapper

# --- Funciones del sistema ---

@requiere_entrenador
def crear_plan_entrenamiento():
    """Permite a un entrenador crear un plan de entrenamiento."""
    nombre = simpledialog.askstring("Crear Plan", "Nombre del plan:")
    if not nombre:
        return
    objetivo = simpledialog.askstring("Crear Plan", "Objetivo del plan:")
    if not objetivo:
        return
    
    try:
        plan = current_user.crear_plan(nombre.strip(), objetivo.strip())
        messagebox.showinfo("OK", f"Plan creado: {plan.nombre}")
        listar_planes()
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear plan:\n{e}")

@requiere_entrenador
def agregar_ejercicio_plan():
    """Agregar ejercicio a un plan existente - permite seleccionar existentes o crear nuevos."""
    try:
        # Cargar planes del entrenador actual
        planes = current_user.obtener_planes()
        
        if not planes:
            messagebox.showwarning("Advertencia", "No hay planes creados.")
            return
        
        # Seleccionar plan
        plan_nombres = [plan.nombre for plan in planes]
        plan_seleccionado = simpledialog.askstring("Seleccionar Plan", 
                                                 f"Planes disponibles: {', '.join(plan_nombres)}\nIngrese el nombre:")
        if not plan_seleccionado:
            return
        
        plan = next((p for p in planes if p.nombre == plan_seleccionado.strip()), None)
        if not plan:
            messagebox.showwarning("Error", "Plan no encontrado.")
            return
        
        # Preguntar si quiere usar ejercicio existente o crear nuevo
        opcion = messagebox.askyesno(
            "Seleccionar Ejercicio",
            f"Plan seleccionado: {plan.nombre}\n\n"
            f"¿Deseas seleccionar un ejercicio existente?\n\n"
            f"• Sí = Elegir de la lista de ejercicios\n"
            f"• No = Crear un nuevo ejercicio"
        )
        
        if opcion:
            # SELECCIONAR EJERCICIO EXISTENTE
            ejercicios_existentes = Ejercicio.listar_todos()
            
            if not ejercicios_existentes:
                messagebox.showwarning("Advertencia", "No hay ejercicios disponibles en el sistema.")
                return
            
            # Mostrar lista de ejercicios
            lista_ejercicios = [f"{ejercicio.nombre} ({ejercicio.tipo}) - {ejercicio.descripcion}" 
                               for ejercicio in ejercicios_existentes]
            
            ejercicio_seleccionado = simpledialog.askstring(
                "Seleccionar Ejercicio Existente",
                f"Ejercicios disponibles:\n" + "\n".join(lista_ejercicios) + 
                "\n\nIngrese el nombre exacto del ejercicio:"
            )
            
            if not ejercicio_seleccionado:
                return
            
            # Buscar el ejercicio
            ejercicio = Ejercicio.buscar_por_nombre(ejercicio_seleccionado.strip())
            if not ejercicio:
                messagebox.showwarning("Error", "Ejercicio no encontrado.")
                return
            
            # Verificar si el ejercicio ya está en el plan
            ejercicios_plan = [e.nombre for e in plan.ejercicios]
            if ejercicio.nombre in ejercicios_plan:
                messagebox.showwarning("Advertencia", f"El ejercicio '{ejercicio.nombre}' ya está en el plan.")
                return
            
        else:
            # CREAR NUEVO EJERCICIO
            tipo_ejercicio = simpledialog.askstring("Tipo de Ejercicio", "Tipo (fuerza/cardio):", initialvalue="fuerza")
            if not tipo_ejercicio:
                return
            
            nombre = simpledialog.askstring("Nuevo Ejercicio", "Nombre del ejercicio:")
            if not nombre:
                return
            
            descripcion = simpledialog.askstring("Nuevo Ejercicio", "Descripción:", initialvalue="")
            
            # Verificar si ya existe un ejercicio con ese nombre
            ejercicio_existente = Ejercicio.buscar_por_nombre(nombre.strip())
            if ejercicio_existente:
                usar_existente = messagebox.askyesno(
                    "Ejercicio Existente",
                    f"Ya existe un ejercicio con el nombre '{nombre}'.\n\n"
                    f"¿Deseas usar el ejercicio existente en lugar de crear uno nuevo?"
                )
                if usar_existente:
                    ejercicio = ejercicio_existente
                else:
                    messagebox.showinfo("Cancelado", "Por favor, usa un nombre diferente.")
                    return
            else:
                # Crear nuevo ejercicio
                if tipo_ejercicio.lower() == 'fuerza':
                    repeticiones = simpledialog.askinteger("Ejercicio Fuerza", "Repeticiones:", initialvalue=10)
                    series = simpledialog.askinteger("Ejercicio Fuerza", "Series:", initialvalue=4)
                    peso = simpledialog.askfloat("Ejercicio Fuerza", "Peso (kg):", initialvalue=50.0)
                    
                    ejercicio = EjercicioFuerza.crear(
                        nombre.strip(), 
                        descripcion.strip(), 
                        repeticiones, 
                        series, 
                        peso
                    )
                else:
                    duracion = simpledialog.askinteger("Ejercicio Cardio", "Duración (minutos):", initialvalue=20)
                    tipo_cardio = simpledialog.askstring("Ejercicio Cardio", "Tipo de cardio:", initialvalue="CORRER")
                    
                    ejercicio = EjercicioCardio.crear(
                        nombre.strip(), 
                        descripcion.strip(), 
                        duracion, 
                        tipo_cardio.strip()
                    )
        
        # Agregar ejercicio al plan
        plan.agregar_ejercicio(ejercicio)
        
        messagebox.showinfo("Éxito", 
                          f"Ejercicio agregado al plan:\n\n"
                          f"Plan: {plan.nombre}\n"
                          f"Ejercicio: {ejercicio.nombre}\n"
                          f"Tipo: {ejercicio.tipo}\n"
                          f"Descripción: {ejercicio.descripcion}")
        
        listar_planes()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al agregar ejercicio:\n{e}")

def programar_sesion():
    """Programar una sesión de entrenamiento"""
    try:
        # Determinar quién está programando la sesión
        if isinstance(current_user, Entrenador):
            # Entrenador programando sesión - busca cliente
            clientes = Cliente.listar_todos()
            planes = current_user.obtener_planes()
            
            if not planes:
                messagebox.showwarning("Advertencia", "No tienes planes creados. Crea un plan primero.")
                return
            if not clientes:
                messagebox.showwarning("Advertencia", "No hay clientes registrados en el sistema.")
                return
            
            # Seleccionar cliente
            cliente_nombres = [f"{cliente.nombre} (ID: {cliente.id})" for cliente in clientes]
            cliente_info = simpledialog.askstring("Programar Sesión - Seleccionar Cliente", 
                                                f"Clientes disponibles:\n" + "\n".join(cliente_nombres) + "\n\nIngrese ID del cliente:")
            if not cliente_info:
                return
            
            try:
                cliente_id = int(cliente_info)
                cliente = Cliente.buscar_por_id(cliente_id)
            except ValueError:
                messagebox.showerror("Error", "ID debe ser un número")
                return
            
            if not cliente:
                messagebox.showwarning("Error", "Cliente no encontrado.")
                return
            
            # Seleccionar plan del entrenador
            plan_nombres = [plan.nombre for plan in planes]
            plan_seleccionado = simpledialog.askstring("Seleccionar Plan", 
                                                     f"Tus planes disponibles: {', '.join(plan_nombres)}\nIngrese el nombre del plan:")
            if not plan_seleccionado:
                return
            
            plan = next((p for p in planes if p.nombre == plan_seleccionado.strip()), None)
            if not plan:
                messagebox.showwarning("Error", "Plan no encontrado.")
                return
            
            # Entrenador programa sesión para cliente
            entrenador_id = current_user.id
            cliente_id = cliente.id
            
        else:  # Cliente programando sesión - busca entrenador
            entrenadores = Entrenador.listar_todos()
            planes_disponibles = PlanEntrenamiento.listar_todos()  # Todos los planes del sistema
            
            if not entrenadores:
                messagebox.showwarning("Advertencia", "No hay entrenadores registrados en el sistema.")
                return
            
            # Seleccionar entrenador
            entrenador_nombres = [f"{entrenador.nombre} (ID: {entrenador.id}) - {entrenador.especialidad}" 
                                 for entrenador in entrenadores]
            entrenador_info = simpledialog.askstring("Programar Sesión - Seleccionar Entrenador", 
                                                   f"Entrenadores disponibles:\n" + "\n".join(entrenador_nombres) + "\n\nIngrese ID del entrenador:")
            if not entrenador_info:
                return
            
            try:
                entrenador_id = int(entrenador_info)
                entrenador = Entrenador.buscar_por_id(entrenador_id)
            except ValueError:
                messagebox.showerror("Error", "ID debe ser un número")
                return
            
            if not entrenador:
                messagebox.showwarning("Error", "Entrenador no encontrado.")
                return
            
            # Filtrar planes del entrenador seleccionado
            planes_entrenador = [p for p in planes_disponibles if p.id_entrenador == entrenador_id]
            
            if not planes_entrenador:
                messagebox.showwarning("Error", f"El entrenador {entrenador.nombre} no tiene planes creados.")
                return
            
            # Seleccionar plan del entrenador
            plan_nombres = [plan.nombre for plan in planes_entrenador]
            plan_seleccionado = simpledialog.askstring("Seleccionar Plan", 
                                                     f"Planes disponibles de {entrenador.nombre}: {', '.join(plan_nombres)}\nIngrese el nombre del plan:")
            if not plan_seleccionado:
                return
            
            plan = next((p for p in planes_entrenador if p.nombre == plan_seleccionado.strip()), None)
            if not plan:
                messagebox.showwarning("Error", "Plan no encontrado.")
                return
            
            # Cliente programa sesión con entrenador
            cliente_id = current_user.id
            entrenador_id = entrenador.id
        
        # Solicitar fecha y hora de la sesión
        fecha_str = simpledialog.askstring("Fecha de la Sesión", 
                                         "Ingrese fecha y hora:\nEjemplo: 2024-01-15 14:30", 
                                         initialvalue=datetime.now().strftime("%Y-%m-%d %H:%M"))
        if not fecha_str:
            return
        
        try:
            fecha_hora = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
            
            # Verificar que la fecha no sea en el pasado
            if fecha_hora < datetime.now():
                messagebox.showwarning("Error", "No puedes programar sesiones en el pasado.")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use: YYYY-MM-DD HH:MM")
            return
        
        # Crear la sesión
        sesion = SesionEntrenamiento.crear(
            fecha_hora, 
            cliente_id, 
            entrenador_id, 
            plan.id_plan
        )
        
        # Mensaje de confirmación personalizado
        if isinstance(current_user, Entrenador):
            mensaje = f" Sesión programada exitosamente!\n\nID Sesión: {sesion.id}\nCliente: {cliente.nombre}\nPlan: {plan.nombre}\nFecha: {fecha_hora.strftime('%d/%m/%Y %H:%M')}"
        else:
            mensaje = f" Sesión programada exitosamente!\n\nID Sesión: {sesion.id}\nEntrenador: {entrenador.nombre}\nPlan: {plan.nombre}\nFecha: {fecha_hora.strftime('%d/%m/%Y %H:%M')}"
        
        messagebox.showinfo("Sesión Programada", mensaje)
        listar_sesiones()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al programar sesión:\n{e}")


@requiere_cliente
def calificar_sesion():
    """Permite a un cliente calificar una sesión completada."""
    try:
        # Obtener sesiones finalizadas del cliente
        sesiones_cliente = SesionEntrenamiento.buscar_por_cliente(current_user.id)
        sesiones_finalizadas = [s for s in sesiones_cliente if s.estado == "FINALIZADA"]
        
        if not sesiones_finalizadas:
            messagebox.showwarning("Advertencia", "No tienes sesiones finalizadas para calificar.")
            return
        
        sesion_info = [f"Sesión {s.id} - {s.plan.nombre} ({s.fecha_hora.strftime('%Y-%m-%d')})" 
                       for s in sesiones_finalizadas]
        sesion_seleccionada = simpledialog.askstring("Seleccionar Sesión", 
                                                   f"Sesiones finalizadas:\n" + "\n".join(sesion_info) + "\n\nIngrese ID de sesión:")
        if not sesion_seleccionada:
            return
        
        try:
            sesion_id = int(sesion_seleccionada)
            sesion = SesionEntrenamiento.buscar_por_id(sesion_id)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
            return
        
        if not sesion or sesion.cliente.id != current_user.id:
            messagebox.showwarning("Error", "Sesión no encontrada.")
            return
        
        calificacion = simpledialog.askinteger("Calificar Sesión", "Calificación (1-5):", minvalue=1, maxvalue=5)
        if calificacion:
            try:
                sesion.calificar(calificacion)
                messagebox.showinfo("OK", f"Sesión calificada con {calificacion} estrellas")
                listar_sesiones()
            except Exception as e:
                messagebox.showerror("Error", f"Error al calificar sesión:\n{e}")
                
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener sesiones:\n{e}")

def listar_planes():
    """Listar todos los planes de entrenamiento."""
    lb_output.delete(0, tk.END)
    try:
        planes = PlanEntrenamiento.listar_todos()
        
        if not planes:
            lb_output.insert(tk.END, "No hay planes de entrenamiento registrados.")
            return
        
        lb_output.insert(tk.END, "PLANES DE ENTRENAMIENTO:")
        for plan in planes:
            lb_output.insert(tk.END, f"  [{plan.nombre}] - {plan.objetivo}")
            lb_output.insert(tk.END, f"    Entrenador: ID {plan.id_entrenador} | Ejercicios: {len(plan.ejercicios)}")
            for i, ejercicio in enumerate(plan.ejercicios, 1):
                lb_output.insert(tk.END, f"      {i}. {ejercicio.nombre} ({ejercicio.tipo})")
            lb_output.insert(tk.END, "")
            
    except Exception as e:
        lb_output.insert(tk.END, f"Error al cargar planes: {e}")

def listar_sesiones():
    """Listar todas las sesiones de entrenamiento."""
    lb_output.delete(0, tk.END)
    try:
        sesiones = SesionEntrenamiento.listar_todas()
        
        if not sesiones:
            lb_output.insert(tk.END, "No hay sesiones de entrenamiento programadas.")
            return
        
        lb_output.insert(tk.END, "SESIONES DE ENTRENAMIENTO:")
        for sesion in sesiones:
            lb_output.insert(tk.END, f"  [ID: {sesion.id}] {sesion.cliente.nombre} con {sesion.entrenador.nombre}")
            lb_output.insert(tk.END, f"    Plan: {sesion.plan.nombre} | Estado: {sesion.estado} | Calificación: {sesion.calificacion}/5")
            lb_output.insert(tk.END, f"    Fecha: {sesion.fecha_hora.strftime('%Y-%m-%d %H:%M')}")
            lb_output.insert(tk.END, "")
            
    except Exception as e:
        lb_output.insert(tk.END, f"Error al cargar sesiones: {e}")

def listar_usuarios():
    """Listar todos los usuarios del sistema."""
    lb_output.delete(0, tk.END)
    try:
        clientes = Cliente.listar_todos()
        entrenadores = Entrenador.listar_todos()
        
        if not clientes and not entrenadores:
            lb_output.insert(tk.END, "No hay usuarios registrados.")
            return
        
        lb_output.insert(tk.END, "USUARIOS DEL SISTEMA:")
        
        if entrenadores:
            lb_output.insert(tk.END, "  ENTRENADORES:")
            for entrenador in entrenadores:
                lb_output.insert(tk.END, f"    [ID: {entrenador.id}] {entrenador.nombre} - {entrenador.especialidad} ({entrenador.anos_experiencia} años exp.)")
        
        if clientes:
            lb_output.insert(tk.END, "  CLIENTES:")
            for cliente in clientes:
                lb_output.insert(tk.END, f"    [ID: {cliente.id}] {cliente.nombre} - Nivel: {cliente.nivel_fitness}")
                
    except Exception as e:
        lb_output.insert(tk.END, f"Error al cargar usuarios: {e}")

def simular_entrenamiento():
    """Simular la finalización de una sesión de entrenamiento."""
    try:
        sesiones = SesionEntrenamiento.listar_todas()
        sesiones_activas = [s for s in sesiones if s.estado == "PROGRAMADA"]
        
        if not sesiones_activas:
            messagebox.showwarning("Advertencia", "No hay sesiones activas para finalizar.")
            return
        
        sesion_info = [f"Sesión {s.id} - {s.cliente.nombre} ({s.fecha_hora.strftime('%Y-%m-%d')})" 
                       for s in sesiones_activas]
        sesion_seleccionada = simpledialog.askstring("Finalizar Sesión", 
                                                   f"Sesiones activas:\n" + "\n".join(sesion_info) + "\n\nIngrese ID de sesión:")
        if not sesion_seleccionada:
            return
        
        try:
            sesion_id = int(sesion_seleccionada)
            sesion = SesionEntrenamiento.buscar_por_id(sesion_id)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
            return
        
        if not sesion or sesion.estado != "PROGRAMADA":
            messagebox.showwarning("Error", "Sesión no encontrada o no está programada.")
            return
        
        try:
            sesion.cambiar_estado("FINALIZADA")
            messagebox.showinfo("OK", f"Sesión {sesion_id} finalizada exitosamente")
            listar_sesiones()
        except Exception as e:
            messagebox.showerror("Error", f"Error al finalizar sesión:\n{e}")
            
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar sesiones:\n{e}")

def mostrar_dashboard():
    """Mostrar el dashboard del usuario actual."""
    if current_user:
        lb_output.delete(0, tk.END)
        try:
            if isinstance(current_user, Cliente):
                sesiones = SesionEntrenamiento.buscar_por_cliente(current_user.id)
                sesiones_completadas = len([s for s in sesiones if s.estado == 'FINALIZADA'])
                
                lb_output.insert(tk.END, f"DASHBOARD DE {current_user.nombre.upper()}")
                lb_output.insert(tk.END, f"Nivel: {current_user.nivel_fitness}")
                lb_output.insert(tk.END, f"Sesiones completadas: {sesiones_completadas}")
                lb_output.insert(tk.END, f"Total de sesiones: {len(sesiones)}")
                lb_output.insert(tk.END, f"Email: {current_user.email}")
                
            else:  # Entrenador
                planes = current_user.obtener_planes()
                sesiones = current_user.obtener_sesiones()
                
                lb_output.insert(tk.END, f"PANEL DE ENTRENADOR: {current_user.nombre.upper()}")
                lb_output.insert(tk.END, f"Especialidad: {current_user.especialidad}")
                lb_output.insert(tk.END, f"Experiencia: {current_user.anos_experiencia} años")
                lb_output.insert(tk.END, f"Planes creados: {len(planes)}")
                lb_output.insert(tk.END, f"Sesiones programadas: {len(sesiones)}")
                lb_output.insert(tk.END, f"Email: {current_user.email}")
                
        except Exception as e:
            lb_output.insert(tk.END, f"Error al cargar dashboard: {e}")

@requiere_entrenador
def eliminar_usuario():
    """Permite a un entrenador eliminar cualquier usuario del sistema, manejando sesiones relacionadas."""
    try:
        # Cargar todos los usuarios del sistema
        clientes = Cliente.listar_todos()
        entrenadores = Entrenador.listar_todos()
        
        if not clientes and not entrenadores:
            messagebox.showwarning("Advertencia", "No hay usuarios registrados en el sistema.")
            return
        
        # Crear lista combinada de usuarios
        todos_usuarios = []
        for cliente in clientes:
            # Contar sesiones del cliente
            sesiones_cliente = SesionEntrenamiento.buscar_por_cliente(cliente.id)
            sesiones_activas = [s for s in sesiones_cliente if s.estado != 'FINALIZADA']
            
            todos_usuarios.append({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'email': cliente.email,
                'tipo': 'CLIENTE',
                'info_adicional': f"Nivel: {cliente.nivel_fitness} | Sesiones activas: {len(sesiones_activas)}"
            })
        
        for entrenador in entrenadores:
            # Contar sesiones del entrenador
            sesiones_entrenador = SesionEntrenamiento.buscar_por_entrenador(entrenador.id)
            sesiones_activas = [s for s in sesiones_entrenador if s.estado != 'FINALIZADA']
            planes_entrenador = entrenador.obtener_planes()
            
            todos_usuarios.append({
                'id': entrenador.id,
                'nombre': entrenador.nombre,
                'email': entrenador.email,
                'tipo': 'ENTRENADOR',
                'info_adicional': f"Especialidad: {entrenador.especialidad} | Planes: {len(planes_entrenador)} | Sesiones activas: {len(sesiones_activas)}"
            })
        
        # Mostrar lista de usuarios
        lista_usuarios = [f"ID: {user['id']} | {user['nombre']} ({user['tipo']}) - {user['info_adicional']}" 
                         for user in todos_usuarios]
        
        usuario_info = simpledialog.askstring("Eliminar Usuario", 
                                            f"Usuarios del sistema:\n" + "\n".join(lista_usuarios) + 
                                            "\n\nIngrese ID del usuario a eliminar:")
        if not usuario_info:
            return
        
        try:
            usuario_id = int(usuario_info)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
            return
        
        # Buscar el usuario
        usuario_a_eliminar = None
        tipo_usuario = None
        
        # Buscar como cliente primero
        usuario_a_eliminar = Cliente.buscar_por_id(usuario_id)
        if usuario_a_eliminar:
            tipo_usuario = 'CLIENTE'
        else:
            # Buscar como entrenador
            usuario_a_eliminar = Entrenador.buscar_por_id(usuario_id)
            if usuario_a_eliminar:
                tipo_usuario = 'ENTRENADOR'
        
        if not usuario_a_eliminar:
            messagebox.showwarning("Error", "Usuario no encontrado.")
            return
        
        # Verificar que no se está intentando eliminar a sí mismo
        if usuario_a_eliminar.id == current_user.id:
            messagebox.showwarning("Error", "No puedes eliminarte a ti mismo.")
            return
        
        # Obtener información de sesiones para mostrar en la confirmación
        sesiones_usuario = []
        if tipo_usuario == 'CLIENTE':
            sesiones_usuario = SesionEntrenamiento.buscar_por_cliente(usuario_id)
        else:  # ENTRENADOR
            sesiones_usuario = SesionEntrenamiento.buscar_por_entrenador(usuario_id)
        
        sesiones_activas = [s for s in sesiones_usuario if s.estado != 'FINALIZADA']
        sesiones_finalizadas = [s for s in sesiones_usuario if s.estado == 'FINALIZADA']
        
        # Confirmación de eliminación con información detallada
        mensaje_confirmacion = (
            f"¿Estás seguro de que deseas eliminar al siguiente usuario?\n\n"
            f"ID: {usuario_a_eliminar.id}\n"
            f"Nombre: {usuario_a_eliminar.nombre}\n"
            f"Email: {usuario_a_eliminar.email}\n"
            f"Tipo: {tipo_usuario}\n"
            f"Sesiones activas: {len(sesiones_activas)}\n"
            f"Sesiones finalizadas: {len(sesiones_finalizadas)}\n\n"
            f" Esta acción eliminará TODAS las sesiones del usuario.\n"
            f" Esta acción no se puede deshacer."
        )
        
        confirmacion = messagebox.askyesno("Confirmar Eliminación", mensaje_confirmacion)
        
        if not confirmacion:
            return
        
        # Eliminar el usuario y sus sesiones
        try:
            from db_connection import create_connection
            conn = create_connection()
            cursor = conn.cursor()
            
            try:
                if tipo_usuario == 'CLIENTE':
                    # Para cliente: eliminar sesiones primero, luego el cliente
                    if sesiones_usuario:
                        # Eliminar todas las sesiones del cliente
                        cursor.execute("DELETE FROM sesion_entrenamiento WHERE id_cliente = %s", (usuario_id,))
                    
                    # Eliminar de tabla cliente (cascade eliminará de usuario)
                    cursor.execute("DELETE FROM cliente WHERE id_usuario = %s", (usuario_id,))
                    
                else:  # ENTRENADOR
                    # Para entrenador: manejar planes y sesiones primero
                    
                    # Verificar si el entrenador tiene planes creados
                    cursor.execute("SELECT COUNT(*) FROM plan_entrenamiento WHERE id_entrenador = %s", (usuario_id,))
                    tiene_planes = cursor.fetchone()[0] > 0
                    
                    if tiene_planes:
                        # Preguntar qué hacer con los planes
                        opcion_planes = messagebox.askyesno(
                            "Planes del Entrenador",
                            f"El entrenador {usuario_a_eliminar.nombre} tiene planes creados.\n\n"
                            f"¿Deseas eliminar también todos sus planes?\n\n"
                            f"Si seleccionas 'No', la eliminación se cancelará."
                        )
                        
                        if opcion_planes:
                            # Eliminar planes del entrenador (cascade eliminará las sesiones relacionadas)
                            cursor.execute("DELETE FROM plan_entrenamiento WHERE id_entrenador = %s", (usuario_id,))
                        else:
                            messagebox.showinfo("Cancelado", "Eliminación cancelada.")
                            return
                    else:
                        # Si no tiene planes, eliminar sus sesiones directamente
                        if sesiones_usuario:
                            cursor.execute("DELETE FROM sesion_entrenamiento WHERE id_entrenador = %s", (usuario_id,))
                    
                    # Eliminar de tabla entrenador
                    cursor.execute("DELETE FROM entrenador WHERE id_usuario = %s", (usuario_id,))
                
                conn.commit()
                
                # Mensaje de éxito con resumen
                mensaje_exito = (
                    f" Usuario eliminado correctamente:\n\n"
                    f"Nombre: {usuario_a_eliminar.nombre}\n"
                    f"Tipo: {tipo_usuario}\n"
                    f"Sesiones eliminadas: {len(sesiones_usuario)}\n"
                )
                
                if tipo_usuario == 'ENTRENADOR' and tiene_planes:
                    mensaje_exito += f"Planes eliminados: {tiene_planes}\n"
                
                messagebox.showinfo("Éxito", mensaje_exito)
                listar_usuarios()  # Actualizar la lista
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{e}")
            
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar la eliminación:\n{e}")

@requiere_entrenador
def actualizar_nivel_cliente():
    """Permite a un entrenador actualizar el nivel de fitness de un cliente."""
    try:
        # Obtener clientes que ha entrenado este entrenador
        clientes = current_user.obtener_clientes_entrenados()
        
        if not clientes:
            messagebox.showwarning("Advertencia", "No tienes clientes asignados.")
            return
        
        # Mostrar lista de clientes
        lista_clientes = [f"ID: {cliente.id} | {cliente.nombre} - Nivel actual: {cliente.nivel_fitness}" 
                         for cliente in clientes]
        
        cliente_info = simpledialog.askstring("Actualizar Nivel de Cliente", 
                                            f"Tus clientes:\n" + "\n".join(lista_clientes) + 
                                            "\n\nIngrese ID del cliente:")
        if not cliente_info:
            return
        
        try:
            cliente_id = int(cliente_info)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
            return
        
        # Verificar que el cliente existe y es entrenado por este entrenador
        cliente = next((c for c in clientes if c.id == cliente_id), None)
        if not cliente:
            messagebox.showwarning("Error", "Cliente no encontrado o no es entrenado por ti.")
            return
        
        # Mostrar niveles disponibles
        niveles = ["Principiante", "Intermedio", "Avanzado", "Experto"]
        nivel_seleccionado = simpledialog.askstring("Seleccionar Nuevo Nivel", 
                                                  f"Cliente: {cliente.nombre}\n"
                                                  f"Nivel actual: {cliente.nivel_fitness}\n\n"
                                                  f"Niveles disponibles: {', '.join(niveles)}\n"
                                                  f"Ingrese el nuevo nivel:")
        if not nivel_seleccionado:
            return
        
        nivel_seleccionado = nivel_seleccionado.strip().capitalize()
        if nivel_seleccionado not in niveles:
            messagebox.showerror("Error", f"Nivel inválido. Debe ser uno de: {', '.join(niveles)}")
            return
        
        # Actualizar el nivel
        cliente_actualizado = current_user.actualizar_nivel_cliente(cliente_id, nivel_seleccionado)
        
        messagebox.showinfo("Éxito", 
                          f"Nivel actualizado correctamente:\n\n"
                          f"Cliente: {cliente_actualizado.nombre}\n"
                          f"Nuevo nivel: {cliente_actualizado.nivel_fitness}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar nivel del cliente:\n{e}")

def salir():
    root.destroy()
    sys.exit(0)

def ajustar_menu_por_rol():
    """Habilita/deshabilita opciones del menú según el rol del usuario actual."""
    if current_user is None:
        # Deshabilitar todo
        for i in range(acciones_menu.index("end") + 1):
            acciones_menu.entryconfig(i, state="disabled")
        return

    # Habilitar opciones comunes
    acciones_menu.entryconfig("Mostrar dashboard", state="normal")
    acciones_menu.entryconfig("Listar sesiones", state="normal")
    acciones_menu.entryconfig("Listar planes", state="normal")

    # Opciones específicas por rol
    if isinstance(current_user, Entrenador):
        acciones_menu.entryconfig("Crear plan entrenamiento", state="normal")
        acciones_menu.entryconfig("Agregar ejercicio a plan", state="normal")
        acciones_menu.entryconfig("Programar sesión", state="normal")
        acciones_menu.entryconfig("Simular entrenamiento", state="normal")
        acciones_menu.entryconfig("Actualizar nivel cliente", state="normal")
        acciones_menu.entryconfig("Eliminar usuario", state="normal")
        acciones_menu.entryconfig("Calificar sesión", state="disabled")
        acciones_menu.entryconfig("Listar usuarios", state="normal")
        opciones_menu.entryconfig("Agregar usuario", state="normal")
    elif isinstance(current_user, Cliente):
        acciones_menu.entryconfig("Crear plan entrenamiento", state="disabled")
        acciones_menu.entryconfig("Agregar ejercicio a plan", state="disabled")
        acciones_menu.entryconfig("Programar sesión", state="normal")
        acciones_menu.entryconfig("Simular entrenamiento", state="disabled")
        acciones_menu.entryconfig("Actualizar nivel cliente", state="disabled")
        acciones_menu.entryconfig("Eliminar usuario", state="disabled")
        acciones_menu.entryconfig("Calificar sesión", state="normal")
        acciones_menu.entryconfig("Listar usuarios", state="disabled")
        opciones_menu.entryconfig("Agregar usuario", state="disabled")

# --------------------------
# Interfaz gráfica
# --------------------------

root = tk.Tk()
root.title("Fit Coach Pro - Interfaz gráfica")
root.geometry("600x400")
root.minsize(700, 500)


# Menú principal
menubar = tk.Menu(root)

# Menú "Acciones" con las opciones
acciones_menu = tk.Menu(menubar, tearoff=0)
acciones_menu.add_command(label="Mostrar dashboard", command=mostrar_dashboard)
acciones_menu.add_separator()
acciones_menu.add_command(label="Crear plan entrenamiento", command=crear_plan_entrenamiento)
acciones_menu.add_command(label="Agregar ejercicio a plan", command=agregar_ejercicio_plan)
acciones_menu.add_command(label="Programar sesión", command=programar_sesion)
acciones_menu.add_separator()
acciones_menu.add_command(label="Simular entrenamiento", command=simular_entrenamiento)
acciones_menu.add_command(label="Calificar sesión", command=calificar_sesion)
acciones_menu.add_command(label="Eliminar usuario", command=eliminar_usuario)
acciones_menu.add_command(label="Actualizar nivel cliente", command=actualizar_nivel_cliente)
acciones_menu.add_separator()
acciones_menu.add_command(label="Listar usuarios", command=listar_usuarios)
acciones_menu.add_command(label="Listar sesiones", command=listar_sesiones)
acciones_menu.add_command(label="Listar planes", command=listar_planes)
menubar.add_cascade(label="¿Qué quieres hacer hoy?", menu=acciones_menu)

# Menú "Opciones" con Salir
opciones_menu = tk.Menu(menubar, tearoff=0)
opciones_menu.add_command(label="Agregar usuario", command=registrar_usuario_publico)
opciones_menu.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Opciones", menu=opciones_menu)

root.config(menu=menubar, bg="black")

# Frame principal para salida / resultados
frame_output = tk.Frame(root, bg="#7D3C98", padx=12, pady=12)
frame_output.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

lbl_output = tk.Label(frame_output, text="Bienvenido a FIT COACH PRO", font=("Segoe UI", 12, "normal"), bg="#7D3C98", fg="white")
lbl_output.pack(anchor="w")

# Listbox con scrollbar para mostrar resultados
frame_list = ttk.Frame(frame_output)
frame_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

sb = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
lb_output = tk.Listbox(frame_list, yscrollcommand=sb.set, font=("Consolas", 10), bg="#ccff33")
sb.config(command=lb_output.yview)
sb.pack(side=tk.RIGHT, fill=tk.Y)
lb_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Mensaje de ayuda inferior
lbl_help = tk.Label(frame_output, text="Iniciando sistema espere un poco pliiiis...", font=("Segoe UI", 9),bg="#7D3C98")
lbl_help.pack(anchor="w", pady=(8, 0))

# Al iniciar, pedir login directamente 
root.after(100, login_inicial)

root.mainloop()