// 🔹 Función segura para obtener valores
function getValue(id) {
  const el = document.getElementById(id);
  return el ? parseFloat(el.value) || 0 : 0;
}

// 🔹 Función segura para escribir en HTML 
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.innerText = value;
  } else {
    console.warn(`Elemento no encontrado: ${id}`);
  }
}

// 🔹 Función principal
async function calcular() {

  const quincena = document.getElementById("quincena_input")?.value;
  const afiliado = document.getElementById("afiliado")?.value === "true";

  const data = {
    quincena: quincena,
    categoria: document.getElementById("categoria_input")?.value,
    horas: getValue("horas"),
    adicionales: getValue("adicionales"),
    feriados: getValue("feriados"),
    antiguedad: getValue("antiguedad"),
    ausencias: getValue("ausencias"),
    afiliado: afiliado
  };

  if (quincena === "2") {
    data.horas_q1 = getValue("horas_q1");
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/calcular", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error("Error en el backend");
    }

    const result = await response.json();

    actualizarUI(result, data);

  } catch (error) {
    console.error("Error:", error);
    alert("Error conectando con el servidor");
  }
}

// 🔹 Actualizar UI (SEGURA)
function actualizarUI(result, data) {

  setText("quincena", result.quincena === 1 ? "1ra" : "2da");

  setText("categoria", data.categoria);
  setText("valor_hora", result.detalle?.valor_hora);

  setText("horas", data.horas);
  setText("sueldo_base", result.detalle?.sueldo_base);

  setText("acfa", result.detalle?.acfa_total);

  setText("cant_adicionales", data.adicionales);
  setText("adicionales", result.detalle?.adicionales);

  setText("cant_feriados", data.feriados);
  setText("feriados", result.detalle?.feriados);

  setText("antiguedad_anios", data.antiguedad);
  setText("antiguedad", result.antiguedad);

  setText("presentismo_quin", result.presentismo_quin || 0);
  setText("presentismo_men", result.presentismo_men || 0);

  setText("premio", result.premio_produccion || 0);

  setText("total_bruto", result.total_bruto);
  setText("descuento", result.descuento);
  setText("porcentaje", result.descuento_porcentaje);
  setText("total_final", result.total_final);
}