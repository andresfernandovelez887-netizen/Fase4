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
    """Subtipos: Redes, Desarrollo de Software, Laboratorio Financiero"""
    def calcular_costo(self, cantidad_horas=1, descuento=0.0):
        # Se cobra por hora
        total = self.costo_base * cantidad_horas
        return total - (total * descuento)

    def obtener_resumen(self):
        return f"[Sala] {self.nombre_servicio} - ${self.costo_base}/hora"


class AlquilerEquipo(Servicios):
    """Subtipos: Servidores, Equipos Portátiles"""
    def calcular_costo(self, cantidad_dias=1, seguro_adicional=0.10):
        # Se cobra por día, más un recargo del 10% por seguro de daños
        total = self.costo_base * cantidad_dias
        return total + (total * seguro_adicional)

    def obtener_resumen(self):
        return f"[Equipo] {self.nombre_servicio} - ${self.costo_base}/día"


class AsesoriaEspecializada(Servicios):
    """Subtipos: Certificación, Instalación, Monitoreo"""
    def calcular_costo(self, cantidad=1, impuesto_iva=0.19):
        # Es un costo fijo por servicio, se le aplica el IVA
        total = self.costo_base + (self.costo_base * impuesto_iva)
        return total * cantidad

    def obtener_resumen(self):
        return f"[Asesoría] {self.nombre_servicio} - Costo Base: ${self.costo_base}"








