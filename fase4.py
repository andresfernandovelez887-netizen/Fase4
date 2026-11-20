# Andres Fernando Velez
# Programacion - Ingenieria de Sistemas
# Fase 4: Sistema Integral de Gestión de Clientes, Servicios y Reservas

from abc import ABC, abstractmethod
import logging

# Configuración del archivo de Logs para registrar eventos y errores sin detener el programa
logging.basicConfig(
    filename='sistema_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ======================================================================
# EXCEPCIONES PERSONALIZADAS
# ======================================================================
class ErrorDatoInvalido(Exception): pass
class ErrorServicioNoDisponible(Exception): pass
class ErrorReservaInvalida(Exception): pass
class ErrorOperacionNoPermitida(Exception): pass
class ErrorSistemaInterno(Exception): pass


# ======================================================================
# 1. SUPERCLASE ABSOLUTA
# ======================================================================
class EntidadGeneral(ABC):
    def __init__(self, id_entidad):
        self.id_entidad = id_entidad

    @abstractmethod
    def obtener_resumen(self):
        """Método abstracto que todas las entidades deben implementar."""
        pass


# ======================================================================
# 2. CLASE CLIENTE (CON ENCAPSULACIÓN Y VALIDACIONES ESTRICTAS)
# ======================================================================
class Cliente(EntidadGeneral):
    def __init__(self, id_entidad, nombre, telefono, documento, correo):
        super().__init__(id_entidad)
        # Se asignan mediante los setters para ejecutar automáticamente las validaciones
        self.nombre = nombre
        self.telefono = telefono
        self.documento = documento
        self.correo = correo

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str):
            raise ErrorDatoInvalido("El nombre del cliente no puede estar vacío.")
        nombre_limpio = valor.strip()
        if len(nombre_limpio) < 3 or not nombre_limpio.replace(" ", "").isalpha():
            raise ErrorDatoInvalido("El nombre debe contener únicamente letras y tener al menos 3 caracteres.")
        self.__nombre = nombre_limpio

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        doc_str = str(valor).strip()
        if not doc_str.isdigit() or len(doc_str) < 6:
            raise ErrorDatoInvalido("El documento debe ser numérico y tener mínimo 6 dígitos.")
        self.__documento = doc_str

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        tel_str = str(valor).strip()
        if not tel_str.isdigit() or len(tel_str) < 7:
            raise ErrorDatoInvalido("El teléfono debe ser numérico y tener mínimo 7 dígitos.")
        self.__telefono = tel_str

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if not valor or not isinstance(valor, str):
            raise ErrorDatoInvalido("El correo electrónico no puede estar vacío.")
        correo_limpio = valor.strip()
        if "@" not in correo_limpio or "." not in correo_limpio:
            raise ErrorDatoInvalido("El correo electrónico debe contener un '@' y un punto '.' válidos.")
        partes = correo_limpio.split("@")
        if len(partes) != 2 or not partes[0] or not partes[1]:
            raise ErrorDatoInvalido("El formato del correo es inválido (ejemplo: cliente@dominio.com).")
        if "." not in partes[1] or partes[1].startswith(".") or partes[1].endswith("."):
            raise ErrorDatoInvalido("El dominio del correo electrónico es inválido.")
        self.__correo = correo_limpio

    def obtener_resumen(self):
        return f"Cliente [{self.id_entidad}]: {self.nombre} | Doc: {self.documento} | Tel: {self.telefono} | Email: {self.correo}"


# ======================================================================
# 3. CLASE PADRE ABSTRACTA: SERVICIOS
# ======================================================================
class Servicios(EntidadGeneral):
    def __init__(self, id_entidad, nombre_servicio, costo_base):
        super().__init__(id_entidad)
        if not nombre_servicio or not isinstance(nombre_servicio, str):
            raise ErrorDatoInvalido("El nombre del servicio no puede estar vacío.")
        if not isinstance(costo_base, (int, float)) or costo_base <= 0:
            raise ErrorDatoInvalido(f"El costo base de '{nombre_servicio}' debe ser numérico y mayor a cero.")
        self.nombre_servicio = nombre_servicio.strip()
        self.costo_base = float(costo_base)

    @abstractmethod
    def validar_parametros(self, **kwargs):
        """Contrato polimórfico: cada servicio valida sus propios parámetros."""
        pass

    @abstractmethod
    def calcular_costo(self, cantidad=1, descuento=0.0):
        """Método polimórfico sobrecargado mediante parámetros opcionales."""
        pass


# ======================================================================
# 4. CLASES HIJAS: LOS 3 TIPOS DE SERVICIOS PRINCIPALES (POLIMORFISMO)
# ======================================================================
class ReservaSala(Servicios):
    """Subtipos: Redes, Desarrollo de Software, Laboratorio Financiero"""
    def validar_parametros(self, horaini=0, horafin=0, **kwargs):
        if not isinstance(horaini, int) or not isinstance(horafin, int):
            raise ErrorReservaInvalida("Las horas de inicio y fin deben ser números enteros.")
        if horaini < 6 or horafin > 22:
            raise ErrorReservaInvalida("Las salas operan únicamente entre las 6:00 y las 22:00 horas.")
        if horaini >= horafin:
            raise ErrorReservaInvalida("La hora de inicio en la sala debe ser menor a la hora de fin.")
        return True

    def calcular_costo(self, cantidad_horas=1, descuento=0.0):
        if cantidad_horas <= 0 or cantidad_horas > 16:
            raise ErrorReservaInvalida("La duración de la sala debe estar entre 1 y 16 horas.")
        if descuento < 0 or descuento > 0.5:
            raise ErrorDatoInvalido("El descuento aplicado debe estar entre 0% y 50%.")
        total = self.costo_base * cantidad_horas
        return total - (total * descuento)

    def obtener_resumen(self):
        return f"[Sala] {self.nombre_servicio} - ${self.costo_base:,.0f}/hora"


class AlquilerEquipo(Servicios):
    """Subtipos: Servidores, Equipos Portátiles"""
    def validar_parametros(self, dias=1, **kwargs):
        if not isinstance(dias, int) or dias <= 0:
            raise ErrorReservaInvalida("El alquiler de equipos debe ser de al menos 1 día.")
        if dias > 30:
            raise ErrorReservaInvalida("El alquiler máximo permitido es de 30 días.")
        return True

    def calcular_costo(self, cantidad_dias=1, seguro_adicional=0.10):
        self.validar_parametros(dias=cantidad_dias)
        total = self.costo_base * cantidad_dias
        return total + (total * seguro_adicional)

    def obtener_resumen(self):
        return f"[Equipo] {self.nombre_servicio} - ${self.costo_base:,.0f}/día"


class AsesoriaEspecializada(Servicios):
    """Subtipos: Certificación, Instalación, Monitoreo"""
    def validar_parametros(self, cantidad=1, **kwargs):
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ErrorReservaInvalida("La cantidad de asesorías debe ser al menos 1.")
        return True

    def calcular_costo(self, cantidad=1, impuesto_iva=0.19):
        self.validar_parametros(cantidad=cantidad)
        total = self.costo_base + (self.costo_base * impuesto_iva)
        return total * cantidad

    def obtener_resumen(self):
        return f"[Asesoría] {self.nombre_servicio} - Costo Fijo: ${self.costo_base:,.0f}"


# ======================================================================
# 5. CLASE DE GESTIÓN Y FACTURACIÓN DE RESERVAS
# ======================================================================
class reservas(EntidadGeneral):
    def __init__(self, id_entidad, fecha, descripcion, cliente, servicio, horaini=0, horafin=0, dias=1):
        super().__init__(id_entidad)
        if not fecha or not str(fecha).strip():
            raise ErrorReservaInvalida("La fecha de la reserva no puede estar vacía.")
        self.fecha = str(fecha).strip()
        self.descripcion = descripcion.strip() if descripcion else "Sin descripción"
        self.cliente = cliente
        self.servicio = servicio
        
        try:
            self.horaini = int(horaini) if horaini != "" else 0
            self.horafin = int(horafin) if horafin != "" else 0
            self.dias = int(dias) if dias != "" else 1
        except ValueError as err:
            raise ErrorReservaInvalida("Las horas y días deben ser valores numéricos enteros.") from err
            
        self.estado = "Pendiente"
        self.costo_final = 0.0

    def obtener_resumen(self):
        return f"Servicio #{self.id_entidad} | {self.fecha} | {self.servicio.nombre_servicio} | Estado: {self.estado} | Costo: ${self.costo_final:,.2f}"

    def confirmar_reserva(self, descuento=0.0):
        """Procesa y confirma la reserva usando el bloque completo try/except/else/finally."""
        try:
            if self.estado == "Facturada":
                raise ErrorOperacionNoPermitida("Esta reserva ya se encuentra facturada y confirmada.")

            self.servicio.validar_parametros(horaini=self.horaini, horafin=self.horafin, dias=self.dias)

            if isinstance(self.servicio, ReservaSala):
                horas_totales = self.horafin - self.horaini
                self.costo_final = self.servicio.calcular_costo(cantidad_horas=horas_totales, descuento=descuento)
            elif isinstance(self.servicio, AlquilerEquipo):
                self.costo_final = self.servicio.calcular_costo(cantidad_dias=self.dias)
            elif isinstance(self.servicio, AsesoriaEspecializada):
                self.costo_final = self.servicio.calcular_costo()

            self.estado = "Facturada"
            logging.info(f"Servicio #{self.id_entidad} ({self.servicio.nombre_servicio}) facturado para {self.cliente.nombre}.")
            return True

        except (ErrorReservaInvalida, ErrorOperacionNoPermitida, ErrorDatoInvalido) as e:
            self.estado = "Fallida"
            logging.warning(f"Error de validación en reserva #{self.id_entidad}: {e}")
            print(f"\n[!] ERROR DE RESERVA: {e}")
            return False

        except Exception as err:
            self.estado = "Error Crítico"
            logging.critical(f"Falla inesperada en reserva #{self.id_entidad}: {err}")
            raise ErrorSistemaInterno("Falla general al procesar la reserva.") from err

        else:
            print(f"\n[+] ÉXITO: Reserva #{self.id_entidad} confirmada correctamente.")

        finally:
            print(f"[*] Auditoría de estado - Reserva #{self.id_entidad}: {self.estado}")

    def cancelar_reserva(self, motivo="Cancelación solicitada por el cliente"):
        """Cancela una reserva activa validando reglas de negocio con try/except/else/finally."""
        try:
            if self.estado == "Cancelada":
                raise ErrorOperacionNoPermitida(f"La reserva #{self.id_entidad} ya fue cancelada previamente.")
            if self.estado == "Fallida":
                raise ErrorOperacionNoPermitida(f"No se puede cancelar la reserva #{self.id_entidad} porque nunca fue confirmada.")
            if not motivo or not motivo.strip():
                raise ErrorDatoInvalido("Debe especificar un motivo válido para cancelar la reserva.")

            self.estado = "Cancelada"
            self.costo_final = 0.0
            logging.info(f"Reserva #{self.id_entidad} CANCELADA. Motivo: {motivo.strip()}")
            return True

        except (ErrorOperacionNoPermitida, ErrorDatoInvalido) as e:
            logging.warning(f"Intento inválido de cancelación en reserva #{self.id_entidad}: {e}")
            print(f"\n[!] OPERACIÓN NO PERMITIDA: {e}")
            return False

        except Exception as err:
            logging.critical(f"Error crítico al cancelar reserva #{self.id_entidad}: {err}")
            raise ErrorSistemaInterno("Error interno durante el proceso de cancelación.") from err

        else:
            print(f"\n[-] CANCELACIÓN EXITOSA: La reserva #{self.id_entidad} ha sido anulada.")

        finally:
            print(f"[*] Auditoría de estado tras cancelación - Reserva #{self.id_entidad}: {self.estado}")


# ======================================================================
# FUNCIÓN AUXILIAR: CAPTURA Y VALIDACIÓN CAMPO POR CAMPO DEL CLIENTE
# ======================================================================
def solicitar_datos_cliente_validados(id_cliente):
    """Pide cada campo del cliente y lo valida inmediatamente antes de pasar al siguiente."""
    # Se instancia con valores base válidos y luego cada setter valida su propio campo al asignarse
    cliente_obj = Cliente(id_cliente, "Base", "0000000", "000000", "base@dominio.com")

    while True:
        try:
            cliente_obj.nombre = input("Nombre del Cliente: ")
            break
        except ErrorDatoInvalido as e:
            logging.warning(f"Validación fallida en nombre de cliente: {e}")
            print(f"[!] ERROR: {e} Vuelva a ingresarlo.\n")

    while True:
        try:
            cliente_obj.documento = input("Documento (mínimo 6 dígitos): ")
            break
        except ErrorDatoInvalido as e:
            logging.warning(f"Validación fallida en documento de cliente: {e}")
            print(f"[!] ERROR: {e} Vuelva a ingresarlo.\n")

    while True:
        try:
            cliente_obj.telefono = input("Teléfono (mínimo 7 dígitos): ")
            break
        except ErrorDatoInvalido as e:
            logging.warning(f"Validación fallida en teléfono de cliente: {e}")
            print(f"[!] ERROR: {e} Vuelva a ingresarlo.\n")

    while True:
        try:
            cliente_obj.correo = input("Correo Electrónico: ")
            break
        except ErrorDatoInvalido as e:
            logging.warning(f"Validación fallida en correo de cliente: {e}")
            print(f"[!] ERROR: {e} Vuelva a ingresarlo.\n")

    return cliente_obj


# ======================================================================
# 6. SIMULACIÓN AUTOMÁTICA DE 10 OPERACIONES COMPLETAS (EXIGIDO POR GUÍA)
# ======================================================================
def ejecutar_simulacion_10_operaciones(lista_clientes, lista_reservas, cat_salas, cat_equipos, cat_asesorias):
    print("\n=======================================================")
    print("   SIMULACIÓN DE 10 OPERACIONES COMPLETAS - SOFTWARE FJ ")
    print("=======================================================")

    # OPERACIÓN 1: Registro válido de Cliente 1
    print("\n--- [OPERACIÓN 1] Registro válido de Cliente 1 ---")
    c1 = None
    try:
        c1 = Cliente(901, "Andres Velez", "3104567890", "1130602784", "andres.velez@unad.edu.co")
        lista_clientes.append(c1)
        logging.info(f"Simulación Op 1: Cliente válido creado -> {c1.nombre}")
        print(f"[+] OK: {c1.obtener_resumen()}")
    except ErrorDatoInvalido as e:
        print(f"[!] Error inesperado: {e}")

    # OPERACIÓN 2: Registro inválido de Cliente (correo sin '@' y documento corto)
    print("\n--- [OPERACIÓN 2] Registro inválido de Cliente (datos corruptos) ---")
    try:
        c_err1 = Cliente(902, "Juan Perez", "3112223344", "123", "juanperez.dominio.com")
        lista_clientes.append(c_err1)
    except ErrorDatoInvalido as e:
        logging.warning(f"Simulación Op 2 (Controlada): {e}")
        print(f"[+] Excepción controlada exitosamente: {e}")

    # OPERACIÓN 3: Registro inválido de Cliente (nombre numérico y teléfono corto)
    print("\n--- [OPERACIÓN 3] Registro inválido de Cliente (nombre con números) ---")
    try:
        c_err2 = Cliente(903, "123456", "310", "98765432", "maria@correo.com")
        lista_clientes.append(c_err2)
    except ErrorDatoInvalido as e:
        logging.warning(f"Simulación Op 3 (Controlada): {e}")
        print(f"[+] Excepción controlada exitosamente: {e}")

    # OPERACIÓN 4: Creación correcta de un Servicio especializado
    print("\n--- [OPERACIÓN 4] Creación válida de Servicio Especializado ---")
    try:
        serv_nuevo = AsesoriaEspecializada(304, "Auditoría de Ciberseguridad", 350000)
        cat_asesorias.append(serv_nuevo)
        logging.info(f"Simulación Op 4: Servicio creado -> {serv_nuevo.obtener_resumen()}")
        print(f"[+] OK: Servicio añadido al catálogo -> {serv_nuevo.obtener_resumen()}")
    except ErrorDatoInvalido as e:
        print(f"[!] Error: {e}")

    # OPERACIÓN 5: Creación incorrecta de Servicio (costo base negativo/cero)
    print("\n--- [OPERACIÓN 5] Creación inválida de Servicio (costo base <= 0) ---")
    try:
        serv_invalido = ReservaSala(199, "Sala Fantasma", -50000)
    except ErrorDatoInvalido as e:
        logging.warning(f"Simulación Op 5 (Controlada): {e}")
        print(f"[+] Excepción controlada exitosamente: {e}")

    # OPERACIÓN 6: Reserva exitosa de Sala (con sobrecarga de descuento del 10%)
    print("\n--- [OPERACIÓN 6] Reserva exitosa de Sala de Redes (con 10% descuento) ---")
    r1 = reservas(5001, "2026-11-20", "Configuración de routers", c1, cat_salas[0], horaini=8, horafin=12)
    if r1.confirmar_reserva(descuento=0.10):
        lista_reservas.append(r1)

    # OPERACIÓN 7: Reserva fallida de Sala (horario cruzado / fuera de rango)
    print("\n--- [OPERACIÓN 7] Reserva fallida de Sala (hora inicio mayor a fin) ---")
    r2 = reservas(5002, "2026-11-21", "Pruebas nocturnas", c1, cat_salas[1], horaini=18, horafin=14)
    r2.confirmar_reserva()
    lista_reservas.append(r2)

    # OPERACIÓN 8: Reserva exitosa de Alquiler de Equipo (Servidor por 3 días)
    print("\n--- [OPERACIÓN 8] Reserva exitosa de Alquiler de Servidor (3 días) ---")
    r3 = reservas(5003, "2026-11-22", "Despliegue servidor pruebas", c1, cat_equipos[0], dias=3)
    if r3.confirmar_reserva():
        lista_reservas.append(r3)

    # OPERACIÓN 9: Reserva fallida de Equipo (excede máximo de 30 días)
    print("\n--- [OPERACIÓN 9] Reserva fallida de Equipo (excede 30 días permitidos) ---")
    r4 = reservas(5004, "2026-11-23", "Alquiler anual", c1, cat_equipos[1], dias=45)
    r4.confirmar_reserva()
    lista_reservas.append(r4)

    # OPERACIÓN 10: Reserva de Asesoría confirmada y luego CANCELADA + intento de doble cancelación
    print("\n--- [OPERACIÓN 10] Reserva de Asesoría, Cancelación válida y Doble Cancelación bloqueada ---")
    r5 = reservas(5005, "2026-11-24", "Certificación ISO", c1, cat_asesorias[0])
    if r5.confirmar_reserva():
        lista_reservas.append(r5)
        r5.cancelar_reserva("Cambio de cronograma del proyecto")
        r5.cancelar_reserva("Segundo intento de cancelación")

    print("\n=======================================================")
    print("   FIN DE LA SIMULACIÓN (10 OPERACIONES EJECUTADAS)    ")
    print("=======================================================\n")


# ======================================================================
# 7. PROGRAMA PRINCIPAL INTERACTIVO
# ======================================================================
if __name__ == "__main__":
    lista_clientes = []
    lista_reservas = []

    # PRE-CONFIGURACIÓN DEL CATÁLOGO
    cat_salas = [
        ReservaSala(101, "Sala de Redes", 50000),
        ReservaSala(102, "Sala de Desarrollo de Software", 60000),
        ReservaSala(103, "Sala de Laboratorio Financiero", 80000)
    ]
    
    cat_equipos = [
        AlquilerEquipo(201, "Servidor Físico", 150000),
        AlquilerEquipo(202, "Equipo Portátil (Laptop)", 80000)
    ]
    
    cat_asesorias = [
        AsesoriaEspecializada(301, "Certificación", 200000),
        AsesoriaEspecializada(302, "Instalación", 150000),
        AsesoriaEspecializada(303, "Monitoreo", 80000)
    ]

    id_cliente_actual = 1
    id_reserva_actual = 1001

    print("=========================================")
    print("   SISTEMA DE GESTIÓN - SOFTWARE FJ      ")
    print("=========================================")

    # BUCLE DE AUTENTICACIÓN
    autenticado = False
    while not autenticado:
        usu = input("Usuario: ").strip()
        pwd = input("Contraseña: ").strip()
        if usu == "administrador" and pwd == "Televisor2020.":
            logging.info("Inicio de sesión exitoso del administrador.")
            print("\n>>> Acceso Concedido <<<\n")
            autenticado = True
        else:
            logging.warning(f"Intento fallido de inicio de sesión con usuario: '{usu}'")
            print("[!] Credenciales incorrectas.\n")

    # MENÚ DE MODO DE EJECUCIÓN
    ir_manual = 'N'
    while True:
        print("Seleccione el modo de operación:")
        print("1. Ejecutar Simulación Automática de 10 Operaciones (Prueba de rúbrica)")
        print("2. Modo Interactivo Manual (Facturación por cliente)")
        modo = input("Opción (1/2): ").strip()

        if modo == '1':
            ejecutar_simulacion_10_operaciones(lista_clientes, lista_reservas, cat_salas, cat_equipos, cat_asesorias)
            ir_manual = input("¿Desea continuar al Modo Interactivo Manual? (S/N): ").strip().upper()
            break
        elif modo == '2':
            break
        else:
            print("[!] Opción inválida. Digite 1 o 2.\n")

    # ==================================================
    # BUCLE 1: REGISTRO DE CLIENTES (MODO INTERACTIVO)
    # ==================================================
    if modo == '2' or ir_manual == 'S':
        while True:
            print("\n--- REGISTRO DE NUEVO CLIENTE ---")
            # Validación inmediata campo por campo
            nuevo_cliente = solicitar_datos_cliente_validados(id_cliente_actual)
            lista_clientes.append(nuevo_cliente)
            logging.info(f"Cliente registrado manualmente: {nuevo_cliente.nombre} (Doc: {nuevo_cliente.documento})")
            id_cliente_actual += 1
            
            reservas_cliente_actual = []
            
            # ==================================================
            # BUCLE 2: MÚLTIPLES SERVICIOS PARA EL MISMO CLIENTE
            # ==================================================
            while True:
                print(f"\n--- FACTURACIÓN DE SERVICIO PARA: {nuevo_cliente.nombre} ---")
                print("1. Reserva de Salas")
                print("2. Alquiler de Equipos")
                print("3. Asesorías Especializadas")
                opc_cat = input("Seleccione Categoría (1/2/3): ").strip()

                if opc_cat not in ('1', '2', '3'):
                    logging.warning(f"Categoría inválida ingresada en menú: '{opc_cat}'")
                    print("\n[!] ERROR: Opción de categoría inválida. Debe digitar 1, 2 o 3. Vuelva a escoger.")
                    continue

                servicio_elegido = None
                horaini = horafin = dias = 0

                # Sub-bucle blindado contra ValueError e IndexError
                while servicio_elegido is None:
                    try:
                        if opc_cat == '1':
                            print("\n--- SALAS DISPONIBLES ---")
                            for i, s in enumerate(cat_salas, 1):
                                print(f"{i}. {s.obtener_resumen()}")
                            sel = int(input(f"Elija la sala (1-{len(cat_salas)}): ")) - 1
                            if sel < 0 or sel >= len(cat_salas):
                                raise ErrorServicioNoDisponible("La sala seleccionada no existe en el catálogo.")
                            servicio_elegido = cat_salas[sel]
                            horaini = input("Hora de inicio (formato 24h, ej. 8): ")
                            horafin = input("Hora de fin (formato 24h, ej. 11): ")

                        elif opc_cat == '2':
                            print("\n--- EQUIPOS DISPONIBLES ---")
                            for i, e in enumerate(cat_equipos, 1):
                                print(f"{i}. {e.obtener_resumen()}")
                            sel = int(input(f"Elija el equipo (1-{len(cat_equipos)}): ")) - 1
                            if sel < 0 or sel >= len(cat_equipos):
                                raise ErrorServicioNoDisponible("El equipo seleccionado no existe en el catálogo.")
                            servicio_elegido = cat_equipos[sel]
                            dias = input("¿Por cuántos días lo alquilará?: ")

                        elif opc_cat == '3':
                            print("\n--- ASESORÍAS DISPONIBLES ---")
                            for i, a in enumerate(cat_asesorias, 1):
                                print(f"{i}. {a.obtener_resumen()}")
                            sel = int(input(f"Elija la asesoría (1-{len(cat_asesorias)}): ")) - 1
                            if sel < 0 or sel >= len(cat_asesorias):
                                raise ErrorServicioNoDisponible("La asesoría seleccionada no existe en el catálogo.")
                            servicio_elegido = cat_asesorias[sel]

                    except ValueError:
                        logging.warning("Entrada inválida en selección de servicio: se ingresó texto en lugar de número.")
                        print("\n[!] ERROR: Debe ingresar un número entero válido. Vuelva a escoger.")
                    except (ErrorServicioNoDisponible, IndexError) as e:
                        logging.warning(f"Índice fuera de rango en menú de servicios: {e}")
                        print(f"\n[!] ERROR: {e} Vuelva a escoger.")

                print("\n--- DETALLES DEL SERVICIO ---")
                fecha = input("Fecha del servicio (YYYY-MM-DD): ")
                descripcion = input("Breve descripción del trabajo: ")

                try:
                    nueva_reserva = reservas(
                        id_entidad=id_reserva_actual, fecha=fecha, descripcion=descripcion, 
                        cliente=nuevo_cliente, servicio=servicio_elegido, 
                        horaini=horaini, horafin=horafin, dias=dias
                    )
                    
                    if nueva_reserva.confirmar_reserva():
                        lista_reservas.append(nueva_reserva)
                        reservas_cliente_actual.append(nueva_reserva)
                        print(f"[+] Servicio agregado exitosamente. (Subtotal: ${nueva_reserva.costo_final:,.2f})")
                        id_reserva_actual += 1
                    else:
                        lista_reservas.append(nueva_reserva)
                        id_reserva_actual += 1
                except ErrorReservaInvalida as e:
                    logging.warning(f"Error al instanciar reserva: {e}")
                    print(f"[!] Falla en validación de reserva: {e}")
                except Exception as e:
                    logging.error(f"Error inesperado procesando reserva: {e}")
                    print(f"[!] Error inesperado procesando la solicitud: {e}")

                otro_servicio = input(f"\n¿Desea agregar OTRO servicio para {nuevo_cliente.nombre}? (S/N): ").strip().upper()
                if otro_servicio != 'S':
                    break

            # ==================================================
            # IMPRESIÓN DE FACTURA INDIVIDUAL DEL CLIENTE
            # ==================================================
            print("\n" + "="*55)
            print(f"   FACTURA DE: {nuevo_cliente.nombre} (Doc: {nuevo_cliente.documento})")
            print("="*55)
            total_cliente = 0
            for r in reservas_cliente_actual:
                print(f"- {r.obtener_resumen()}")
                if r.estado == "Facturada":
                    total_cliente += r.costo_final
            print("-" * 55)
            print(f"TOTAL A PAGAR: ${total_cliente:,.2f}")
            print("="*55 + "\n")

            otro_cliente = input("¿Desea registrar a un NUEVO CLIENTE? (S/N): ").strip().upper()
            if otro_cliente != 'S':
                break
            print("\n" + "*"*55 + "\n")

    # ==================================================
    # MÓDULO GLOBAL DE CANCELACIÓN POR CÓDIGO (TRAS INGRESAR TODOS LOS CLIENTES)
    # ==================================================
    servicios_facturados = [r for r in lista_reservas if r.estado == "Facturada"]
    if servicios_facturados:
        while True:
            desea_cancelar = input("\n¿Desea CANCELAR algún servicio registrado antes de emitir los totales finales? (S/N): ").strip().upper()
            if desea_cancelar != 'S':
                break

            print("\n--- SERVICIOS ACTIVOS DISPONIBLES PARA CANCELACIÓN ---")
            for r in lista_reservas:
                if r.estado == "Facturada":
                    print(f"Código #{r.id_entidad} | Cliente: {r.cliente.nombre} | {r.servicio.nombre_servicio} | ${r.costo_final:,.2f}")

            try:
                id_cancelar = int(input("\nIngrese el CÓDIGO (#ID) del servicio a cancelar: "))
                encontrada = False
                for r in lista_reservas:
                    if r.id_entidad == id_cancelar:
                        motivo = input("Motivo de cancelación: ")
                        r.cancelar_reserva(motivo)
                        encontrada = True
                        break
                if not encontrada:
                    logging.warning(f"Intento de cancelación con código inexistente: #{id_cancelar}")
                    print(f"[!] No se encontró ningún servicio con el código #{id_cancelar}.")
            except ValueError:
                logging.warning("Error de tipo al ingresar código de cancelación.")
                print("[!] Error: El código del servicio debe ser un número entero.")

    # ==========================================
    # REPORTE TOTAL CONSOLIDADO (FIN DEL PROGRAMA)
    # ==========================================
    print("\n\n=======================================================")
    print("   REPORTE FINANCIERO TOTAL CONSOLIDADO - SOFTWARE FJ  ")
    print("=======================================================")
    
    gran_total_ingresos = 0
    total_servicios_prestados = 0

    for cliente in lista_clientes:
        print(f"\n>> {cliente.obtener_resumen()}")
        subtotal_acumulado = 0
        
        for r in lista_reservas:
            if r.cliente.id_entidad == cliente.id_entidad:
                print(f"   {r.obtener_resumen()}")
                if r.estado == "Facturada":
                    subtotal_acumulado += r.costo_final
                    total_servicios_prestados += 1
                
        print(f"   --- Subtotal Facturado Cliente: ${subtotal_acumulado:,.2f}")
        gran_total_ingresos += subtotal_acumulado

    print("\n=======================================================")
    print(f"TOTAL DE CLIENTES ATENDIDOS: {len(lista_clientes)}")
    print(f"TOTAL DE SERVICIOS FACTURADOS: {total_servicios_prestados}")
    print(f"GRAN TOTAL DE INGRESOS: ${gran_total_ingresos:,.2f}")
    print("=======================================================")
    print("Sistema Finalizado Exitosamente. Historial guardado en 'sistema_fj.log'")
