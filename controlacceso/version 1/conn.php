<?php

// Datos de conexión a la base de datos
$servername = "localhost";
$username = "root";
$password = "";
$database = "controlacceso";

// Crear conexión
$conn = new mysqli($servername, $username, $password, $database);

// Verificar la conexión
if ($conn->connect_error) {
die(json_encode(array("mensaje" => "Conexión fallida: " . $conn->connect_error)));
}