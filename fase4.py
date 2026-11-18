# Andres Fernando Velez
# Programacion - Ingenieria de Sistemas
# Fase 4: Sistema Integral de Gestión de Clientes, Servicios y Reservas

from abc import ABC, abstractmethod
import logging

# Configuración del archivo de Logs 
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
class ErrorSistemaInterno(Exception): pass


# ======================================================================
# 1. SUPERCLASE ABSOLUTA
# ======================================================================
class EntidadGeneral(ABC):
    def __init__(self, id_entidad):
        self.id_entidad = id_entidad

    @abstractmethod
    def obtener_resumen(self):
        pass


# ======================================================================
# 2. CLASE CLIENTE 
# ======================================================================
class Cliente(EntidadGeneral):
    def __init__(self, id_entidad, nombre, telefono, documento):
        super().__init__(id_entidad)
        self.nombre = nombre
        self.telefono = telefono
        self.documento = documento

    @property
    def nombre(self): return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or valor.isnumeric():
            raise ErrorDatoInvalido("El nombre no puede estar vacío y debe ser texto válido.")
        self.__nombre = valor.strip()

    @property
    def documento(self): return self.__documento

    @documento.setter
    def documento(self, valor):
        if not str(valor).isdigit():
            raise ErrorDatoInvalido("El documento debe contener únicamente números.")
        self.__documento = str(valor)

    @property
    def telefono(self): return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not str(valor).isdigit():
            raise ErrorDatoInvalido("El teléfono no puede estar vacío y debe ser numérico.")
        self.__telefono = str(valor)

    def obtener_resumen(self):
        return f"Cliente [{self.id_entidad}]: {self.nombre} - Doc: {self.documento}"


# ======================================================================
# 3. CLASE PADRE ABSTRACTA: SERVICIOS
# ======================================================================
class Servicios(EntidadGeneral):
    def __init__(self, id_entidad, nombre_servicio, costo_base):
        super().__init__(id_entidad)
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base

    @abstractmethod
    def calcular_costo(self, cantidad=1, descuento=0.0):
        pass


# ======================================================================
# 4. CLASES HIJAS: LOS 3 TIPOS DE SERVICIOS PRINCIPALES (POLIMORFISMO)
# ======================================================================
class ReservaSala(Servicios):
    def calcular_costo(self, cantidad_horas=1, descuento=0.0):
        total = self.costo_base * cantidad_horas
        return total - (total * descuento)

    def obtener_resumen(self):
        return f"[Sala] {self.nombre_servicio} - ${self.costo_base}/hora"


class AlquilerEquipo(Servicios):
    def calcular_costo(self, cantidad_dias=1, seguro_adicional=0.10):
        total = self.costo_base * cantidad_dias
        return total + (total * seguro_adicional)

    def obtener_resumen(self):
        return f"[Equipo] {self.nombre_servicio} - ${self.costo_base}/día"


class AsesoriaEspecializada(Servicios):
    def calcular_costo(self, cantidad=1, impuesto_iva=0.19):
        total = self.costo_base + (self.costo_base * impuesto_iva)
        return total * cantidad

    def obtener_resumen(self):
        return f"[Asesoría] {self.nombre_servicio} - Costo Fijo: ${self.costo_base}"


# ======================================================================
# 5. CLASE DE GESTIÓN Y FACTURACIÓN DE RESERVAS
# ======================================================================
class reservas(EntidadGeneral):
    def __init__(self, id_entidad, fecha, descripcion, cliente, servicio, horaini=0, horafin=0, dias=1):
        super().__init__(id_entidad)
        self.fecha = fecha
        self.descripcion = descripcion
        self.cliente = cliente
        self.servicio = servicio
        
        try:
            self.horaini = int(horaini) if horaini else 0
            self.horafin = int(horafin) if horafin else 0
            self.dias = int(dias) if dias else 1
        except ValueError:
            raise ErrorReservaInvalida("Las horas y días deben ser valores numéricos enteros.")
            
        self.estado = "Pendiente"
        self.costo_final = 0.0

    def obtener_resumen(self):
        return f"Servicio #{self.id_entidad} | {self.fecha} | {self.servicio.nombre_servicio} | Costo: ${self.costo_final:,.2f}"

    def confirmar_reserva(self):
        try:
            if isinstance(self.servicio, ReservaSala):
                if self.horaini >= self.horafin:
                    raise ErrorReservaInvalida("La hora de inicio en la sala debe ser menor a la hora de fin.")
                horas_totales = self.horafin - self.horaini
                self.costo_final = self.servicio.calcular_costo(cantidad_horas=horas_totales)
            
            elif isinstance(self.servicio, AlquilerEquipo):
                if self.dias <= 0:
                    raise ErrorReservaInvalida("El alquiler debe ser de al menos 1 día.")
                self.costo_final = self.servicio.calcular_costo(cantidad_dias=self.dias)
            
            elif isinstance(self.servicio, AsesoriaEspecializada):
                self.costo_final = self.servicio.calcular_costo()

            self.estado = "Facturada"
            logging.info(f"Servicio {self.id_entidad} procesado para {self.cliente.nombre}.")
            return True

        except ErrorReservaInvalida as e:
            self.estado = "Fallida"
            logging.warning(f"Error de validación: {e}")
            print(f"\n[!] ERROR: {e}")
            return False
        except Exception as err:
            self.estado = "Error Crítico"
            logging.critical(f"Falla inesperada: {err}")
            raise ErrorSistemaInterno("Falla general al procesar.") from err


# ======================================================================
# 6. PROGRAMA PRINCIPAL INTERACTIVO
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
        usu = input("Usuario: ")
        pwd = input("Contraseña: ")
        if usu == "administrador" and pwd == "Televisor2020.":
            print("\n>>> Acceso Concedido <<<\n")
            autenticado = True
        else:
            print("[!] Credenciales incorrectas.\n")

    # ==================================================
    # BUCLE 1: REGISTRO DE CLIENTES
    # ==================================================
    while True:
        print("--- REGISTRO DE NUEVO CLIENTE ---")
        try:
            nombre = input("Nombre del Cliente: ")
            documento = input("Documento: ")
            telefono = input("Teléfono: ")
            nuevo_cliente = Cliente(id_cliente_actual, nombre, telefono, documento)
            lista_clientes.append(nuevo_cliente)
            id_cliente_actual += 1
        except ErrorDatoInvalido as e:
            print(f"\n[!] ERROR DE VALIDACIÓN: {e}\n")
            continue
        
        reservas_cliente_actual = []
        
        # ==================================================
        # BUCLE 2: MÚLTIPLES SERVICIOS PARA EL MISMO CLIENTE
        # ==================================================
        while True:
            print(f"\n--- FACTURACIÓN DE SERVICIO PARA: {nuevo_cliente.nombre} ---")
            print("1. Reserva de Salas")
            print("2. Alquiler de Equipos")
            print("3. Asesorías Especializadas")
            opc_cat = input("Seleccione Categoría (1/2/3): ")

            servicio_elegido = None
            horaini = horafin = dias = 0

            if opc_cat == '1':
                print("\n--- SALAS DISPONIBLES ---")
                for i, s in enumerate(cat_salas, 1): print(f"{i}. {s.obtener_resumen()}")
                sel = int(input("Elija la sala: ")) - 1
                servicio_elegido = cat_salas[sel]
                horaini = input("Hora de inicio (formato 24h, ej. 8): ")
                horafin = input("Hora de fin (formato 24h, ej. 11): ")

            elif opc_cat == '2':
                print("\n--- EQUIPOS DISPONIBLES ---")
                for i, e in enumerate(cat_equipos, 1): print(f"{i}. {e.obtener_resumen()}")
                sel = int(input("Elija el equipo: ")) - 1
                servicio_elegido = cat_equipos[sel]
                dias = input("¿Por cuántos días lo alquilará?: ")

            elif opc_cat == '3':
                print("\n--- ASESORÍAS DISPONIBLES ---")
                for i, a in enumerate(cat_asesorias, 1): print(f"{i}. {a.obtener_resumen()}")
                sel = int(input("Elija la asesoría: ")) - 1
                servicio_elegido = cat_asesorias[sel]

            else:
                print("[!] Opción inválida.")
                continue

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
            except ErrorReservaInvalida as e:
                print(f"[!] Falla en validación de reserva: {e}")
            except Exception as e:
                print(f"[!] Error inesperado procesando la solicitud: {e}")

            # Evaluar si el cliente quiere añadir más servicios a su factura
            otro_servicio = input(f"\n¿Desea agregar OTRO servicio para {nuevo_cliente.nombre}? (S/N): ").strip().upper()
            if otro_servicio != 'S':
                break

        # ==================================================
        # IMPRESIÓN DE FACTURA INDIVIDUAL DEL CLIENTE
        # ==================================================
        print("\n" + "="*50)
        print(f"   FACTURA DE: {nuevo_cliente.nombre} (Doc: {nuevo_cliente.documento})")
        print("="*50)
        total_cliente = 0
        for r in reservas_cliente_actual:
            print(f"- {r.obtener_resumen()}")
            total_cliente += r.costo_final
        print("-" * 50)
        print(f"TOTAL A PAGAR: ${total_cliente:,.2f}")
        print("="*50 + "\n")

        # Evaluar si se va a registrar a un cliente distinto o terminar el día
        otro_cliente = input("¿Desea registrar a un NUEVO CLIENTE? (S/N): ").strip().upper()
        if otro_cliente != 'S':
            break
        print("\n" + "*"*50 + "\n")

    # ==========================================
    # REPORTE TOTAL CONSOLIDADO (FIN DEL PROGRAMA)
    # ==========================================
    print("\n\n=======================================================")
    print("   REPORTE FINANCIERO TOTAL CONSOLIDADO - SOFTWARE FJ  ")
    print("=======================================================")
    
    gran_total_ingresos = 0
    total_servicios_prestados = 0

    # Agrupar e imprimir los servicios por cada cliente registrado
    for cliente in lista_clientes:
        print(f"\n>> {cliente.obtener_resumen()}")
        subtotal_acumulado = 0
        
        # Buscar todas las reservas exitosas que pertenecen a este cliente
        for r in lista_reservas:
            if r.cliente.id_entidad == cliente.id_entidad and r.estado == "Facturada":
                print(f"   {r.obtener_resumen()}")
                subtotal_acumulado += r.costo_final
                total_servicios_prestados += 1
                
        print(f"   --- Subtotal Cliente: ${subtotal_acumulado:,.2f}")
        gran_total_ingresos += subtotal_acumulado

    print("\n=======================================================")
    print(f"TOTAL DE CLIENTES ATENDIDOS: {len(lista_clientes)}")
    print(f"TOTAL DE SERVICIOS PRESTADOS: {total_servicios_prestados}")
    print(f"GRAN TOTAL DE INGRESOS: ${gran_total_ingresos:,.2f}")
    print("=======================================================")
    print("Sistema Finalizado Exitosamente. Historial guardado en 'sistema_fj.log'")
