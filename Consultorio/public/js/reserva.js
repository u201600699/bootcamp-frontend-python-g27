const form = document.getElementById("form-reserva");
const msg = document.getElementById("mensaje");
const btnWhatsapp = document.getElementById("btn-whatsapp");

const $ = (id) => document.getElementById(id);
const fields = ["servicio", "fecha", "hora", "nombre", "telefono", "email"];

// Limita la fecha mínima a hoy
(function setMinDate(){
  const f = $("fecha");
  if (!f) return;
  const today = new Date();
  const iso = today.toISOString().split("T")[0];
  f.setAttribute("min", iso);
})();