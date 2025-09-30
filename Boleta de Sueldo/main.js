(function () {
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const fmt = (n) => (isNaN(n) ? "0.00" : n.toFixed(2));

  // --- Cálculo principal de totales
  function calcular() {
    ajustarEssaludSiCorresponde(); // aplica auto 9% si está activo

    const filas = $$("#tbl-conceptos tbody tr");
    let ingresos = 0, deducciones = 0, aportes = 0;

    filas.forEach((tr) => {
      const tipo = $(".input--tipo", tr)?.value || "ingreso";
      const cant = parseFloat($(".input--cantidad", tr)?.value) || 0;
      const imp  = parseFloat($(".input--importe", tr)?.value) || 0;
      const subtotal = cant * imp;

      if (tipo === "ingreso") ingresos += subtotal;
      else if (tipo === "deduccion") deducciones += subtotal;
      else if (tipo === "aporte") aportes += subtotal;
    });

    $("#tot-ingresos").textContent = fmt(ingresos);
    $("#tot-deducciones").textContent = fmt(deducciones);
    $("#tot-aportes").textContent = fmt(aportes);

    const totalPagar = Math.max(ingresos - deducciones, 0);
    $("#tot-pagar").textContent = fmt(totalPagar);
  }

  // --- Localiza la Remuneración básica e Essalud
  function getRemBasicaMonto() {
    const filas = $$("#tbl-conceptos tbody tr");
    for (const tr of filas) {
      const concepto = ($(".input--concepto", tr)?.value || "").toLowerCase();
      const tipo = $(".input--tipo", tr)?.value;
      if (tipo === "ingreso" && concepto.includes("remuneración básica")) {
        const cant = parseFloat($(".input--cantidad", tr)?.value) || 0;
        const imp  = parseFloat($(".input--importe", tr)?.value) || 0;
        return cant * imp;
      }
    }
    return 0;
  }

  function getEssaludRow() {
    return $('[data-essalud-row]');
  }

  // --- Ajuste automático del Essalud = tasa% * Rem. básica
  function ajustarEssaludSiCorresponde() {
    const modo = $("#essalud-modo")?.value || "manual";
    if (modo !== "auto") return;

    const tasa = Math.max(parseFloat($("#essalud-tasa")?.value) || 9, 0) / 100;
    const base = getRemBasicaMonto();
    const essaludRow = getEssaludRow();
    if (!essaludRow) return;

    const inputImporte = $(".input--importe", essaludRow);
    const inputCantidad = $(".input--cantidad", essaludRow);
    const cantidad = parseFloat(inputCantidad?.value) || 1;

    // Ajustamos el importe unitario para que subtotal = base * tasa
    // subtotal = cantidad * importe_unitario  => importe_unitario = (base*tasa)/cantidad
    const importeUnit = cantidad > 0 ? (base * tasa) / cantidad : 0;
    if (inputImporte) {
      inputImporte.value = (isNaN(importeUnit) ? 0 : importeUnit).toFixed(2);
    }
  }

  // --- Wire up
  function wireTable() {
    const tabla = $("#tbl-conceptos");
    // Entradas que disparan recálculo
    tabla.addEventListener("input", (e) => {
      const t = e.target;
      if (
        t.classList.contains("input--cantidad") ||
        t.classList.contains("input--importe") ||
        t.classList.contains("input--tipo") ||
        t.classList.contains("input--concepto")
      ) calcular();
    });
    tabla.addEventListener("change", (e) => {
      const t = e.target;
      if (t.classList.contains("input--tipo")) calcular();
    });
  }

  function addRow() {
    const tbody = $("#tbl-conceptos tbody");
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input class="input input--codigo" placeholder="COD" /></td>
      <td><input class="input input--concepto" value="Nuevo concepto" /></td>
      <td>
        <select class="input input--tipo">
          <option value="ingreso" selected>Ingreso</option>
          <option value="deduccion">Deducción</option>
          <option value="aporte">Aporte empleador</option>
        </select>
      </td>
      <td><input class="input input--unidad" placeholder="Unidad" /></td>
      <td><input class="input input--cantidad" type="number" step="1" min="0" value="1" /></td>
      <td><input class="input input--importe" type="number" step="0.01" min="0" value="0.00" /></td>
    `;
    tbody.appendChild(tr);
    calcular();
  }

  function imprimir() { window.print(); }

  // Controles Essalud
  function wireEssalud() {
    $("#essalud-modo").addEventListener("change", calcular);
    $("#essalud-tasa").addEventListener("input", calcular);
  }

  document.addEventListener("DOMContentLoaded", () => {
    wireTable();
    wireEssalud();
    calcular();
    $("#btn-add-row").addEventListener("click", addRow);
    $("#btn-print").addEventListener("click", imprimir);
  });
})();
