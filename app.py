# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import base64
from io import BytesIO


# ============================================================
# EcoCharge - Sprint 3
# Protótipo de gestão inteligente de energia para eletropostos
# ============================================================


# ============================================================
# DADOS DA SIMULAÇÃO
# ============================================================

horarios = list(range(6, 23))

consumo_eletroposto = [
    20, 25, 30, 35, 45, 55, 60, 70, 75,
    80, 85, 90, 100, 110, 105, 95, 70
]

geracao_solar = [
    0, 5, 15, 30, 50, 70, 85, 95, 100,
    90, 75, 55, 30, 10, 0, 0, 0
]


# ============================================================
# FUNÇÃO PRINCIPAL DA SIMULAÇÃO
# ============================================================

def simular(bateria_inicial, capacidade_bateria):

    bateria = bateria_inicial

    energia_rede = []
    energia_solar_usada = []
    energia_bateria_usada = []
    energia_reduzida = []
    consumo_efetivo = []
    acoes_sistema = []
    nivel_bateria = []

    for i in range(len(horarios)):

        horario = horarios[i]

        consumo = consumo_eletroposto[i]

        solar = geracao_solar[i]

        solar_usada = 0
        bateria_usada = 0
        rede = 0
        reducao = 0

        # ====================================================
        # GERENCIAMENTO DE DEMANDA
        # ====================================================

        demanda = consumo

        # Consideramos 18h até 21h como horário de pico.
        # Durante esse período, o sistema reduz a demanda
        # em 20% antes de definir as fontes de energia.

        if 18 <= horario <= 21:

            reducao = consumo * 0.20

            demanda = consumo - reducao

        # ====================================================
        # PRIORIDADE 1 - ENERGIA SOLAR
        # ====================================================

        if solar >= demanda:

            solar_usada = demanda

            excedente = solar - demanda

            # Armazena o excedente na bateria
            bateria = min(
                capacidade_bateria,
                bateria + excedente
            )

            acao = (
                "Usar energia solar e armazenar "
                "o excedente na bateria"
            )

        else:

            solar_usada = solar

            restante = demanda - solar

            # =================================================
            # PRIORIDADE 2 - BATERIA
            # =================================================

            if bateria >= restante:

                bateria_usada = restante

                bateria -= restante

                acao = (
                    "Usar energia solar + bateria"
                )

            else:

                bateria_usada = bateria

                restante -= bateria

                bateria = 0

                # =============================================
                # PRIORIDADE 3 - REDE ELÉTRICA
                # =============================================

                rede = restante

                if 18 <= horario <= 21:

                    acao = (
                        "Horário de pico: demanda reduzida "
                        "em 20% e energia complementar "
                        "fornecida pela rede"
                    )

                else:

                    acao = (
                        "Usar energia solar + bateria "
                        "+ rede elétrica"
                    )

        energia_solar_usada.append(solar_usada)

        energia_bateria_usada.append(bateria_usada)

        energia_rede.append(rede)

        energia_reduzida.append(reducao)

        consumo_efetivo.append(demanda)

        acoes_sistema.append(acao)

        nivel_bateria.append(bateria)

    return (
        energia_rede,
        energia_solar_usada,
        energia_bateria_usada,
        energia_reduzida,
        consumo_efetivo,
        acoes_sistema,
        nivel_bateria
    )


# ============================================================
# CRIAÇÃO DO DATAFRAME COM PANDAS
# ============================================================

def criar_dataframe(
    energia_rede,
    energia_solar_usada,
    energia_bateria_usada,
    energia_reduzida,
    consumo_efetivo,
    acoes_sistema,
    nivel_bateria
):

    dados = pd.DataFrame({

        "Horário": horarios,

        "Consumo Original": consumo_eletroposto,

        "Consumo Efetivo": consumo_efetivo,

        "Geração Solar": geracao_solar,

        "Solar Utilizada": energia_solar_usada,

        "Bateria Utilizada": energia_bateria_usada,

        "Rede Utilizada": energia_rede,

        "Demanda Reduzida": energia_reduzida,

        "Nível da Bateria": nivel_bateria,

        "Ação do Sistema": acoes_sistema

    })

    return dados


# ============================================================
# GERAÇÃO DO GRÁFICO COM MATPLOTLIB
# ============================================================

def gerar_grafico(dados):

    plt.figure(figsize=(12, 5))

    plt.plot(
        dados["Horário"],
        dados["Consumo Original"],
        marker="o",
        linewidth=2,
        label="Consumo Original"
    )

    plt.plot(
        dados["Horário"],
        dados["Consumo Efetivo"],
        marker="o",
        linewidth=2,
        label="Consumo Efetivo"
    )

    plt.plot(
        dados["Horário"],
        dados["Geração Solar"],
        marker="o",
        linewidth=2,
        label="Geração Solar"
    )

    plt.plot(
        dados["Horário"],
        dados["Bateria Utilizada"],
        marker="o",
        linewidth=2,
        label="Bateria"
    )

    plt.plot(
        dados["Horário"],
        dados["Rede Utilizada"],
        marker="o",
        linewidth=2,
        label="Rede"
    )

    plt.xlabel("Horário")

    plt.ylabel("Energia (kWh)")

    plt.title(
        "EcoCharge - Gestão Energética por Horário"
    )

    plt.xticks(horarios)

    plt.grid(True, alpha=0.3)

    plt.legend()

    plt.tight_layout()

    imagem = BytesIO()

    plt.savefig(
        imagem,
        format="png",
        bbox_inches="tight"
    )

    plt.close()

    imagem.seek(0)

    grafico_base64 = base64.b64encode(
        imagem.getvalue()
    ).decode("utf-8")

    return grafico_base64


# ============================================================
# ANÁLISE DOS RESULTADOS
# ============================================================

def analisar(dados):

    consumo_original_total = (
        dados["Consumo Original"].sum()
    )

    consumo_efetivo_total = (
        dados["Consumo Efetivo"].sum()
    )

    rede_total = (
        dados["Rede Utilizada"].sum()
    )

    solar_total = (
        dados["Solar Utilizada"].sum()
    )

    bateria_total = (
        dados["Bateria Utilizada"].sum()
    )

    reducao_total = (
        dados["Demanda Reduzida"].sum()
    )

    # Quantidade de energia que não precisou
    # ser fornecida pela rede.
    energia_nao_retirada_rede = (
        consumo_efetivo_total - rede_total
    )

    percentual_atendido_sem_rede = (
        energia_nao_retirada_rede /
        consumo_efetivo_total
    ) * 100

    percentual_reducao_demanda = (
        reducao_total /
        consumo_original_total
    ) * 100

    analise = []

    # ========================================================
    # APROVEITAMENTO ENERGÉTICO
    # ========================================================

    if percentual_atendido_sem_rede >= 70:

        analise.append(
            "A maior parte da demanda efetiva foi "
            "atendida sem utilização direta da rede elétrica."
        )

    elif percentual_atendido_sem_rede >= 40:

        analise.append(
            "Uma parcela relevante da demanda efetiva "
            "foi atendida por fontes alternativas à rede."
        )

    else:

        analise.append(
            "A simulação apresenta dependência significativa "
            "da rede elétrica para complementar a demanda."
        )

    # ========================================================
    # ENERGIA SOLAR
    # ========================================================

    if solar_total > 0:

        analise.append(
            "A geração solar contribui para o atendimento "
            "da demanda e pode fornecer excedente para "
            "armazenamento na bateria."
        )

    # ========================================================
    # BATERIA
    # ========================================================

    if bateria_total > 0:

        analise.append(
            "A bateria complementa a energia solar nos "
            "períodos em que a geração não é suficiente."
        )

    # ========================================================
    # REDUÇÃO DE DEMANDA
    # ========================================================

    if reducao_total > 0:

        analise.append(
            f"O gerenciamento de demanda reduziu "
            f"{reducao_total:.2f} kWh do consumo original "
            f"durante os horários de pico, correspondendo "
            f"a {percentual_reducao_demanda:.2f}%."
        )

    # ========================================================
    # ESTRATÉGIA DO SISTEMA
    # ========================================================

    analise.append(
        "A gestão do sistema segue uma estratégia baseada "
        "em regras: energia solar, bateria e, por último, "
        "rede elétrica."
    )

    return (
        analise,
        consumo_original_total,
        consumo_efetivo_total,
        rede_total,
        solar_total,
        bateria_total,
        reducao_total,
        percentual_atendido_sem_rede,
        percentual_reducao_demanda
    )


# ============================================================
# CRIAÇÃO DA PÁGINA HTML
# ============================================================

def pagina(bateria_inicial, capacidade_bateria):

    (
        energia_rede,
        energia_solar_usada,
        energia_bateria_usada,
        energia_reduzida,
        consumo_efetivo,
        acoes_sistema,
        nivel_bateria
    ) = simular(
        bateria_inicial,
        capacidade_bateria
    )

    dados = criar_dataframe(
        energia_rede,
        energia_solar_usada,
        energia_bateria_usada,
        energia_reduzida,
        consumo_efetivo,
        acoes_sistema,
        nivel_bateria
    )

    (
        analise,
        consumo_original_total,
        consumo_efetivo_total,
        rede_total,
        solar_total,
        bateria_total,
        reducao_total,
        percentual_atendido_sem_rede,
        percentual_reducao_demanda
    ) = analisar(dados)

    grafico_base64 = gerar_grafico(dados)

    # ========================================================
    # CRIA LINHAS DA TABELA
    # ========================================================

    linhas = ""

    for _, linha in dados.iterrows():

        linhas += f"""
        <tr>

            <td>
                {int(linha["Horário"])}:00
            </td>

            <td>
                {linha["Consumo Original"]:.2f} kWh
            </td>

            <td>
                {linha["Consumo Efetivo"]:.2f} kWh
            </td>

            <td>
                {linha["Geração Solar"]:.2f} kWh
            </td>

            <td>
                {linha["Solar Utilizada"]:.2f} kWh
            </td>

            <td>
                {linha["Bateria Utilizada"]:.2f} kWh
            </td>

            <td>
                {linha["Rede Utilizada"]:.2f} kWh
            </td>

            <td>
                {linha["Demanda Reduzida"]:.2f} kWh
            </td>

            <td>
                {linha["Nível da Bateria"]:.2f} kWh
            </td>

            <td>
                {linha["Ação do Sistema"]}
            </td>

        </tr>
        """

    # ========================================================
    # ANÁLISE EM HTML
    # ========================================================

    analise_html = ""

    for item in analise:

        analise_html += (
            "<li>" + item + "</li>"
        )

    # ========================================================
    # HTML
    # ========================================================

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>EcoCharge</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    font-family: Arial, sans-serif;

    margin: 0;

    background: #f4f7f5;

    color: #222;

}}

header {{

    background: #075c36;

    color: white;

    padding: 25px 40px;

}}

header h1 {{

    margin: 0;

    font-size: 32px;

}}

header p {{

    margin-top: 5px;

    margin-bottom: 0;

}}

.container {{

    width: 95%;

    max-width: 1500px;

    margin: 25px auto;

}}

.card {{

    background: white;

    padding: 20px;

    margin-bottom: 20px;

    border-radius: 10px;

    box-shadow: 0 2px 8px #ccc;

}}

form {{

    display: flex;

    align-items: center;

    gap: 20px;

    flex-wrap: wrap;

}}

.form-group {{

    display: flex;

    flex-direction: column;

}}

label {{

    margin-bottom: 6px;

    font-weight: bold;

}}

input {{

    padding: 10px;

    width: 200px;

    border: 1px solid #ccc;

    border-radius: 5px;

}}

button {{

    padding: 11px 30px;

    background: #079447;

    color: white;

    border: none;

    border-radius: 5px;

    cursor: pointer;

    font-size: 16px;

}}

button:hover {{

    background: #067a3c;

}}

.grid {{

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 15px;

    margin-bottom: 20px;

}}

.box {{

    background: white;

    padding: 20px;

    border-radius: 10px;

    text-align: center;

    box-shadow: 0 2px 8px #ccc;

}}

.box h3 {{

    margin-top: 0;

    color: #075c36;

}}

.numero {{

    font-size: 27px;

    font-weight: bold;

}}

.economia {{

    background:
        linear-gradient(
            90deg,
            #e5f8ec,
            #ffffff
        );

    border-left:
        6px solid #079447;

}}

.economia-numero {{

    font-size: 40px;

    color: #079447;

    font-weight: bold;

}}

.grafico {{

    width: 100%;

    max-width: 1200px;

    display: block;

    margin: 20px auto;

}}

.tabela-container {{

    overflow-x: auto;

}}

table {{

    width: 100%;

    border-collapse: collapse;

}}

th,
td {{

    border: 1px solid #ddd;

    padding: 10px;

    text-align: center;

}}

th {{

    background: #075c36;

    color: white;

}}

tr:nth-child(even) {{

    background: #f3f7f4;

}}

tr:hover {{

    background: #e7f5eb;

}}

.analise li {{

    margin-bottom: 12px;

    line-height: 1.5;

}}

footer {{

    background: #075c36;

    color: white;

    text-align: center;

    padding: 15px;

    margin-top: 30px;

}}

@media(max-width: 900px) {{

    .grid {{

        grid-template-columns:
            repeat(2, 1fr);

    }}

}}

@media(max-width: 600px) {{

    .grid {{

        grid-template-columns:
            1fr;

    }}

}}

</style>

</head>

<body>


<header>

<h1>EcoCharge</h1>

<p>
Protótipo de gestão inteligente de energia
para eletropostos
</p>

</header>


<div class="container">


<div class="card">

<h2>Parâmetros da Simulação</h2>

<form method="get">

<div class="form-group">

<label>
Nível inicial da bateria (kWh)
</label>

<input
    name="bateria"
    type="number"
    min="0"
    step="0.1"
    value="{bateria_inicial}"
>

</div>


<div class="form-group">

<label>
Capacidade da bateria (kWh)
</label>

<input
    name="capacidade"
    type="number"
    min="1"
    step="0.1"
    value="{capacidade_bateria}"
>

</div>


<div class="form-group">

<label>&nbsp;</label>

<button type="submit">
Simular
</button>

</div>

</form>

</div>


<div class="grid">


<div class="box">

<h3>Consumo Original</h3>

<div class="numero">
{consumo_original_total:.2f} kWh
</div>

</div>


<div class="box">

<h3>Consumo Efetivo</h3>

<div class="numero">
{consumo_efetivo_total:.2f} kWh
</div>

</div>


<div class="box">

<h3>Energia Solar</h3>

<div class="numero">
{solar_total:.2f} kWh
</div>

</div>


<div class="box">

<h3>Energia da Rede</h3>

<div class="numero">
{rede_total:.2f} kWh
</div>

</div>


</div>


<div class="card economia">

<h2>
Atendimento sem uso da rede
</h2>

<div class="economia-numero">

{percentual_atendido_sem_rede:.2f}%

</div>

<p>

Percentual do consumo efetivo atendido por
energia solar e bateria, sem utilização direta
da rede elétrica.

</p>

</div>


<div class="card">

<h2>
Redução de Demanda
</h2>

<div class="economia-numero">

{percentual_reducao_demanda:.2f}%

</div>

<p>

Percentual do consumo original que foi reduzido
durante os horários de pico por meio do
gerenciamento de demanda.

</p>

</div>


<div class="card">

<h2>
Desempenho Energético por Horário
</h2>

<p>

Gráfico gerado com Python utilizando
Pandas para organização dos dados e
Matplotlib para visualização.

</p>

<img
    class="grafico"
    src="data:image/png;base64,{grafico_base64}"
    alt="Gráfico de desempenho energético"
>

</div>


<div class="card analise">

<h2>
Análise da Gestão Inteligente
</h2>

<ul>

{analise_html}

</ul>

</div>


<div class="card">

<h2>
Dados da Simulação por Horário
</h2>

<div class="tabela-container">

<table>

<tr>

<th>Horário</th>

<th>Consumo Original</th>

<th>Consumo Efetivo</th>

<th>Geração Solar</th>

<th>Solar Utilizada</th>

<th>Bateria Utilizada</th>

<th>Rede Utilizada</th>

<th>Demanda Reduzida</th>

<th>Nível da Bateria</th>

<th>Ação do Sistema</th>

</tr>

{linhas}

</table>

</div>

</div>


</div>


<footer>

EcoCharge |
Gestão Inteligente de Energia |
Python + Pandas + Matplotlib

</footer>


</body>

</html>
"""


# ============================================================
# SERVIDOR LOCAL
# ============================================================

class Servidor(BaseHTTPRequestHandler):

    def do_GET(self):

        query = parse_qs(
            urlparse(self.path).query
        )

        try:

            bateria_inicial = float(
                query.get(
                    "bateria",
                    [50]
                )[0]
            )

            capacidade_bateria = float(
                query.get(
                    "capacidade",
                    [100]
                )[0]
            )

        except ValueError:

            bateria_inicial = 50

            capacidade_bateria = 100


        # ====================================================
        # VALIDAÇÃO DOS VALORES
        # ====================================================

        if capacidade_bateria <= 0:

            capacidade_bateria = 100


        if bateria_inicial < 0:

            bateria_inicial = 0


        if bateria_inicial > capacidade_bateria:

            bateria_inicial = capacidade_bateria


        # ====================================================
        # GERAÇÃO DA PÁGINA
        # ====================================================

        html = pagina(
            bateria_inicial,
            capacidade_bateria
        )


        self.send_response(200)

        self.send_header(
            "Content-type",
            "text/html; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(
            html.encode("utf-8")
        )


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    servidor = HTTPServer(
        ("localhost", 8000),
        Servidor
    )

    print(
        "========================================"
    )

    print(
        "EcoCharge iniciado."
    )

    print(
        "Abra no navegador:"
    )

    print(
        "http://localhost:8000"
    )

    print(
        "========================================"
    )

    servidor.serve_forever()