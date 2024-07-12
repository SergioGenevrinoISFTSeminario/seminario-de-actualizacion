<?php
include('../conn.php');

try {
    // Crear conexión usando PDO
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    // Configurar el modo de error de PDO a excepción
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Verificar el método de la solicitud
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        echo json_encode(array('success' => false, 'message' => 'Método no permitido'));
        http_response_code(405); // Método no permitido
        exit();
    }

    // Obtener datos del cuerpo de la solicitud JSON
    $data = json_decode(file_get_contents('php://input'), true);
    if (!isset($data['accion'])) {
        echo json_encode(array('success' => false, 'message' => 'Datos incompletos'));
        http_response_code(400); // Bad request
        exit();
    }

    $accion = $data['accion'];
    
    // Preparar y ejecutar la inserción
    $stmt = $conn->prepare("INSERT INTO acciones (Accion) VALUES (:accion)");
    $stmt->bindParam(':accion', $accion);
    
    if ($stmt->execute()) {
        echo json_encode(array('success' => true, 'message' => 'Accion registrada exitosamente'));
    } else {
        echo json_encode(array('success' => false, 'message' => 'Error al registrar accion'));
    }
} catch (PDOException $e) {
    echo json_encode(array('success' => false, 'message' => 'Error: ' . $e->getMessage()));
}

// Cerrar conexión
$conn = null;
