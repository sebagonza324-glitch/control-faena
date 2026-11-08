"""Interfaz gráfica para administrar trabajadores y turnos."""

import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk
from tkinter import simpledialog

from mysql.connector import Error

from src.db.maintenance import limpiar_base_datos
from src.repositories.trabajador_repo import (
    RutDuplicadoError,
    actualizar_trabajador,
    crear_trabajador,
    listar_trabajadores,
)
from src.repositories.turno_repo import (
    SinTurnoAbiertoError,
    TrabajadorNoExisteError,
    TurnoAbiertoError,
    iniciar_turno as iniciar_turno_repo,
    listar_turnos_activos,
    registrar_salida as registrar_salida_repo,
)
from src.utils.rut import RutInvalidoError


class App:
    """Ventana principal de Control de Faena."""

    def __init__(self, root: tk.Tk) -> None:
        """Configura la ventana y sus pestañas."""
        self.root = root
        self.root.title("Control de Faena")
        self.root.geometry("900x560")
        self.root.minsize(720, 440)

        estilo = ttk.Style(root)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        self.pestana_trabajadores = ttk.Frame(self.notebook, padding=24)
        self.pestana_turnos = ttk.Frame(self.notebook, padding=24)
        self.pestana_activos = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(self.pestana_trabajadores, text="Trabajadores")
        self.notebook.add(self.pestana_turnos, text="Turnos")
        self.notebook.add(self.pestana_activos, text="Turnos activos")

        self._crear_pestana_trabajadores()
        self._crear_pestana_turnos()
        self._crear_pestana_activos()
        self.notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)
        pie = ttk.Frame(root, padding=(16, 0, 16, 12))
        pie.pack(fill=tk.X)
        ttk.Button(
            pie,
            text="Limpiar base de datos",
            command=self.limpiar_base_datos,
        ).pack(side=tk.RIGHT)

    def _crear_pestana_trabajadores(self) -> None:
        """Crea los campos y controles de trabajadores."""
        self.rut_trabajador = tk.StringVar()
        self.nombre_trabajador = tk.StringVar()
        self.cargo_trabajador = tk.StringVar()
        self.filtro_rut_trabajador = tk.StringVar()
        self.rut_trabajador_original: str | None = None
        self.editando_trabajador = False

        ttk.Label(self.pestana_trabajadores, text="RUT").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.entrada_rut_trabajador = ttk.Entry(
            self.pestana_trabajadores, textvariable=self.rut_trabajador, width=40
        )
        self.entrada_rut_trabajador.grid(row=0, column=1, sticky="ew", pady=8)

        ttk.Label(self.pestana_trabajadores, text="Nombre").grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.entrada_nombre_trabajador = ttk.Entry(
            self.pestana_trabajadores, textvariable=self.nombre_trabajador, width=40
        )
        self.entrada_nombre_trabajador.grid(row=1, column=1, sticky="ew", pady=8)

        ttk.Label(self.pestana_trabajadores, text="Cargo (opcional)").grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.entrada_cargo_trabajador = ttk.Entry(
            self.pestana_trabajadores, textvariable=self.cargo_trabajador, width=40
        )
        self.entrada_cargo_trabajador.grid(row=2, column=1, sticky="ew", pady=8)

        acciones = ttk.Frame(self.pestana_trabajadores)
        acciones.grid(row=3, column=1, sticky="e", pady=(12, 8))
        self.boton_accion_trabajador = ttk.Button(
            acciones,
            text="Registrar",
            command=self.registrar_trabajador,
        )
        self.boton_accion_trabajador.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(
            acciones, text="Nuevo", command=self.nuevo_trabajador
        ).pack(side=tk.LEFT)

        ttk.Label(self.pestana_trabajadores, text="Buscar por RUT").grid(
            row=4, column=0, sticky="w", pady=(12, 6)
        )
        busqueda = ttk.Frame(self.pestana_trabajadores)
        busqueda.grid(row=4, column=1, sticky="ew", pady=(12, 6))
        self.entrada_filtro_rut = ttk.Entry(
            busqueda, textvariable=self.filtro_rut_trabajador
        )
        self.entrada_filtro_rut.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            busqueda,
            text="Limpiar búsqueda",
            command=self.limpiar_busqueda_trabajadores,
        ).pack(side=tk.LEFT, padx=(8, 0))
        self.entrada_filtro_rut.bind(
            "<KeyRelease>", self._filtrar_trabajadores
        )

        columnas = ("rut", "nombre", "cargo")
        self.tabla_trabajadores = ttk.Treeview(
            self.pestana_trabajadores,
            columns=columnas,
            show="headings",
            height=8,
        )
        for columna, titulo, ancho in (
            ("rut", "RUT", 180),
            ("nombre", "Nombre", 260),
            ("cargo", "Cargo", 220),
        ):
            self.tabla_trabajadores.heading(columna, text=titulo)
            self.tabla_trabajadores.column(
                columna, width=ancho, anchor="w", stretch=True
            )
        self.tabla_trabajadores.grid(
            row=5, column=0, columnspan=2, sticky="nsew", pady=(6, 0)
        )
        self.tabla_trabajadores.bind(
            "<<TreeviewSelect>>", self._seleccionar_trabajador
        )
        self.pestana_trabajadores.columnconfigure(1, weight=1)
        self.pestana_trabajadores.rowconfigure(5, weight=1)
        for entrada in (
            self.entrada_rut_trabajador,
            self.entrada_nombre_trabajador,
            self.entrada_cargo_trabajador,
        ):
            entrada.bind("<Return>", self._al_presionar_enter_trabajador)
        self.actualizar_lista_trabajadores()

    def _crear_pestana_turnos(self) -> None:
        """Crea los controles para iniciar y cerrar turnos."""
        self.rut_turno = tk.StringVar()
        ttk.Label(self.pestana_turnos, text="RUT").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.entrada_rut_turno = ttk.Entry(
            self.pestana_turnos, textvariable=self.rut_turno, width=40
        )
        self.entrada_rut_turno.grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Button(
            self.pestana_turnos,
            text="Iniciar turno",
            command=self.iniciar_turno,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=16)
        ttk.Button(
            self.pestana_turnos,
            text="Registrar salida",
            command=self.registrar_salida,
        ).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=16)
        self.pestana_turnos.columnconfigure(1, weight=1)
        self.entrada_rut_turno.bind("<Return>", self._al_presionar_enter_turnos)

    def _crear_pestana_activos(self) -> None:
        """Crea la tabla y los controles de turnos activos."""
        columnas = ("rut", "nombre", "cargo", "inicio")
        self.tabla_turnos = ttk.Treeview(
            self.pestana_activos, columns=columnas, show="headings", height=16
        )
        encabezados = {
            "rut": "Rut",
            "nombre": "Nombre",
            "cargo": "Cargo",
            "inicio": "Inicio",
        }
        anchos = {"rut": 150, "nombre": 220, "cargo": 180, "inicio": 180}
        for columna in columnas:
            self.tabla_turnos.heading(columna, text=encabezados[columna])
            self.tabla_turnos.column(
                columna, width=anchos[columna], anchor="w", stretch=True
            )
        self.tabla_turnos.pack(fill=tk.BOTH, expand=True)

        controles = ttk.Frame(self.pestana_activos)
        controles.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(
            controles, text="Actualizar", command=self.actualizar_turnos_activos
        ).pack(side=tk.RIGHT)
        self.etiqueta_personas = ttk.Label(controles, text="Personas en faena: 0")
        self.etiqueta_personas.pack(side=tk.LEFT)

    def registrar_trabajador(self) -> None:
        """Valida y registra un trabajador."""
        rut = self.rut_trabajador.get().strip()
        nombre = self.nombre_trabajador.get().strip()
        cargo = self.cargo_trabajador.get().strip() or None
        if not rut:
            messagebox.showwarning("Dato requerido", "Ingrese el RUT.", parent=self.root)
            self.entrada_rut_trabajador.focus_set()
            return
        if not nombre:
            messagebox.showwarning(
                "Dato requerido", "Ingrese el nombre.", parent=self.root
            )
            self.entrada_nombre_trabajador.focus_set()
            return

        try:
            id_trabajador = crear_trabajador(rut, nombre, cargo)
        except RutInvalidoError:
            messagebox.showwarning(
                "RUT inválido",
                "Ingrese un RUT chileno válido.",
                parent=self.root,
            )
            return
        except RutDuplicadoError:
            messagebox.showwarning(
                "RUT duplicado",
                "Ya existe un trabajador registrado con ese RUT.",
                parent=self.root,
            )
            return
        except Error:
            self._mostrar_error_base_datos()
            return

        self.rut_trabajador.set("")
        self.nombre_trabajador.set("")
        self.cargo_trabajador.set("")
        self.nuevo_trabajador()
        self.actualizar_lista_trabajadores()
        messagebox.showinfo(
            "Registro exitoso",
            f"Trabajador registrado correctamente (ID: {id_trabajador}).",
            parent=self.root,
        )

    def guardar_cambios_trabajador(self) -> None:
        """Guarda el nombre y cargo del trabajador seleccionado."""
        rut = self.rut_trabajador_original
        nombre = self.nombre_trabajador.get().strip()
        cargo = self.cargo_trabajador.get().strip() or None
        if rut is None:
            self.nuevo_trabajador()
            return
        if not nombre:
            messagebox.showwarning(
                "Dato requerido", "Ingrese el nombre.", parent=self.root
            )
            self.entrada_nombre_trabajador.focus_set()
            return

        try:
            actualizar_trabajador(rut, nombre, cargo)
        except RutInvalidoError:
            messagebox.showwarning(
                "RUT inválido",
                "El RUT del trabajador seleccionado no es válido.",
                parent=self.root,
            )
            return
        except TrabajadorNoExisteError:
            messagebox.showwarning(
                "Trabajador no encontrado",
                "El trabajador seleccionado ya no existe.",
                parent=self.root,
            )
            self.nuevo_trabajador()
            self.actualizar_lista_trabajadores()
            return
        except Error:
            self._mostrar_error_base_datos()
            return

        self.nuevo_trabajador()
        self.actualizar_lista_trabajadores()
        messagebox.showinfo(
            "Cambios guardados",
            "Los datos del trabajador se actualizaron correctamente.",
            parent=self.root,
        )

    def nuevo_trabajador(self) -> None:
        """Limpia el formulario y vuelve al modo de registro."""
        self.editando_trabajador = False
        self.rut_trabajador_original = None
        self.rut_trabajador.set("")
        self.nombre_trabajador.set("")
        self.cargo_trabajador.set("")
        self.entrada_rut_trabajador.configure(state="normal")
        self.boton_accion_trabajador.configure(
            text="Registrar", command=self.registrar_trabajador
        )
        seleccion = self.tabla_trabajadores.selection()
        if seleccion:
            self.tabla_trabajadores.selection_remove(*seleccion)

    def actualizar_lista_trabajadores(self) -> None:
        """Carga la lista de trabajadores según el filtro actual."""
        try:
            trabajadores = listar_trabajadores(self.filtro_rut_trabajador.get())
        except Error:
            self._mostrar_error_base_datos()
            return

        for elemento in self.tabla_trabajadores.get_children():
            self.tabla_trabajadores.delete(elemento)
        for trabajador in trabajadores:
            self.tabla_trabajadores.insert(
                "",
                tk.END,
                values=(
                    trabajador["rut"],
                    trabajador["nombre"],
                    trabajador["cargo"] or "",
                ),
            )

    def limpiar_busqueda_trabajadores(self) -> None:
        """Borra el filtro y vuelve a mostrar todos los trabajadores."""
        self.filtro_rut_trabajador.set("")
        self.actualizar_lista_trabajadores()

    def _filtrar_trabajadores(self, _: tk.Event) -> None:
        """Filtra trabajadores al escribir en el campo de búsqueda."""
        self.actualizar_lista_trabajadores()

    def _seleccionar_trabajador(self, _: tk.Event) -> None:
        """Carga los datos seleccionados y activa el modo de edición."""
        seleccion = self.tabla_trabajadores.selection()
        if not seleccion:
            return
        valores = self.tabla_trabajadores.item(seleccion[0], "values")
        rut = str(valores[0])
        self.rut_trabajador_original = rut
        self.editando_trabajador = True
        self.rut_trabajador.set(rut)
        self.nombre_trabajador.set(str(valores[1]))
        self.cargo_trabajador.set(str(valores[2]))
        self.entrada_rut_trabajador.configure(state="readonly")
        self.boton_accion_trabajador.configure(
            text="Guardar cambios", command=self.guardar_cambios_trabajador
        )

    def iniciar_turno(self) -> None:
        """Valida el RUT e inicia el turno del trabajador."""
        rut = self.rut_turno.get().strip()
        if not rut:
            messagebox.showwarning("Dato requerido", "Ingrese el RUT.", parent=self.root)
            self.entrada_rut_turno.focus_set()
            return

        try:
            id_turno = iniciar_turno_repo(rut)
        except RutInvalidoError:
            messagebox.showwarning(
                "RUT inválido",
                "Ingrese un RUT chileno válido.",
                parent=self.root,
            )
            return
        except TrabajadorNoExisteError:
            messagebox.showwarning(
                "Trabajador no encontrado",
                "No existe un trabajador registrado con ese RUT.",
                parent=self.root,
            )
            return
        except TurnoAbiertoError:
            messagebox.showwarning(
                "Turno ya abierto",
                "El trabajador ya tiene un turno abierto.",
                parent=self.root,
            )
            return
        except Error:
            self._mostrar_error_base_datos()
            return

        messagebox.showinfo(
            "Turno iniciado",
            f"El turno se inició correctamente (ID: {id_turno}).",
            parent=self.root,
        )
        self.actualizar_turnos_activos()

    def registrar_salida(self) -> None:
        """Valida el RUT y registra la salida del trabajador."""
        rut = self.rut_turno.get().strip()
        if not rut:
            messagebox.showwarning("Dato requerido", "Ingrese el RUT.", parent=self.root)
            self.entrada_rut_turno.focus_set()
            return

        try:
            id_salida = registrar_salida_repo(rut)
        except RutInvalidoError:
            messagebox.showwarning(
                "RUT inválido",
                "Ingrese un RUT chileno válido.",
                parent=self.root,
            )
            return
        except SinTurnoAbiertoError:
            messagebox.showwarning(
                "Sin turno abierto",
                "El trabajador no tiene un turno abierto para registrar su salida.",
                parent=self.root,
            )
            return
        except Error:
            self._mostrar_error_base_datos()
            return

        messagebox.showinfo(
            "Salida registrada",
            f"La salida se registró correctamente (ID: {id_salida}).",
            parent=self.root,
        )
        self.actualizar_turnos_activos()

    def actualizar_turnos_activos(self) -> None:
        """Actualiza la tabla de turnos abiertos."""
        try:
            turnos = listar_turnos_activos()
        except Error:
            self._mostrar_error_base_datos()
            return

        for elemento in self.tabla_turnos.get_children():
            self.tabla_turnos.delete(elemento)
        for turno in turnos:
            fecha_inicio = turno["fecha_inicio"]
            if isinstance(fecha_inicio, (datetime, date)):
                fecha_formateada = fecha_inicio.strftime("%d/%m/%Y %H:%M")
            else:
                fecha_formateada = str(fecha_inicio)
            self.tabla_turnos.insert(
                "",
                tk.END,
                values=(
                    turno["rut"],
                    turno["nombre"],
                    turno["cargo"] or "",
                    fecha_formateada,
                ),
            )
        self.etiqueta_personas.configure(
            text=f"Personas en faena: {len(turnos)}"
        )

    def limpiar_base_datos(self) -> None:
        """Pide doble confirmación y elimina todos los datos."""
        confirmado = messagebox.askyesno(
            "Limpiar base de datos",
            "Se borrarán TODOS los trabajadores y turnos. "
            "Esta acción no se puede deshacer. ¿Desea continuar?",
            parent=self.root,
            icon="warning",
        )
        if not confirmado:
            return

        palabra = simpledialog.askstring(
            "Confirmar limpieza",
            "Escriba LIMPIAR para confirmar:",
            parent=self.root,
        )
        if palabra != "LIMPIAR":
            return

        try:
            limpiar_base_datos()
        except Error:
            self._mostrar_error_base_datos()
            return

        self.actualizar_lista_trabajadores()
        self.actualizar_turnos_activos()
        messagebox.showinfo(
            "Base de datos limpia",
            "Se eliminaron todos los trabajadores y turnos.",
            parent=self.root,
        )

    def _mostrar_error_base_datos(self) -> None:
        """Muestra un aviso sin detalles internos de la base de datos."""
        messagebox.showerror(
            "Error de base de datos",
            "Ocurrió un problema al comunicarse con la base de datos. "
            "Inténtelo nuevamente.",
            parent=self.root,
        )

    def _al_presionar_enter_trabajador(self, _: tk.Event) -> str:
        """Ejecuta la acción del formulario al presionar Enter."""
        if self.editando_trabajador:
            self.guardar_cambios_trabajador()
        else:
            self.registrar_trabajador()
        return "break"

    def _al_presionar_enter_turnos(self, _: tk.Event) -> str:
        """Inicia el turno al presionar Enter."""
        self.iniciar_turno()
        return "break"

    def _al_cambiar_pestana(self, _: tk.Event) -> None:
        """Actualiza los turnos al abrir su pestaña."""
        if self.notebook.select() == str(self.pestana_activos):
            self.actualizar_turnos_activos()


def main() -> None:
    """Crea y ejecuta la ventana principal."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
