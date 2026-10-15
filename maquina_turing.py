#la clase cinta representa la cinta de la maquina de turing

class Cinta:
    def __init__(self, blank_symbol='B'):
        self.blank_symbol = blank_symbol
        self.celdas = {}  # Diccionario para permitir índices negativos y positivos
    #tomo la palabra inicial y la cargo en la cinta, celda por celda 
    def cargar(self, palabra):   
        self.celdas = {}
        for i, caracter in enumerate(palabra):
            self.celdas[i] = caracter

    def leer(self, posicion): #esta funcion se encarga de leer lo que hay en la celda de la cinta
        # Si la celda no tiene nada, devuelve el símbolo blanco (esto simula que la cinta es infinita)
        return self.celdas.get(posicion, self.blank_symbol)

    def escribir(self, posicion, simbolo): #escribe un simbolo en la celda
        self.celdas[posicion] = simbolo

    def obtener_contenido(self):
        # Devuelve el segmento de la cinta que ha sido utilizado (para la interfaz web)
        if not self.celdas:
            return {0: self.blank_symbol}
        min_idx = min(self.celdas.keys())
        max_idx = max(self.celdas.keys())
        return {i: self.leer(i) for i in range(min_idx - 1, max_idx + 2)} #VERLO


class MaquinaTuring:
    def __init__(self, config):
        # Cargamos la configuración (esto vendrá del JSON en el próximo paso)
        self.states = config['states']
        self.input_alphabet = config['input_alphabet']
        self.tape_alphabet = config['tape_alphabet']
        self.blank_symbol = config.get('blank_symbol', 'B')
        self.start_state = config['start_state']
        self.accept_states = config['accept_states']
        self.reject_states = config.get('reject_states', [])
        
        # Diccionario de transiciones: {(estado_actual, simbolo_leido): (nuevo_estado, simbolo_escrito, direccion)}
        self.transitions = {}
        for t in config['transitions']:
            self.transitions[(t['from_state'], t['read'])] = (t['to_state'], t['write'], t['dir'])

        self.cinta = Cinta(self.blank_symbol)
        self.reiniciar()

    def reiniciar(self): #REINICIA LA MAQUINA PONIENDO EL ESTADO ACTUAL EN 0
        self.estado_actual = self.start_state
        self.cabezal = 0
        self.halted = False
        self.resultado = None # "Aceptada", "Rechazada", o None

    def cargar_entrada(self, entrada):
        self.reiniciar()
        self.cinta.cargar(entrada)

    def step(self):#cuando el usuario presiona siguiente paso esta funcion se ejecuta
        """Ejecuta un solo paso de la máquina. Ideal para el modo 'Paso a paso'."""
        if self.halted: #si la maquina termino no hace nada
            return False

        # Comprobar si ya estamos en un estado final
        if self.estado_actual in self.accept_states:
            self.halted = True
            self.resultado = "Aceptada"
            return False
        if self.estado_actual in self.reject_states:
            self.halted = True
            self.resultado = "Rechazada"
            return False

        simbolo_actual = self.cinta.leer(self.cabezal) #me marca que simbolo es el actual dentro de la cinta
        clave_transicion = (self.estado_actual, simbolo_actual)

        if clave_transicion in self.transitions: #VER
            nuevo_estado, simbolo_escrito, direccion = self.transitions[clave_transicion]
            
            # Escribir en la cinta
            self.cinta.escribir(self.cabezal, simbolo_escrito)
            
            # Mover el cabezal
            if direccion == 'D':
                self.cabezal += 1
            elif direccion == 'I':
                self.cabezal -= 1
            # Si es 'S' (Stay), el cabezal no se mueve
            
            # Cambiar de estado
            self.estado_actual = nuevo_estado
            return True
        else:
            # Si no hay transición definida, la máquina se detiene y rechaza
            self.halted = True
            self.resultado = "Rechazada (Transición no definida)"
            return False

    def obtener_estado_actual(self): #obtiene el estado actual y lo envia al html
        """Devuelve un 'fotograma' del estado actual para mandarlo al HTML"""
        return {
            "cinta": self.cinta.obtener_contenido(),
            "blank_symbol": self.blank_symbol,
            "cabezal": self.cabezal,
            "estado": self.estado_actual,
            "halted": self.halted,
            "resultado": self.resultado
        }