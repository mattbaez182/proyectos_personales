# Categorias
CATEGORIAS = {
    "esp": 5790.38,
    "1": 5390.17,
    "2": 4800.75,
    "3": 4500.25,
    "4": 4200.10
}

VIATICO = 2.2
PRESENTISMO_QUIN = 89926.07
PRESENTISMO_MEN = 65756.69

#-----------------------------------------------------------------------
#  Calcular Categoria 

def calcular_categoria(categoria):
    valor_hora = CATEGORIAS.get(categoria)

    if valor_hora is None:
        return {"error": "Categoría inválida"}

    acfa = valor_hora * 0.15
    valor_hora_total = valor_hora + acfa + VIATICO

    return {
        "valor_hora": valor_hora,
        "acfa": acfa,
        "valor_hora_total": valor_hora_total
    }


#---------------------------------------------------------------------------
#  Base de Calculo

def calculo_base(categoria, horas, adicionales, feriados, antiguedad, ausencias, calcular_antiguedad=True):

    cat = calcular_categoria(categoria)
    if "error" in cat:
        return cat

    valor_hora_total = cat["valor_hora_total"]
    acfa = cat["acfa"]

    #  Sueldo base
    sueldo_base = (valor_hora_total - acfa) * horas

    #  ACFA total
    acfa_total = acfa * horas

    #  Adicionales
    adicionales_valor = valor_hora_total / 2
    adicionales_total = adicionales_valor * adicionales

    #  Feriados
    pago_feriados = 0
    if feriados > 0:
        feriados_base = (feriados * 8) * valor_hora_total
        pago_feriados = feriados_base * 1.2

    #  Ausencias / Presentismo
    presentismo_quin = 0
    presentismo_men = 0

    if ausencias == 0:
        presentismo_quin = PRESENTISMO_QUIN
        presentismo_men = PRESENTISMO_MEN

    #  Antigüedad (solo Q1)
    adicional_antiguedad = 0
    
    if calcular_antiguedad:
        base_antiguedad = (
            sueldo_base +
            acfa_total +
            adicionales_total +
            pago_feriados +
            presentismo_quin +
            presentismo_men
        )

        adicional_antiguedad = base_antiguedad * (antiguedad / 100)

    return {
        "valor_hora": cat["valor_hora"],
        "valor_hora_total": valor_hora_total,
        "acfa": acfa,
        "acfa_total": acfa_total,
        "sueldo_base": sueldo_base,
        "adicionales": adicionales_total,
        "feriados": pago_feriados,
        "presentismo_quin": presentismo_quin,
        "presentismo_men": presentismo_men,
        "antiguedad": adicional_antiguedad
    }
          
                   
# ------------------------------------------------------------------------
#  Premio Produccion

def premio_produccion(categoria, horas_q1, sueldo_base_q2, acfa_total_q2):

    # Obtener datos de la categoría (Q1)
    cat = calcular_categoria(categoria)

    if "error" in cat:
        return 0

    valor_hora = cat["valor_hora"]
    #print(valor_hora)
    acfa = cat["acfa"]
    #print(acfa)

    # Primera quincena (solo horas)
    valor_q1 = (valor_hora + VIATICO) * horas_q1
    acfa_q1 = acfa * horas_q1
    #print(valor_q1, acfa_q1)

    # Segunda quincena
    valor_q2 = sueldo_base_q2 + acfa_total_q2
    #print(sueldo_base_q2,acfa_total_q2)

    # Premio producción (20%)
    total = (valor_q1 + acfa_q1 + valor_q2) * 0.2
    #print(total)

    return total

# ----------------------------------------------------
#  Primera Quincena


def calcular_q1(categoria, horas, adicionales, feriados, antiguedad, ausencias, afiliado):

    base = calculo_base(
        categoria, horas, adicionales, feriados, antiguedad, ausencias,
        calcular_antiguedad=True
    )

    if "error" in base:
        return base

    #  Presentismos Q1
    presentismo_quin = 0
    presentismo_men = 0

    if ausencias == 0:
        presentismo_quin = PRESENTISMO_QUIN
        presentismo_men = PRESENTISMO_MEN

    #  Total bruto
    total_bruto = (
        base["sueldo_base"] +
        base["acfa_total"] +
        base["adicionales"] +
        base["feriados"] +
        base["antiguedad"] +
        presentismo_quin +
        presentismo_men
    )

    #  Descuento
    desc = calcular_descuento(total_bruto, afiliado)

    return {
        "quincena": 1,
        "detalle": {k: round(v, 2) for k, v in base.items()},
        "horas": horas,
        "adicionales": round(adicionales,2),
        "feriados": round(feriados,2),

        "presentismo_quin": round(presentismo_quin, 2),
        "presentismo_men": round(presentismo_men, 2),

        "total_bruto": round(total_bruto, 2),
        "descuento_porcentaje": int(desc["porcentaje"] * 100),
        "descuento": round(desc["descuento"], 2),
        "total_final": round(desc["total_final"], 2)
    }


# -------------------------------------------------------------------------
#  Segunda Quincena

def calcular_q2(categoria, horas, adicionales, feriados, antiguedad, ausencias, horas_q1, afiliado):

    base = calculo_base(
        categoria, horas, adicionales, feriados, antiguedad, ausencias,
        calcular_antiguedad=False
    )

    if "error" in base:
        return base

    #  Premio producción
    premio = premio_produccion(
        categoria,
        horas_q1,
        base["sueldo_base"],
        base["acfa_total"]
    )

    #  Presentismo Q2 
    presentismo_quin = 0

    if ausencias == 0:
        presentismo_quin = PRESENTISMO_QUIN

    #  Antigüedad (incluye premio + presentismo)
    base_antiguedad_q2 = (
        base["sueldo_base"] +
        base["acfa_total"] +
        base["adicionales"] +
        base["feriados"] +
        premio +
        presentismo_quin
    )

    adicional_antiguedad = (base_antiguedad_q2 * antiguedad) / 100

    #  Total bruto
    total_bruto = (
        base["sueldo_base"] +
        base["acfa_total"] +
        base["adicionales"] +
        base["feriados"] +
        adicional_antiguedad +
        premio +
        presentismo_quin
    )

    #  Descuento
    desc = calcular_descuento(total_bruto, afiliado)

    return {
        "quincena": 2,
        "detalle": {k: round(v, 2) for k, v in base.items()},

        "premio_produccion": round(premio, 2),
        "presentismo_quin": round(presentismo_quin, 2),
        "horas": horas,
        "adicionales": round(adicionales,2),
        "feriados": round(feriados,2),

        "antiguedad": round(adicional_antiguedad, 2),

        "total_bruto": round(total_bruto, 2),
        "descuento_porcentaje": int(desc["porcentaje"] * 100),
        "descuento": round(desc["descuento"], 2),
        "total_final": round(desc["total_final"], 2)
    }

# -----------------------------------------------------------
#   Calculo Descuentos


def calcular_descuento(total, afiliado):
    
    porcentaje = 0.21 if afiliado else 0.19

    descuento = total * porcentaje
    total_final = total - descuento

    return {
        "porcentaje": porcentaje,
        "descuento": descuento,
        "total_final": total_final
    }


# -----------------------------------------------------------------
#  Controlador Principal


def calcular_quincena(quincena, datos):

    if quincena == "1":
        return calcular_q1(
            datos["categoria"],
            datos["horas"],
            datos["adicionales"],
            datos["feriados"],
            datos["antiguedad"],
            datos["ausencias"],
            datos["afiliado"]   
        )

    elif quincena == "2":
        return calcular_q2(
            datos["categoria"],
            datos["horas"],
            datos["adicionales"],
            datos["feriados"],
            datos["antiguedad"],
            datos["ausencias"],
            datos["horas_q1"],
            datos["afiliado"]   
        )

    return {"error": "Quincena inválida"}

#------------------------------------------------------------------------
# Ejemplo de uso

datos = {
    "categoria": "1",
    "horas": 88,
    "adicionales": 55,
    "feriados": 1,
    "antiguedad": 16,
    "ausencias": 0,

    # 👇 SOLO PARA Q2
    "horas_q1": 88,

    "afiliado": True   # 👈 21%
}


resultado = calcular_quincena("1", datos)
print(resultado)


print(f"- Quincena: {resultado['quincena']}")
print(f"- Categoría: {datos['categoria']}")
print(f"- Valor hora categoría: ${resultado['detalle']['valor_hora']}")
print(f"- Valor hora total: ${resultado['detalle']['valor_hora_total']}")

# Total sin descuento (calculo)
total_sin_descuento = resultado['total_final'] + resultado['descuento']

print(f"- Total sin descuento: ${round(total_sin_descuento, 2)}")

print(f"- Descuento: ${resultado['descuento']} ({resultado['descuento_porcentaje']}%)")
print(f"- Total final: ${resultado['total_final']}")

# Extra (si es Q2)
if "premio_produccion" in resultado:
    print(f"- Premio producción: ${resultado['premio_produccion']}")




