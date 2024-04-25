 <?php
    // Recibir la cadena de parámetros
    $parametrosString = $_GET['parametros'];
    // Convertir la cadena en un array separado por comas
    $parametros = explode(',', $parametrosString);

    //var_dump($parametros);
    ?>

 <!DOCTYPE html>
 <html lang="es">

 <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>Editar Contacto</title>
     <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
     <link rel="stylesheet" href="style1.css">
     <script src="controller.js"></script>
 </head>

 <body>

     <div class="w3-container">
         <h3>Editar Contacto</h3>
         <a href="index.php"><button class="w3-button w3-round w3-white w3-hover-light-gray w3-border"><img src="imagenes/back.png" height="32" width="32"> Volver </button></a>
     </div>
     <div class="w3-container myform">
         <h3>Datos Contacto</h3>
         <form class="w3-container " action="javascript:editar()" id="editform">
             <div class="w3-row">
                 <div class="w3-half">

                     <input type="hidden" value="<?php echo ($parametros[0]) ?>" name="idcontactos">

                     <label class=""><b>Nombre</b></label>
                     <input class="w3-input w3-border w3-margin long" type="text" name="nombre" id="nombre" maxlength="45" value="<?php echo ($parametros[1]) ?>" required>

                     <label class="w3-text-black"><b>Apellido</b></label>
                     <input class="w3-input w3-border w3-margin long" type="text" name="apellido" id="apellido" maxlength="45" value="<?php echo ($parametros[2]) ?>" required>

                     <label class="w3-text-black"><b>Email</b></label>
                     <input class="w3-input w3-border w3-margin long" type="email" name="email" id="email" maxlength="45" value="<?php echo ($parametros[3]) ?>" required>
                 </div>
                 <div class="w3-half">
                     <label class="w3-text-black"><b>Teléfono 1</b></label>
                     <input class="w3-input w3-border w3-margin short" type="tel" name="telefono1" id="telefono1" maxlength="20" value="<?php echo ($parametros[4]) ?>" required>

                     <label class="w3-text-black"><b>Teléfono 2</b></label>
                     <input class="w3-input w3-border w3-margin short" type="tel" name="telefono2" id="telefono2" maxlength="20" value="<?php if (isset($parametros[5])) {
                                                                                                                                            echo ($parametros[5]);
                                                                                                                                        } ?>">

                     <label class="w3-text-black"><b>Teléfono 3</b></label>
                     <input class="w3-input w3-border w3-margin short" type="tel" name="telefono3" id="telefono3" maxlength="20" value="<?php if (isset($parametros[6])) {
                                                                                                                                            echo ($parametros[6]);
                                                                                                                                        } ?>">

                     <div class="button-container">
                         <button class="w3-button w3-round w3-white w3-hover-light-gray w3-border w3-right"><img src="imagenes/editar.png" height="32" width="32"> Editar Registro </button>
                     </div>
                 </div>
             </div>
         </form>
         <div class="w3-container" id="mensaje"></div>
     </div>
 </body>

 </html>