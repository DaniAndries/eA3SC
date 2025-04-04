// Funcion que maneja el envio del archivo al servidor
function print_file(event) {
  event.preventDefault(); // Prevenir el comportamiento por defecto del formulario

  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.textContent = "Enviando..."; // Cambia el texto del boton a "Enviando..."
  submitButton.disabled = true; // Desactiva el boton para evitar envios multiples

  let formData = new FormData();
  // Agrega el numero de copias al formulario
  formData.append("copies", document.getElementById("copiesNumber").value);

  let fileInput = document.getElementById("formatField").files[0];
  if (!fileInput) {
    alert("Por favor, selecciona un archivo.");
    resetSubmitButton(); // Restaura el boton si no hay archivo
    return;
  }
  formData.append("file", fileInput);

  const driverInput = document.querySelector('input[name="driver"]:checked');
  if (driverInput) {
    formData.append("driver", driverInput.value); // Agrega el modo de impresion seleccionado
  } else {
    alert("Por favor, selecciona un modo de impresión.");
    resetSubmitButton(); // Restaura el boton si no se selecciona un modo
    return;
  }

  let printerSelect = document.getElementById("printerSelect");
  let printerId = printerSelect.value;
  if (!printerId || printerSelect.options.length === 0) {
    alert("Por favor, selecciona una impresora válida.");
    resetSubmitButton(); // Restaura el boton si no se selecciona impresora
    return;
  }

  // Realiza la peticion POST para enviar el archivo a la impresora
  fetch(`/printers/${encodeURIComponent(printerId)}`, {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      return response.text().then((text) => {
        if (!response.ok) {
          try {
            const data = JSON.parse(text);
            throw new Error(
              data.error || `Error en el servidor (${response.status})`
            );
          } catch {
            throw new Error(`Error desconocido: ${text}`);
          }
        }
        return JSON.parse(text);
      });
    })
    .then((data) => {
      alert(data.message || "Documento enviado correctamente");
      document.getElementById("print").reset(); // Resetea el formulario despues de enviar
      loadPrinters(); // Recarga la lista de impresoras
    })
    .catch((error) => {
      console.error("Error:", error);
      alert(
        `Error: ${
          error.message || "Problema al enviar el documento a imprimir"
        }`
      );
    })
    .finally(resetSubmitButton); // Restaura el boton al final
}

function saveSettings(event) {
  event.preventDefault();
  console.log("Guardando configuración...");
  // Obtener los valores de los campos del formulario
  console.log(document.getElementById("NOTIFY").checked);
  const NOTIFY = document.getElementById("NOTIFY").checked;
  const NOTIFICATION = document.getElementById("NOTIFICATION").value;
  const EMAIL = document.getElementById("EMAIL").value;
  const PASSWORD = document.getElementById("PASSWORD").value;
  const PORT = document.getElementById("PORT").value;
  const HOST = document.getElementById("HOST").value;
  const TO = document.getElementById("TO").value;
  const CC = document.getElementById("CC").value;
  const SUBJECT = document.getElementById("SUBJECT").value;
  const PRINT_SC = document.getElementById("printerSelect").value;
  const TIME_SECONDS = parseInt(document.getElementById("TIME_SECONDS").value,10);
  const USER_DB = document.getElementById("USER_DB").value;
  const PASSWORD_DB = document.getElementById("PASSWORD_DB").value;
  const SERVER = document.getElementById("SERVER").value;
  const DATABASE_DB = document.getElementById("DATABASE_DB").value;

  // Validación de campos
  if (!NOTIFICATION || !EMAIL || !PASSWORD || !PORT || !HOST || !TO || !CC || !SUBJECT || !PRINT_SC || !TIME_SECONDS || !USER_DB || !PASSWORD_DB || !SERVER || !DATABASE_DB) {
    alert("Por favor, complete todos los campos.");
    return;
  }
  fetch("/management/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      NOTIFY, NOTIFICATION, EMAIL, PASSWORD, PORT, HOST, TO, CC, SUBJECT, PRINT_SC, TIME_SECONDS, USER_DB, PASSWORD_DB, SERVER, DATABASE_DB
    }),
  })
  .then((response) => response.json())
  .then((data) => {
    alert(data.message);
  })
  .catch((error) => {
      console.error("Error al guardar configuración:", error);
      alert("Error al guardar configuración.");
    });
}

// Función que restaura el texto y habilita el botón de envío
function resetSubmitButton() {
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.textContent = "Guardar";
  submitButton.disabled = false;
}

// Función para cargar la lista de impresoras disponibles
let printersData = {}; // Objeto global para almacenar los datos de las impresoras
function loadPrinters() {
  const printerSelect = document.getElementById("printerSelect");
  const selectedPrinter = printerSelect.value;
  const printerConfig = printersData[selectedPrinter];

  fetch("/printers")
    .then((response) => {
      if (!response.ok) {
        throw new Error("No se pudieron cargar las impresoras");
      }
      return response.json();
    })
    .then((printers) => {
      printerSelect.innerHTML = ""; // Limpia las opciones previas
      printersData = {}; // Reinicia el objeto global

      if (!Array.isArray(printers) || printers.length === 0) {
        printerSelect.innerHTML = '<option value="">No se encontraron impresoras</option>';
        return;
      }

      printers.forEach((printer) => {
        // Almacena la configuración en el objeto global
        printersData[printer.name] = printer;

        // Agrega la impresora al select
        const option = document.createElement("option");
        option.value = printer.name;
        option.textContent = printer.name;
        printerSelect.appendChild(option);
      });

      // Selecciona la impresora que coincide con PRINT_SC
      const printSC = "{{PRINTER_SC}}"; // Suponiendo que PRINTER_SC es una variable global o inyectada en el HTML
      if (printSC && printersData[printSC]) {
        printerSelect.value = printSC;
      } else {
        // Si no hay coincidencia, selecciona el primero disponible
        printerSelect.value = printers[0].name;
      }

      // Dispara un evento para actualizar la selección
      printerSelect.dispatchEvent(new Event("change"));
    })
    .catch((error) => {
      console.error("Error al cargar impresoras:", error);
      printerSelect.innerHTML = '<option value="">Error al cargar impresoras</option>';
    });
}

// Evento que se dispara cuando la página se ha cargado completamente
document.addEventListener("DOMContentLoaded", function () {
  loadPrinters();
  form="";
  if (window.location.pathname.includes("config")) {
    form = document.getElementById("PropertiesForm");
    if (form) {
      form.addEventListener("submit", saveSettings);
    } else {
      console.error("No se encontró el formulario");
    }
  } else if (window.location.pathname.includes("print")) {
    form = document.getElementById("print");
    if (form) {
      form.addEventListener("submit", print_file);
    } else {
      console.error("No se encontró el formulario");
    }
  }
});

const notifyCheckbox = document.getElementById("NOTIFY");
const notificationInput = document.getElementById("NOTIFICATION");
function toggleNotificationInput() {
  notificationInput.disabled = !notifyCheckbox.checked;
}
document.addEventListener("DOMContentLoaded", function() {
  if (window.location.pathname.includes("config")) {
    toggleNotificationInput();
    notifyCheckbox.addEventListener("change", toggleNotificationInput);
  }
});
