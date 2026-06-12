"""
Bot de Telegram - Horarios de Colectivo
Rutas: G.ROCA ↔ GOMEZ ↔ GUERR. ↔ ALLEN ↔ FDEZ.ORO ↔ CIPO ↔ NQN ↔ ETON
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ── Configuración ──────────────────────────────────────────────────────────────
TOKEN = "TU_TOKEN_AQUI"  # ← Reemplazá con el token de @BotFather

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ── Datos: horarios ida (G.ROCA → ETON) ───────────────────────────────────────
# Cada fila es un servicio. Las columnas corresponden a las paradas en orden.
PARADAS_IDA = ["G.ROCA", "GOMEZ", "GUERR.", "ALLEN", "FDEZ.ORO", "CIPO", "NQN", "ETON"]

HORARIOS_IDA = [
    [None,  None,  None,  "04:55", "05:10", "05:25", "05:45", "05:55"],
    [None,  None,  None,  None,    "05:50", "06:10", "06:40", "06:50"],
    ["05:00","05:15","05:25","05:40","05:55","06:10","06:40","06:50"],
    ["05:55","06:10","06:20","06:35","06:50","07:05","07:35","07:45"],
    ["06:20","06:35","06:45","07:00","07:15","07:30","08:00","08:15"],
    ["06:55","07:10","07:25","07:40","07:55","08:10","08:40","08:50"],
    ["07:15","07:30","07:40","07:55","08:10","08:25","08:55","09:10"],
    ["07:55","08:10","08:20","08:35","08:50","09:05","09:35","09:50"],
    ["08:35","08:50","09:00","09:15","09:30","09:45","10:15","10:30"],
    ["09:15","09:30","09:40","09:55","10:10","10:25","10:55","11:10"],
    ["09:55","10:10","10:20","10:35","10:50","11:05","11:35","11:50"],
    ["10:45","11:00","11:10","11:25","11:40","11:55","12:25","12:40"],
    ["11:25","11:40","11:50","12:05","12:20","12:35","13:05","13:20"],
    ["12:05","12:20","12:30","12:45","13:00","13:15","13:45","14:00"],
    ["13:00","13:15","13:25","13:40","13:55","14:10","14:40","14:50"],
    ["13:45","14:00","14:10","14:25","14:40","14:55","15:25","15:40"],
    ["14:35","14:50","15:00","15:15","15:30","15:45","16:15","16:30"],
    ["15:15","15:30","15:40","15:55","16:10","16:25","16:55","17:10"],
    ["16:00","16:15","16:25","16:40","16:55","17:10","17:40","17:50"],
    ["16:25","16:40","16:50","17:05","17:20","17:35","18:05","18:20"],
    ["17:15","17:30","17:40","17:55","18:10","18:25","18:55","19:10"],
    ["17:55","18:10","18:20","18:35","18:50","19:05","19:35","19:50"],
    ["18:25","18:40","18:50","19:05","19:20","19:35","20:05","20:20"],
    ["19:10","19:25","19:35","19:50","20:05","20:20","20:50","21:05"],
    ["19:50","20:05","20:15","20:30","20:45","21:00","21:30","21:40"],
    ["20:40","20:55","21:05","21:20","21:35","21:50","22:20","22:30"],
    ["21:25","21:40","21:50","22:05","22:20","22:35","23:05", None  ],
    ["22:05","22:20","22:30","22:45","23:00","23:15","23:45", None  ],
    ["22:50","23:05","23:20","23:35","23:50","00:05","00:35", None  ],
    ["00:10","00:25","00:35","00:50","01:05","01:05", None,   None  ],
]

# ── Datos: horarios vuelta (ETON → G.ROCA) ────────────────────────────────────
PARADAS_VUELTA = ["ETON", "NQN", "CIPO", "FDEZ.ORO", "ALLEN", "GUERR.", "GOMEZ", "G.ROCA"]

HORARIOS_VUELTA = [
    [None,  None,  "04:40","04:50","05:05","05:15","05:25","05:35"],
    [None,  "05:20","05:30","05:45","06:00","06:10","06:25","06:25"],  # ajuste menor
    [None,  "05:45","06:00","06:15","06:30","06:45","None", "06:50"],
    ["05:15","05:25","05:55","06:05","06:20","06:30","06:40","06:55"],
    ["05:55","06:10","06:40","06:55","07:10","07:25","07:35","07:50"],
    ["06:40","06:55","07:25","07:40","07:55","08:10","08:20","08:30"],
    ["07:15","07:30","08:00","08:15","08:30","08:45","08:55","09:10"],
    ["08:00","08:15","08:45","09:00","09:15","09:30","09:40","09:55"],
    [None,  "08:45","09:15","09:30","09:45", None,   None,   None  ],
    ["08:35","08:50","09:20","09:35","09:50","10:05","10:15","10:30"],
    ["09:20","09:35","10:05","10:20","10:35","10:50","11:00","11:15"],
    ["10:00","10:15","10:45","11:00","11:15","11:30","11:45","12:00"],
    ["10:40","10:55","11:25","11:40","11:55","12:10","12:20","12:35"],
    ["11:20","11:35","12:05","12:20","12:35","12:50","13:00","13:15"],
    ["12:00","12:15","12:45","13:00","13:15","13:30","13:40","13:55"],
    ["12:50","13:05","13:35","13:50","14:05","14:15","14:30","14:45"],
    ["13:30","13:45","14:15","14:30","14:45","15:00","15:10","15:25"],
    ["14:10","14:25","14:55","15:10","15:25","15:40","15:50","16:05"],
    ["15:00","15:15","15:45","16:00","16:15","16:30","16:40","16:55"],
    ["15:50","16:05","16:35","16:50","17:05","17:20","17:30","17:45"],
    ["16:40","16:55","17:25","17:40","17:55","18:10","18:20","18:35"],
    ["17:20","17:35","18:05","18:20","18:35","18:50","19:00","19:15"],
    ["18:00","18:15","18:45","19:00","19:15","19:30","19:40","19:55"],
    ["18:40","18:55","19:25","19:40","19:55","20:10","20:20","20:35"],
    ["19:20","19:35","20:05","20:20","20:35","20:50","21:00","21:15"],
    ["20:00","20:15","20:45","21:00","21:15","21:30","21:40","21:55"],
    ["20:40","20:55","21:25","21:40","21:55","22:10","22:20","22:35"],
    ["21:30","21:45","22:15","22:30","22:45", None,   None,   None  ],
    ["22:20","22:35","23:05","23:20","23:35","23:50","00:00","00:10"],
    ["23:00","23:15","23:45","00:00","00:15","00:30","00:40","00:55"],
]

# ── Nombres alternativos / alias ───────────────────────────────────────────────
ALIAS = {
    "general roca": "G.ROCA", "groca": "G.ROCA", "g roca": "G.ROCA", "roca": "G.ROCA",
    "gomez": "GOMEZ", "gómez": "GOMEZ",
    "guerrero": "GUERR.", "guerr": "GUERR.",
    "allen": "ALLEN",
    "fernandez oro": "FDEZ.ORO", "fdez oro": "FDEZ.ORO", "fernandez": "FDEZ.ORO",
    "fernández oro": "FDEZ.ORO", "fdez.oro": "FDEZ.ORO",
    "cipolletti": "CIPO", "cipo": "CIPO", "cipolleti": "CIPO",
    "neuquen": "NQN", "neuquén": "NQN", "nqn": "NQN",
    "eton": "ETON",
}

# ── Utilidades ─────────────────────────────────────────────────────────────────
def normalizar(texto: str) -> str | None:
    """Convierte texto libre al nombre oficial de parada."""
    t = texto.lower().strip()
    if t in ALIAS:
        return ALIAS[t]
    for parada in PARADAS_IDA:
        if t == parada.lower():
            return parada
    return None


def proximos_horarios(origen: str, destino: str, cantidad: int = 5) -> list[dict]:
    """Devuelve los próximos N servicios entre dos paradas."""
    from datetime import datetime

    ahora = datetime.now().strftime("%H:%M")

    # Determinar dirección
    if origen in PARADAS_IDA and destino in PARADAS_IDA:
        idx_o = PARADAS_IDA.index(origen)
        idx_d = PARADAS_IDA.index(destino)
        if idx_o < idx_d:
            horarios = HORARIOS_IDA
            paradas = PARADAS_IDA
        else:
            horarios = HORARIOS_VUELTA
            paradas = PARADAS_VUELTA
    elif origen in PARADAS_VUELTA and destino in PARADAS_VUELTA:
        horarios = HORARIOS_VUELTA
        paradas = PARADAS_VUELTA
    else:
        return []

    idx_o = paradas.index(origen)
    idx_d = paradas.index(destino)

    if idx_o >= idx_d:
        return []

    resultados = []
    for fila in horarios:
        h_o = fila[idx_o]
        h_d = fila[idx_d]
        if h_o and h_d:
            resultados.append({"sale": h_o, "llega": h_d})

    # Ordenar y filtrar los próximos desde ahora
    futuros = [r for r in resultados if r["sale"] >= ahora]
    pasados = [r for r in resultados if r["sale"] < ahora]
    ordenados = futuros + pasados  # wrap-around para mostrar siguiente día si es tarde

    return ordenados[:cantidad]


def todos_horarios(origen: str, destino: str) -> list[dict]:
    """Devuelve todos los servicios entre dos paradas."""
    if origen in PARADAS_IDA and destino in PARADAS_IDA:
        idx_o = PARADAS_IDA.index(origen)
        idx_d = PARADAS_IDA.index(destino)
        if idx_o < idx_d:
            horarios, paradas = HORARIOS_IDA, PARADAS_IDA
        else:
            horarios, paradas = HORARIOS_VUELTA, PARADAS_VUELTA
    else:
        return []

    idx_o = paradas.index(origen)
    idx_d = paradas.index(destino)
    if idx_o >= idx_d:
        return []

    return [
        {"sale": f[idx_o], "llega": f[idx_d]}
        for f in horarios
        if f[idx_o] and f[idx_d]
    ]


# ── Handlers de Telegram ───────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🚌 *Horarios de Colectivo*\n\n"
        "Puedo decirte a qué hora sale el próximo servicio.\n\n"
        "📍 *Paradas disponibles:*\n"
        "General Roca · Gómez · Guerrero · Allen\n"
        "Fernández Oro · Cipolletti · Neuquén · ETON\n\n"
        "💬 *Escribime directamente*, por ejemplo:\n"
        "→ `de NQN a ETON`\n"
        "→ `Allen a Neuquén`\n"
        "→ `Cipolletti hacia General Roca`\n\n"
        "O usá /horarios para seleccionar paradas con botones."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def horarios_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra teclado para elegir parada de origen."""
    botones = [
        [InlineKeyboardButton(p, callback_data=f"origen:{p}")]
        for p in PARADAS_IDA
    ]
    reply_markup = InlineKeyboardMarkup(botones)
    await update.message.reply_text("🚌 ¿Desde qué parada salís?", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("origen:"):
        origen = data.split(":")[1]
        context.user_data["origen"] = origen
        idx_o = PARADAS_IDA.index(origen)

        # Solo mostrar destinos válidos (adelante en la ruta)
        posibles_ida = PARADAS_IDA[idx_o + 1:]
        posibles_vuelta = [p for p in PARADAS_VUELTA if PARADAS_IDA.index(p) < idx_o] if idx_o > 0 else []
        destinos = posibles_ida + posibles_vuelta

        botones = [
            [InlineKeyboardButton(p, callback_data=f"destino:{p}")]
            for p in destinos
        ]
        reply_markup = InlineKeyboardMarkup(botones)
        await query.edit_message_text(
            f"📍 Origen: *{origen}*\n\n¿A dónde vas?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data.startswith("destino:"):
        destino = data.split(":")[1]
        origen = context.user_data.get("origen")
        if not origen:
            await query.edit_message_text("❌ Empezá de nuevo con /horarios")
            return

        proximos = proximos_horarios(origen, destino, cantidad=5)
        if not proximos:
            await query.edit_message_text(f"❌ No encontré servicios de *{origen}* a *{destino}*.", parse_mode="Markdown")
            return

        lineas = [f"🚌 *{origen}* → *{destino}*\n"]
        lineas.append("⏰ *Próximos servicios:*")
        for s in proximos:
            lineas.append(f"  Sale: `{s['sale']}` · Llega: `{s['llega']}`")

        botones = [[InlineKeyboardButton("📋 Ver todos los horarios", callback_data=f"todos:{origen}:{destino}")],
                   [InlineKeyboardButton("🔄 Nueva consulta", callback_data="nueva")]]
        reply_markup = InlineKeyboardMarkup(botones)

        await query.edit_message_text(
            "\n".join(lineas),
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data.startswith("todos:"):
        _, origen, destino = data.split(":")
        todos = todos_horarios(origen, destino)
        if not todos:
            await query.edit_message_text("❌ No se encontraron horarios.", parse_mode="Markdown")
            return

        lineas = [f"📋 *Todos los servicios {origen} → {destino}*\n"]
        for s in todos:
            lineas.append(f"  `{s['sale']}` → `{s['llega']}`")

        botones = [[InlineKeyboardButton("🔄 Nueva consulta", callback_data="nueva")]]
        reply_markup = InlineKeyboardMarkup(botones)

        await query.edit_message_text(
            "\n".join(lineas),
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data == "nueva":
        botones = [
            [InlineKeyboardButton(p, callback_data=f"origen:{p}")]
            for p in PARADAS_IDA
        ]
        reply_markup = InlineKeyboardMarkup(botones)
        await query.edit_message_text("🚌 ¿Desde qué parada salís?", reply_markup=reply_markup)


async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Interpreta mensajes como 'de NQN a ETON' o 'Allen Neuquén'."""
    texto = update.message.text.lower()

    # Intentar extraer origen y destino
    origen_encontrado = None
    destino_encontrado = None

    for alias, parada in sorted(ALIAS.items(), key=lambda x: -len(x[0])):
        if alias in texto:
            if origen_encontrado is None:
                idx = texto.index(alias)
                origen_encontrado = (idx, parada)
            elif destino_encontrado is None:
                idx = texto.index(alias)
                destino_encontrado = (idx, parada)
                break

    if origen_encontrado and destino_encontrado:
        # El que aparece antes en el texto es el origen
        if origen_encontrado[0] > destino_encontrado[0]:
            origen_encontrado, destino_encontrado = destino_encontrado, origen_encontrado
        origen = origen_encontrado[1]
        destino = destino_encontrado[1]
    else:
        await update.message.reply_text(
            "🤔 No entendí bien la consulta.\n\n"
            "Probá con algo como:\n"
            "→ `de NQN a ETON`\n"
            "→ `Allen Neuquén`\n\n"
            "O usá /horarios para elegir con botones.",
            parse_mode="Markdown"
        )
        return

    proximos = proximos_horarios(origen, destino, cantidad=5)
    if not proximos:
        await update.message.reply_text(
            f"❌ No encontré servicios de *{origen}* a *{destino}*.\n"
            "Verificá las paradas con /horarios.",
            parse_mode="Markdown"
        )
        return

    lineas = [f"🚌 *{origen}* → *{destino}*\n"]
    lineas.append("⏰ *Próximos servicios:*")
    for s in proximos:
        lineas.append(f"  Sale: `{s['sale']}` · Llega: `{s['llega']}`")

    botones = [[InlineKeyboardButton("📋 Ver todos", callback_data=f"todos:{origen}:{destino}")]]
    reply_markup = InlineKeyboardMarkup(botones)

    await update.message.reply_text(
        "\n".join(lineas),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("horarios", horarios_comando))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_libre))

    print("✅ Bot iniciado. Presioná Ctrl+C para detenerlo.")
    app.run_polling()


if __name__ == "__main__":
    main()
