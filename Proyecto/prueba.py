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

# Variables globales
current_user = None  # objeto Usuario autenticado (Cliente o Entrenador)
entrenadores = []
clientes = []
planes = []
sesiones = []

# --------------------------
# Funciones de la aplicación
# --------------------------

def login_inicial():
    """Solicita credenciales al iniciar la aplicación."""
    global current_user

    # Preguntar si el usuario ya tiene cuenta
    tiene = messagebox.askyesno("Bienvenido al Sistema de Fitness", "¿Tienes una cuenta en el sistema?")
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
                listar_sesiones()
                return
            else:
                messagebox.showinfo("Info", "Registro cancelado. Se solicitará inicio de sesión.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el registro:\n{e}")

    # Intentar iniciar sesión (3 intentos)
    for intento in range(3):
        login = simpledialog.askstring("Inicio de sesión", "ID de usuario (ej: C001, E001):")
        if login is None:
            salir()
            return
        
        # Buscar usuario en las listas
        usuario_encontrado = None
        for cliente in clientes:
            if cliente.id == login.strip():
                usuario_encontrado = cliente
                break
        if not usuario_encontrado:
            for entrenador in entrenadores:
                if entrenador.id == login.strip():
                    usuario_encontrado = entrenador
                    break
        
        if usuario_encontrado:
            current_user = usuario_encontrado
            lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({type(current_user).__name__})")
            ajustar_menu_por_rol()
            listar_sesiones()
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
                                listar_sesiones()
                                return
                        except Exception as e:
                            messagebox.showerror("Error", f"Error durante el registro:\n{e}")
            else:
                messagebox.showerror("Error", "Demasiados intentos fallidos. Saliendo.")
                salir()

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
            user_id = f"C{len(clientes) + 1:03d}"
            usuario = Cliente(user_id, nombre.strip(), email.strip(), nivel.strip() if nivel else "Principiante")
            clientes.append(usuario)
        else:
            especialidad = simpledialog.askstring("Registrar entrenador", "Especialidad:", initialvalue="General")
            experiencia = simpledialog.askinteger("Registrar entrenador", "Años de experiencia:", initialvalue=1)
            user_id = f"E{len(entrenadores) + 1:03d}"
            usuario = Entrenador(user_id, nombre.strip(), email.strip(), 
                               especialidad.strip() if especialidad else "General", 
                               experiencia if experiencia else 1)
            entrenadores.append(usuario)
        
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
        planes.append(plan)
        messagebox.showinfo("OK", f"Plan creado: {plan.nombre}")
        listar_planes()
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear plan:\n{e}")

@requiere_entrenador
def agregar_ejercicio_plan():
    """Agregar ejercicio a un plan existente."""
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
    
    # Crear ejercicio
    tipo_ejercicio = simpledialog.askstring("Tipo de Ejercicio", "Tipo (fuerza/cardio):", initialvalue="fuerza")
    if not tipo_ejercicio:
        return
    
    nombre = simpledialog.askstring("Ejercicio", "Nombre del ejercicio:")
    if not nombre:
        return
    descripcion = simpledialog.askstring("Ejercicio", "Descripción:")
    
    try:
        if tipo_ejercicio.lower() == 'fuerza':
            repeticiones = simpledialog.askinteger("Ejercicio Fuerza", "Repeticiones:", initialvalue=10)
            series = simpledialog.askinteger("Ejercicio Fuerza", "Series:", initialvalue=4)
            peso = simpledialog.askfloat("Ejercicio Fuerza", "Peso (kg):", initialvalue=50.0)
            ejercicio = EjercicioFuerza(nombre.strip(), descripcion.strip() if descripcion else "", 
                                      repeticiones, series, peso)
        else:
            duracion = simpledialog.askinteger("Ejercicio Cardio", "Duración (minutos):", initialvalue=20)
            tipo_cardio = simpledialog.askstring("Ejercicio Cardio", "Tipo de cardio:", initialvalue="CORRER")
            ejercicio = EjercicioCardio(nombre.strip(), descripcion.strip() if descripcion else "", 
                                      duracion, tipo_cardio.strip())
        
        plan.agregar_ejercicio(ejercicio)
        messagebox.showinfo("OK", f"Ejercicio '{ejercicio.nombre}' agregado al plan '{plan.nombre}'")
        listar_planes()
    except Exception as e:
        messagebox.showerror("Error", f"Error al agregar ejercicio:\n{e}")

@requiere_entrenador
def programar_sesion():
    """Programar una sesión de entrenamiento."""
    if not planes:
        messagebox.showwarning("Advertencia", "No hay planes creados.")
        return
    if not clientes:
        messagebox.showwarning("Advertencia", "No hay clientes registrados.")
        return
    
    # Seleccionar cliente
    cliente_nombres = [f"{cliente.nombre} ({cliente.id})" for cliente in clientes]
    cliente_info = simpledialog.askstring("Seleccionar Cliente", 
                                        f"Clientes disponibles: {', '.join(cliente_nombres)}\nIngrese ID o nombre:")
    if not cliente_info:
        return
    
    cliente = next((c for c in clientes if cliente_info.strip() in [c.id, c.nombre]), None)
    if not cliente:
        messagebox.showwarning("Error", "Cliente no encontrado.")
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
    
    try:
        sesion_id = f"S{len(sesiones) + 1:03d}"
        sesion = SesionEntrenamiento(sesion_id, datetime.now(), cliente, current_user, plan)
        sesiones.append(sesion)
        messagebox.showinfo("OK", f"Sesión programada: {sesion_id}\nCliente: {cliente.nombre}\nPlan: {plan.nombre}")
        listar_sesiones()
    except Exception as e:
        messagebox.showerror("Error", f"Error al programar sesión:\n{e}")

@requiere_cliente
def calificar_sesion():
    """Permite a un cliente calificar una sesión completada."""
    sesiones_cliente = [s for s in sesiones if s._SesionEntrenamiento__cliente.id == current_user.id 
                       and s._SesionEntrenamiento__estado == "FINALIZADA"]
    
    if not sesiones_cliente:
        messagebox.showwarning("Advertencia", "No tienes sesiones finalizadas para calificar.")
        return
    
    sesion_info = [f"Sesión {s._SesionEntrenamiento__id} - {s._SesionEntrenamiento__plan.nombre}" 
                   for s in sesiones_cliente]
    sesion_seleccionada = simpledialog.askstring("Seleccionar Sesión", 
                                               f"Sesiones: {', '.join(sesion_info)}\nIngrese ID de sesión:")
    if not sesion_seleccionada:
        return
    
    sesion = next((s for s in sesiones_cliente if s._SesionEntrenamiento__id == sesion_seleccionada.strip()), None)
    if not sesion:
        messagebox.showwarning("Error", "Sesión no encontrada.")
        return
    
    calificacion = simpledialog.askinteger("Calificar Sesión", "Calificación (1-5):", minvalue=1, maxvalue=5)
    if calificacion:
        try:
            current_user.calificar_sesion(sesion, calificacion)
            messagebox.showinfo("OK", f"Sesión calificada con {calificacion} estrellas")
            listar_sesiones()
        except Exception as e:
            messagebox.showerror("Error", f"Error al calificar sesión:\n{e}")

def listar_planes():
    """Listar todos los planes de entrenamiento."""
    lb_output.delete(0, tk.END)
    if not planes:
        lb_output.insert(tk.END, "No hay planes de entrenamiento registrados.")
        return
    
    lb_output.insert(tk.END, "PLANES DE ENTRENAMIENTO:")
    for plan in planes:
        lb_output.insert(tk.END, f"  [{plan.nombre}] - {getattr(plan, '_PlanEntrenamiento__objetivo', 'Sin objetivo')}")
        lb_output.insert(tk.END, f"    Ejercicios: {len(plan.ejercicios)}")
        for i, ejercicio in enumerate(plan.ejercicios, 1):
            lb_output.insert(tk.END, f"      {i}. {ejercicio.nombre}")
        lb_output.insert(tk.END, "")

def listar_sesiones():
    """Listar todas las sesiones de entrenamiento."""
    lb_output.delete(0, tk.END)
    if not sesiones:
        lb_output.insert(tk.END, "No hay sesiones de entrenamiento programadas.")
        return
    
    lb_output.insert(tk.END, "SESIONES DE ENTRENAMIENTO:")
    for sesion in sesiones:
        estado = sesion._SesionEntrenamiento__estado
        calificacion = sesion._SesionEntrenamiento__calificacion
        cliente = sesion._SesionEntrenamiento__cliente.nombre
        entrenador = sesion._SesionEntrenamiento__entrenador.nombre
        plan = sesion._SesionEntrenamiento__plan.nombre
        
        lb_output.insert(tk.END, f"  [{sesion._SesionEntrenamiento__id}] {cliente} con {entrenador}")
        lb_output.insert(tk.END, f"    Plan: {plan} | Estado: {estado} | Calificación: {calificacion}/5")
        lb_output.insert(tk.END, "")

def listar_usuarios():
    """Listar todos los usuarios del sistema."""
    lb_output.delete(0, tk.END)
    if not clientes and not entrenadores:
        lb_output.insert(tk.END, "No hay usuarios registrados.")
        return
    
    lb_output.insert(tk.END, "USUARIOS DEL SISTEMA:")
    
    if entrenadores:
        lb_output.insert(tk.END, "  ENTRENADORES:")
        for entrenador in entrenadores:
            lb_output.insert(tk.END, f"    [{entrenador.id}] {entrenador.nombre} - {entrenador._Entrenador__especialidad}")
    
    if clientes:
        lb_output.insert(tk.END, "  CLIENTES:")
        for cliente in clientes:
            lb_output.insert(tk.END, f"    [{cliente.id}] {cliente.nombre} - Nivel: {cliente.nivel_fitness}")

def simular_entrenamiento():
    """Simular la finalización de una sesión de entrenamiento."""
    if not sesiones:
        messagebox.showwarning("Advertencia", "No hay sesiones programadas.")
        return
    
    sesiones_activas = [s for s in sesiones if s._SesionEntrenamiento__estado == "PROGRAMADA"]
    if not sesiones_activas:
        messagebox.showwarning("Advertencia", "No hay sesiones activas para finalizar.")
        return
    
    sesion_info = [f"Sesión {s._SesionEntrenamiento__id} - {s._SesionEntrenamiento__cliente.nombre}" 
                   for s in sesiones_activas]
    sesion_seleccionada = simpledialog.askstring("Finalizar Sesión", 
                                               f"Sesiones activas: {', '.join(sesion_info)}\nIngrese ID de sesión:")
    if not sesion_seleccionada:
        return
    
    sesion = next((s for s in sesiones_activas if s._SesionEntrenamiento__id == sesion_seleccionada.strip()), None)
    if not sesion:
        messagebox.showwarning("Error", "Sesión no encontrada.")
        return
    
    try:
        sesion.cambiar_estado("FINALIZADA")
        # Agregar al historial del cliente
        sesion._SesionEntrenamiento__cliente.agregar_sesion_historial(sesion)
        messagebox.showinfo("OK", f"Sesión {sesion_seleccionada} finalizada exitosamente")
        listar_sesiones()
    except Exception as e:
        messagebox.showerror("Error", f"Error al finalizar sesión:\n{e}")

def mostrar_dashboard():
    """Mostrar el dashboard del usuario actual."""
    if current_user:
        lb_output.delete(0, tk.END)
        current_user.mostrar_dashboard()
        # Por ahora mostramos información básica
        if isinstance(current_user, Cliente):
            sesiones_cliente = len([s for s in sesiones if s._SesionEntrenamiento__cliente.id == current_user.id])
            lb_output.insert(tk.END, f"DASHBOARD DE {current_user.nombre.upper()}")
            lb_output.insert(tk.END, f"Nivel: {current_user.nivel_fitness}")
            lb_output.insert(tk.END, f"Sesiones completadas: {sesiones_cliente}")
        else:
            planes_entrenador = len([p for p in planes])
            lb_output.insert(tk.END, f"PANEL DE ENTRENADOR: {current_user.nombre.upper()}")
            lb_output.insert(tk.END, f"Especialidad: {current_user._Entrenador__especialidad}")
            lb_output.insert(tk.END, f"Planes creados: {planes_entrenador}")

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
    acciones_menu.entryconfig("Listar usuarios", state="normal")
    acciones_menu.entryconfig("Listar sesiones", state="normal")
    acciones_menu.entryconfig("Listar planes", state="normal")

    # Opciones específicas por rol
    if isinstance(current_user, Entrenador):
        acciones_menu.entryconfig("Crear plan entrenamiento", state="normal")
        acciones_menu.entryconfig("Agregar ejercicio a plan", state="normal")
        acciones_menu.entryconfig("Programar sesión", state="normal")
        acciones_menu.entryconfig("Simular entrenamiento", state="normal")
        acciones_menu.entryconfig("Calificar sesión", state="disabled")
    elif isinstance(current_user, Cliente):
        acciones_menu.entryconfig("Crear plan entrenamiento", state="disabled")
        acciones_menu.entryconfig("Agregar ejercicio a plan", state="disabled")
        acciones_menu.entryconfig("Programar sesión", state="disabled")
        acciones_menu.entryconfig("Simular entrenamiento", state="disabled")
        acciones_menu.entryconfig("Calificar sesión", state="normal")

# --------------------------
# Interfaz gráfica
# --------------------------

root = tk.Tk()
root.title("Fit Coach Pro - Interfaz gráfica")
root.geometry("800x600")
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
acciones_menu.add_separator()
acciones_menu.add_command(label="Listar usuarios", command=listar_usuarios)
acciones_menu.add_command(label="Listar sesiones", command=listar_sesiones)
acciones_menu.add_command(label="Listar planes", command=listar_planes)
menubar.add_cascade(label="Acciones", menu=acciones_menu)

# Menú "Opciones" con Salir
archivo_menu = tk.Menu(menubar, tearoff=0)
archivo_menu.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Opciones", menu=archivo_menu)

root.config(menu=menubar)

# Frame principal para salida / resultados
frame_output = ttk.Frame(root, padding=(12, 12))
frame_output.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

lbl_output = ttk.Label(frame_output, text=f"BIENVENIDO A FIT COACH PRO", font=("Segoe UI", 12, "bold"))
lbl_output.pack(anchor="w")

# Listbox con scrollbar para mostrar resultados
frame_list = ttk.Frame(frame_output)
frame_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

sb = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
lb_output = tk.Listbox(frame_list, yscrollcommand=sb.set, font=("Consolas", 10))
sb.config(command=lb_output.yview)
sb.pack(side=tk.RIGHT, fill=tk.Y)
lb_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Mensaje de ayuda inferior
lbl_help = ttk.Label(frame_output, text="Iniciando sistema de fitness...", font=("Segoe UI", 9))
lbl_help.pack(anchor="w", pady=(8, 0))

# Crear algunos datos de prueba al iniciar
def crear_datos_prueba():
    """Crear datos de prueba para demostración."""
    global entrenadores, clientes
    
    # Entrenador de prueba
    entrenador_test = Entrenador("E001", "Juan Pérez", "juan@gym.com", "Hipertrofia", 5)
    entrenadores.append(entrenador_test)
    
    # Cliente de prueba
    cliente_test = Cliente("C001", "Pedro López", "pedro@mail.com", "Principiante")
    clientes.append(cliente_test)
    
    # Plan de prueba
    plan_test = entrenador_test.crear_plan("Volumen Extremo", "Ganancia muscular máxima")
    planes.append(plan_test)
    
    # Ejercicios de prueba
    press_banca = EjercicioFuerza("Press de Banca", "Empuje horizontal con barra", 10, 4, 60.5)
    cinta_correr = EjercicioCardio("Cinta Correr", "Running suave", 20, "CORRER")
    plan_test.agregar_ejercicio(press_banca)
    plan_test.agregar_ejercicio(cinta_correr)
    
    # Sesión de prueba
    sesion_test = SesionEntrenamiento("S001", datetime.now(), cliente_test, entrenador_test, plan_test)
    sesiones.append(sesion_test)

# Al iniciar, crear datos de prueba y pedir login
root.after(100, lambda: [crear_datos_prueba(), login_inicial()])

root.mainloop()