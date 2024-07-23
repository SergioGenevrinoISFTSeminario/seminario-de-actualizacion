import { getAuthHeaders } from '../authHeaders';
import { checkSessionStatus } from '../sessionTimer';
const sessionidusuario = localStorage.getItem('idusuario');
const sessionusuario = localStorage.getItem('usuario');
const sessionpassword = localStorage.getItem('contraseña');
const sessiontoken = localStorage.getItem('token');
const sessionMetodo = localStorage.getItem('selectedAuthMethod');
console.log(sessionidusuario, sessionusuario, sessionpassword, sessiontoken);

document.addEventListener('DOMContentLoaded', function () {

    // VERIFICAR QUE LA SESION NO HAYA EXPIRADO
    checkSessionStatus();

    // Realiza la solicitud JSON al archivo PHP con método POST y headers personalizados
    fetch('../verificarPermiso.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Idusuario': sessionidusuario,
            'X-Usuario': sessionusuario,
            'X-Token': sessiontoken,
            'X-Operacion': '3' // BORRADO
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener los datos');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            // Verifica si hay un error en la respuesta
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            if (data.success) {
                console.log('Borrado:', data.message);
                document.getElementById('puestoForm').style.display = 'block';

            } else {
                console.log('Usuario no autorizado:', data.message);
                alert('No esta autorizado para ejecutar esta accion.')
            }

        })
        .catch(error => {
            console.error('Error al obtener los datos:', error);
        });

    document.getElementById('backButton').addEventListener('click', function () {
        window.location.href = '../dashboard.html';
    });
});


document.getElementById('puestoForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const idpuesto = document.getElementById('idpuesto').value;   
    const data = { idpuesto: idpuesto };

    let headerSelect = getAuthHeaders('3'); // BORRADO
    console.log('headerSelect envío', headerSelect);
  
    console.log(data);
    fetch('borrado_puesto.php', {
        method: 'POST',
        headers: headerSelect,
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Puesto borrado exitosamente');
               
                if (sessionMetodo === 'token' && data.token) {
                    // ALMACENAR NUEVO TOKEN
                    console.log('New token:', data.token);
                    localStorage.setItem('token', data.token);
                }

            } else {
                alert('Error al borrar puesto: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error al borrar puesto');
        });
});

