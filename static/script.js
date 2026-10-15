let reproduccionAutomatica = null;

async function solicitarJson(url, opciones) {
    const respuesta = await fetch(url, opciones);
    let datos;
    try {
        datos = await respuesta.json();
    } catch {
        throw new Error(`El servidor respondió con un formato inesperado (HTTP ${respuesta.status}).`);
    }

    if (!respuesta.ok || datos.error) {
        throw new Error(datos.error || `Error del servidor (HTTP ${respuesta.status}).`);
    }

    return datos;
}

function mostrarError(mensaje) {
    const resultado = document.getElementById('resultado');
    resultado.innerText = mensaje;
    resultado.className = 'resultado rechazada';
}

// 1. Enviar la orden a Flask para cargar la máquina
async function cargarMaquina() {
    const tipo = document.getElementById('tipo-maquina').value;
    const entrada = document.getElementById('input-palabra').value;
    const botonCargar = document.getElementById('btn-cargar');
    const botonPaso = document.getElementById('btn-step');
    const botonPlay = document.getElementById('btn-play');

    pausar();
    botonCargar.disabled = true;
    botonPaso.disabled = true;
    botonPlay.disabled = true;
    document.getElementById('resultado').innerText = 'Cargando máquina...';
    document.getElementById('salida-maquina').innerText = '';

    try {
        const datos = await solicitarJson('/cargar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo: tipo, entrada: entrada })
        });

        actualizarInterfaz(datos);
        document.getElementById('resultado').innerText = '';
        document.getElementById('resultado').className = 'resultado';
        document.getElementById('salida-maquina').innerText = '';
        botonPaso.disabled = false;
        botonPlay.disabled = false;
    } catch (error) {
        mostrarError(`No se pudo cargar la máquina: ${error.message} Comprueba que Flask esté iniciado con "python app.py".`);
        document.getElementById('cinta').innerHTML = '';
        document.getElementById('estado-actual').innerText = '-';
    } finally {
        botonCargar.disabled = false;
    }
}

// 2. Dar un solo paso
async function ejecutarPaso() {
    try {
        const datos = await solicitarJson('/step', { method: 'POST' });

        actualizarInterfaz(datos);

        if (datos.halted) {
            finalizarEjecucion(datos);
        }
    } catch (error) {
        pausar();
        mostrarError(`No se pudo ejecutar el paso: ${error.message}`);
    }
}

// 3. Dibujar los cambios en pantalla
function actualizarInterfaz(datos) {
    document.getElementById('estado-actual').innerText = datos.estado;

    const contenedorCinta = document.getElementById('cinta');
    contenedorCinta.innerHTML = '';

    const posiciones = Object.keys(datos.cinta).map(Number).sort((a, b) => a - b);

    posiciones.forEach(pos => {
        const div = document.createElement('div');
        div.className = 'celda';
        div.innerText = datos.cinta[pos];

        if (pos === datos.cabezal) {
            div.classList.add('activa');
        }
        contenedorCinta.appendChild(div);
    });
}

// 4. Controles de Reproducción Automática
function reproducir() {
    document.getElementById('btn-step').disabled = true;
    document.getElementById('btn-play').disabled = true;
    document.getElementById('btn-pause').disabled = false;

    reproduccionAutomatica = setInterval(ejecutarPaso, 500);
}

function pausar() {
    clearInterval(reproduccionAutomatica);
    reproduccionAutomatica = null;
    document.getElementById('btn-step').disabled = false;
    document.getElementById('btn-play').disabled = false;
    document.getElementById('btn-pause').disabled = true;
}

function finalizarEjecucion(datos) {
    pausar();
    document.getElementById('btn-step').disabled = true;
    document.getElementById('btn-play').disabled = true;
    const divResultado = document.getElementById('resultado');
    divResultado.innerText = "Máquina detenida: " + datos.resultado;

    if (datos.resultado.includes("Aceptada")) {
        divResultado.className = 'resultado aceptada';
    } else {
        divResultado.className = 'resultado rechazada';
    }

    const posiciones = Object.keys(datos.cinta).map(Number).sort((a, b) => a - b);
    const cintaFinal = posiciones.map(pos => datos.cinta[pos]);
    const blankSymbol = datos.blank_symbol;
    while (cintaFinal[0] === blankSymbol) cintaFinal.shift();
    while (cintaFinal[cintaFinal.length - 1] === blankSymbol) cintaFinal.pop();
    document.getElementById('salida-maquina').innerText =
        `Cinta final: ${cintaFinal.join('') || '(vacía)'}`;
}