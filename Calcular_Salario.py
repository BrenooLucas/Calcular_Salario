# =============================================================================
# 1) IMPORTAÇÃO DE BIBLIOTECAS
# =============================================================================
import calendar
from typing import Tuple
import tkinter as tk
from tkinter import ttk, messagebox
import locale

# =============================================================================
# Configurações iniciais
# =============================================================================
# Formatação monetária para pt_BR (executada apenas uma vez).
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

# =============================================================================
# Constantes do sistema
# =============================================================================
COPYRIGHT = "© 2025-2026 Copyright | Todos os Direitos Reservados | GitHub: github.com/BrenooLucas"
SEPARATOR = "--------------------------------------------------------------------"

# =============================================================================
# Faixas e alíquotas do INSS (progressivo)
INSS_LIMITS = [1518.00, 2793.88, 4190.83, 8157.41]
INSS_RATES = [0.075, 0.09, 0.12, 0.14]
# =============================================================================

# Salário mínimo base para cálculo de insalubridade
SALARIO_MINIMO = 1518.00

# =============================================================================
# Utilitários de formatação e parsing
# =============================================================================
def formatar_valor(valor: float) -> str:
    """
    Formata um float para moeda brasileira (ex: '1.518,00').

    """
    try:
        return locale.currency(valor, symbol=False, grouping=True).strip()
    except Exception:
        # Fallback simples caso locale falhe
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def limpar_formato(valor: str) -> float:
    """
    Converte uma string no formato brasileiro (com '.' como separador de milhar
    e ',' como decimal) para float.
    Ex: '1.518,00' -> 1518.0
    """
    if not valor:
        return 0.0
    return float(valor.replace('.', '').replace(',', '.'))

# =============================================================================
# Cálculos financeiros
# =============================================================================
def calcular_inss(salario_bruto: float) -> float:
    if salario_bruto <= 0:
        return 0.0

    inss_total = 0.0
    lower = 0.0
    for i, upper in enumerate(INSS_LIMITS):
        rate = INSS_RATES[i]
        # Se o salário ultrapassa o topo da faixa, contribui sobre a faixa completa
        if salario_bruto > upper:
            inss_total += (upper - lower) * rate
            lower = upper
        else:
            # Contribuição parcial na faixa atual; término do cálculo
            inss_total += (salario_bruto - lower) * rate
            return inss_total

    # Se passou por todas as faixas, o loop já computou corretamente até o teto
    return inss_total

def calcular_insalubridade(percentual: float) -> Tuple[float, float, float]:
    """
    Calcula o valor total da insalubridade com base no salário mínimo e divide
    nas parcelas de 40% e 60%.
    """
    if percentual <= 0:
        return 0.0, 0.0, 0.0
    insal_total = SALARIO_MINIMO * (percentual / 100.0)
    parcela_40 = insal_total * 0.40
    parcela_60 = insal_total * 0.60
    return insal_total, parcela_40, parcela_60

def calcular_vr(valor_vr: float, dias_vr: int, percentual_desconto: float) -> float:
    if percentual_desconto > 0 and valor_vr > 0 and dias_vr > 0:
        return (valor_vr * dias_vr) * (percentual_desconto / 100.0)
    return 0.0

def calcular_vt(salario_bruto: float, percentual_desconto: float) -> float:
    """
    Calcula descontos proporcionais ao salário (VT, saúde, odontológico).
    """
    if percentual_desconto > 0 and salario_bruto > 0:
        return salario_bruto * (percentual_desconto / 100.0)
    return 0.0

# =============================================================================
# Composição da string de resultados
# =============================================================================
def get_resultados_string(
    salario_bruto: float,
    adiantamento_salario: float,
    insalubridade_percentual: float,
    valor_vr: float,
    dias_vr: int,
    desconto_vr_percentual: float,
    desconto_vt_percentual: float,
    desconto_saude_percentual: float,
    desconto_odonto_percentual: float,
) -> str:
    """
    Recebe todos os inputs numéricos (já convertidos) e retorna uma string
    formatada com os cálculos detalhados para exibição no Text widget.
    """
    # Descontos e adicionais
    desconto_inss = calcular_inss(salario_bruto)
    insal_total, parcela_40, parcela_60 = calcular_insalubridade(insalubridade_percentual)
    desconto_vr = calcular_vr(valor_vr, dias_vr, desconto_vr_percentual)
    desconto_vt = calcular_vt(salario_bruto, desconto_vt_percentual)
    desconto_saude = calcular_vt(salario_bruto, desconto_saude_percentual)
    desconto_odonto = calcular_vt(salario_bruto, desconto_odonto_percentual)

    # Adiantamentos
    adiantamento_40 = (adiantamento_salario / 100.0) * salario_bruto
    adiantamento_insalubridade_40 = parcela_40

    # Salário líquido (soma de proventos - descontos + insalubridade)
    salario_liquido = (
        salario_bruto
        - desconto_inss
        - desconto_vr
        - desconto_vt
        - desconto_saude
        - desconto_odonto
        + insal_total
    )

    linhas = []
    linhas.append(f"- Salário Bruto: R$ {formatar_valor(salario_bruto)}")
    linhas.append(f"\n- Valor Adiantamento Salário ({adiantamento_salario}%): R$ {formatar_valor(adiantamento_40)}")
    linhas.append(f"\n- Valor VR ({dias_vr} Dias): R$ {formatar_valor(valor_vr * dias_vr)}")
    linhas.append(f"\n- Valor Adiantamento Insalubridade: R$ {formatar_valor(adiantamento_insalubridade_40)} Reais. | Obs.: A empresa pode (ou não) arredondar.")
    linhas.append(f"\n- Valor Final Insalubridade: R$ {formatar_valor(parcela_60)}")
    linhas.append(f"\n- Valor Adiantamento Insalubridade (40%) + Valor Adiantamento Salário ({adiantamento_salario}%): R$ {formatar_valor(adiantamento_40 + adiantamento_insalubridade_40)} Reais. | Obs.: A empresa pode (ou não) arredondar.")
    linhas.append(SEPARATOR)

    percentual_inss = (desconto_inss / salario_bruto * 100.0) if salario_bruto > 0 else 0.0
    linhas.append(f"\n- Valor Desconto INSS ({percentual_inss:.2f}%): R$ {formatar_valor(desconto_inss)}")

    if desconto_vr_percentual > 0:
        linhas.append(f"\n- Valor Desconto VR ({desconto_vr_percentual}%): R$ {formatar_valor(desconto_vr)}")
    else:
        linhas.append("\n- Sem desconto de VR.")

    if desconto_vt_percentual > 0:
        linhas.append(f"\n- Valor Desconto VT ({desconto_vt_percentual}%): R$ {formatar_valor(desconto_vt)}")
    else:
        linhas.append("\n- Sem desconto de VT.")

    if desconto_saude_percentual > 0:
        linhas.append(f"\n- Valor Desconto Plano de Saúde ({desconto_saude_percentual}%): R$ {formatar_valor(desconto_saude)}")
    else:
        linhas.append("\n- Sem desconto de Plano de Saúde.")

    if desconto_odonto_percentual > 0:
        linhas.append(f"\n- Valor Desconto Plano Odontológico ({desconto_odonto_percentual}%): R$ {formatar_valor(desconto_odonto)}")
    else:
        linhas.append("\n- Sem desconto de Plano Odontológico.")

    total_descontos = desconto_inss + desconto_vr + desconto_vt + desconto_saude + desconto_odonto
    linhas.append(f"\n- Valor Total Desconto (INSS + VR + VT + Saúde + Odontológico): R$ {formatar_valor(total_descontos)}")
    linhas.append(SEPARATOR)
    linhas.append(f"\n- Total de Proventos: R$ {formatar_valor(salario_bruto + insal_total)} Reais. | Obs.: A empresa pode (ou não) arredondar.")
    linhas.append(f"\n- Total Insalubridade: R$ {formatar_valor(insal_total)} Reais. | Obs.: A empresa pode (ou não) arredondar.")
    linhas.append(SEPARATOR)
    linhas.append(f"\n- Salário Líquido: R$ {formatar_valor(salario_liquido)} Reais. | Obs.: A empresa pode (ou não) arredondar.")
    linhas.append(SEPARATOR)

    return "\n".join(linhas)

# =============================================================================
# Validações utilitárias
# =============================================================================
def verificar_dias_validos(ano: int, mes: int, dias_trab_mes: int) -> bool:
    """
    Verifica se a quantidade de dias informada é válida para o mês/ano (considera bissextos).
    Retorna True se válido; False caso contrário.
    """
    if mes < 1 or mes > 12:
        return False
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    return 0 <= dias_trab_mes <= dias_no_mes

# =============================================================================
# Interface Gráfica (GUI)
# =============================================================================
def gui_main():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal enquanto carrega

    # Cria a tela de splash (loading)
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)  # Remove a barra de título para um visual mais clean
    splash.geometry("300x100")
    splash.configure(bg='#606060')

    # Centraliza a splash na tela
    splash.update_idletasks()
    width = splash.winfo_width()
    height = splash.winfo_height()
    x = (splash.winfo_screenwidth() // 2) - (width // 2)
    y = (splash.winfo_screenheight() // 2) - (height // 2)
    splash.geometry(f'{width}x{height}+{x}+{y}')

    label = tk.Label(splash, text="Carregando a aplicação...", bg='#606060', fg="#ffffff", font=("Roboto", 12, "bold"))
    label.pack(expand=True, pady=30)

    splash.update()  # Atualiza para exibir a splash imediatamente

    # Agora constrói a UI principal (pode demorar frações de segundos)
    root.title("Folha de Pagamento - Calculadora de Salário")
    root.geometry("1100x700")

    try:
        root.iconbitmap("salario.ico")
    except Exception:
        # Não interrompe caso o ícone não exista
        pass
    root.configure(bg='#606060')
    root.resizable(True, True)

    # =============================================================================
    # Estilos
    # =============================================================================
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TLabel", font=("Roboto", 12), padding=5)
    style.configure("TEntry", font=("Roboto", 12), padding=5)
    style.configure("TButton", font=("Roboto", 12, "bold"), padding=10)
    style.configure("TCombobox", font=("Roboto", 12), padding=5)
    style.configure("Treeview",
                    background="#c0c0c0",
                    fieldbackground="#c0c0c0",
                    foreground="black")
    style.map("Treeview", background=[("selected", "#007bff")])

    # =============================================================================
    # Cabeçalho e estrutura principal
    # =============================================================================
    title_label = tk.Label(root, text="Calculadora de Salário - Folha de Pagamento",
                           bg='#606060', fg="#ffffff", font=("Roboto", 18, "bold"))
    title_label.pack(pady=20)

    main_frame = tk.Frame(root, bg='#606060')
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)
    # =============================================================================

    # Frame esquerdo: Inputs
    input_frame = tk.Frame(main_frame, bg="#909090", relief="ridge", borderwidth=2)
    input_frame.pack(side="left", fill="both", expand=True, padx=10)

    input_title = tk.Label(input_frame, text="Dados de Entrada", bg="#909090", fg="black",
                           font=("Roboto", 14, "bold"))
    input_title.pack(pady=10)

    # =============================================================================
    # Variáveis vinculadas aos widgets (preservei nomes para compatibilidade)
    # =============================================================================
    salario_bruto_var = tk.StringVar()
    adiantamento_var = tk.StringVar()
    ano_var = tk.StringVar()
    mes_var = tk.StringVar()
    dias_mes_var = tk.StringVar()
    insal_var = tk.StringVar()
    valor_vr_var = tk.StringVar()
    dias_vr_var = tk.StringVar()
    tem_desconto_vr_var = tk.StringVar(value="N")
    desconto_vr_perc_var = tk.StringVar()
    tem_desconto_vt_var = tk.StringVar(value="N")
    desconto_vt_perc_var = tk.StringVar()
    tem_desconto_saude_var = tk.StringVar(value="N")
    desconto_saude_perc_var = tk.StringVar()
    tem_desconto_odonto_var = tk.StringVar(value="N")
    desconto_odonto_perc_var = tk.StringVar()

    # =============================================================================
    # Validação simples para campos monetários e percentuais
    # =============================================================================
    def format_money_input(d, i, S, v, V, W):
        """
        Verifica se o conteúdo atual do widget pode ser convertido para float
        após limpar o formato brasileiro. Retorna True para permitir a mudança.
        """
        try:
            widget = root.nametowidget(W)
            current_value = widget.get()
            clean_value = current_value.replace('.', '').replace(',', '.')
            if clean_value:
                float(clean_value)
            return True
        except (ValueError, AttributeError):
            return False

    vcmd = root.register(format_money_input)

    def validate_digits(P):
        return P == "" or P.isdigit()

    vcmd_digits = root.register(validate_digits)

    # Função para validar percentuais no FocusOut
    def validate_percent(event, sv):
        value = sv.get()
        if value:
            try:
                clean_value = value.replace('.', '').replace(',', '.')
                percent = float(clean_value)
                if percent > 100:
                    messagebox.showerror("Erro - Porcentagem", "Esse valor é um valor cheio. Insira o percentual: Ex: 10")
                    sv.set("")
            except ValueError:
                pass

    # Função para formatação dinâmica de moeda ao digitar
    def on_key_release_monetary(event, var):
        text = var.get()
        digits = ''.join(c for c in text if c.isdigit())
        if not digits:
            return
        int_value = int(digits)
        formatted = formatar_valor(int_value / 100)
        var.set(formatted)
        event.widget.icursor(len(formatted))

    # =============================================================================
    # Frame - Informações Básicas (salário, adiantamento, data)
    # =============================================================================
    basic_frame = tk.LabelFrame(input_frame, text="Informações Básicas", bg="#909090", fg="black",
                                font=("Roboto", 12))
    basic_frame.pack(fill="x", padx=10, pady=5)

    labels_basic = ["Salário Bruto (R$):", "Adiant. Salário (Ex: 10%):", "Ano (ex: 2025):", "Mês (1-12):",
                    "Total de Dias no Mês:"]
    entries_basic = []

    for i, texto in enumerate(labels_basic):
        lbl = tk.Label(basic_frame, text=texto, bg="#909090", fg="black")
        lbl.grid(row=i, column=0, sticky="e", padx=10, pady=5)
        ent = tk.Entry(basic_frame, width=40, bg="#f0f0f0", fg="black")
        ent.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        entries_basic.append(ent)

    # Vinculação das StringVars aos Entry widgets
    entries_basic[0].config(textvariable=salario_bruto_var, validate="key",
                            validatecommand=(vcmd_digits, '%P'))
    entries_basic[1].config(textvariable=adiantamento_var, validate="all",
                            validatecommand=(vcmd, '%d', '%i', '%S', '%v', '%V', '%W'))
    entries_basic[2].config(textvariable=ano_var)
    entries_basic[3].config(textvariable=mes_var)
    entries_basic[4].config(textvariable=dias_mes_var)

    # Validação de percentual para adiantamento
    entries_basic[1].bind("<FocusOut>", lambda event: validate_percent(event, adiantamento_var))

    # Formatação dinâmica para salário bruto
    entries_basic[0].bind("<KeyRelease>", lambda event: on_key_release_monetary(event, salario_bruto_var))

    # =============================================================================
    # Frame - Benefícios e Insalubridade (VR e dias)
    # =============================================================================
    benefits_frame = tk.LabelFrame(input_frame, text="Benefícios", bg="#909090", fg="black",
                                   font=("Roboto", 12))
    benefits_frame.pack(fill="x", padx=10, pady=5)

    labels_benefits = ["Insalubridade (Ex: 10%):", "Valor VR por Dia (R$):", "Dias Úteis VR:"]
    entries_benefits = []

    for i, texto in enumerate(labels_benefits):
        lbl = tk.Label(benefits_frame, text=texto, bg="#909090", fg="black")
        lbl.grid(row=i, column=0, sticky="e", padx=10, pady=5)
        ent = tk.Entry(benefits_frame, width=40, bg="#f0f0f0", fg="black")
        ent.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        entries_benefits.append(ent)

    entries_benefits[0].config(textvariable=insal_var, validate="all",
                               validatecommand=(vcmd, '%d', '%i', '%S', '%v', '%V', '%W'))
    entries_benefits[1].config(textvariable=valor_vr_var, validate="key",
                               validatecommand=(vcmd_digits, '%P'))
    entries_benefits[2].config(textvariable=dias_vr_var)

    # Validação de percentual para insalubridade
    entries_benefits[0].bind("<FocusOut>", lambda event: validate_percent(event, insal_var))

    # Formatação dinâmica para valor VR
    entries_benefits[1].bind("<KeyRelease>", lambda event: on_key_release_monetary(event, valor_vr_var))

    # =============================================================================
    # Frame - Descontos (toggles + percentuais opcionais)
    # =============================================================================
    discounts_frame = tk.LabelFrame(input_frame, text="Descontos", bg="#909090", fg="black", font=("Roboto", 12))
    discounts_frame.pack(fill="x", padx=10, pady=5)

    # =============================================================================

    # VR toggle
    row_disc = 0
    lbl_vr = tk.Label(discounts_frame, text="Desconto VR/VA?", bg="#909090", fg="black")
    lbl_vr.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    cmb_vr = ttk.Combobox(discounts_frame, textvariable=tem_desconto_vr_var, values=["N", "S"], state="readonly")
    cmb_vr.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)

    row_disc += 1
    lbl_vr_perc = tk.Label(discounts_frame, text="Desconto VR (Ex: 10%):", bg="#909090", fg="black")
    ent_vr_perc = tk.Entry(discounts_frame, textvariable=desconto_vr_perc_var, width=23, bg="#f0f0f0", fg="black",
                           validate="all", validatecommand=(vcmd, '%d', '%i', '%S', '%v', '%V', '%W'))
    lbl_vr_perc.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    ent_vr_perc.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)
    lbl_vr_perc.grid_remove()
    ent_vr_perc.grid_remove()

    def toggle_vr(*args):
        if tem_desconto_vr_var.get() == "S":
            lbl_vr_perc.grid()
            ent_vr_perc.grid()
        else:
            lbl_vr_perc.grid_remove()
            ent_vr_perc.grid_remove()
            desconto_vr_perc_var.set("")

    tem_desconto_vr_var.trace("w", toggle_vr)

    # Validação de percentual para desconto VR
    ent_vr_perc.bind("<FocusOut>", lambda event: validate_percent(event, desconto_vr_perc_var))

    # VT toggle
    row_disc += 1
    lbl_vt = tk.Label(discounts_frame, text="Desconto VT?", bg="#909090", fg="black")
    lbl_vt.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    cmb_vt = ttk.Combobox(discounts_frame, textvariable=tem_desconto_vt_var, values=["N", "S"], state="readonly")
    cmb_vt.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)

    row_disc += 1
    lbl_vt_perc = tk.Label(discounts_frame, text="Desconto VT (Ex: 10%):", bg="#909090", fg="black")
    ent_vt_perc = tk.Entry(discounts_frame, textvariable=desconto_vt_perc_var, width=23, bg="#f0f0f0", fg="black",
                           validate="all", validatecommand=(vcmd, '%d', '%i', '%S', '%v', '%V', '%W'))
    lbl_vt_perc.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    ent_vt_perc.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)
    lbl_vt_perc.grid_remove()
    ent_vt_perc.grid_remove()

    def toggle_vt(*args):
        if tem_desconto_vt_var.get() == "S":
            lbl_vt_perc.grid()
            ent_vt_perc.grid()
        else:
            lbl_vt_perc.grid_remove()
            ent_vt_perc.grid_remove()
            desconto_vt_perc_var.set("")

    tem_desconto_vt_var.trace("w", toggle_vt)

    # Validação de percentual para desconto VT
    ent_vt_perc.bind("<FocusOut>", lambda event: validate_percent(event, desconto_vt_perc_var))

    # Saúde toggle
    row_disc += 1
    lbl_saude = tk.Label(discounts_frame, text="Desconto Plano de Saúde?", bg="#909090", fg="black")
    lbl_saude.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    cmb_saude = ttk.Combobox(discounts_frame, textvariable=tem_desconto_saude_var, values=["N", "S"], state="readonly")
    cmb_saude.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)

    row_disc += 1
    lbl_saude_perc = tk.Label(discounts_frame, text="Desconto Saúde (Ex: 10%):", bg="#909090", fg="black")
    ent_saude_perc = tk.Entry(discounts_frame, textvariable=desconto_saude_perc_var, width=23, bg="#f0f0f0", fg="black",
                              validate="all", validatecommand=(vcmd, '%d', '%i', '%S', '%v', '%V', '%W'))
    lbl_saude_perc.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    ent_saude_perc.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)
    lbl_saude_perc.grid_remove()
    ent_saude_perc.grid_remove()

    def toggle_saude(*args):
        if tem_desconto_saude_var.get() == "S":
            lbl_saude_perc.grid()
            ent_saude_perc.grid()
        else:
            lbl_saude_perc.grid_remove()
            ent_saude_perc.grid_remove()
            desconto_saude_perc_var.set("")

    tem_desconto_saude_var.trace("w", toggle_saude)

    # Validação de percentual para desconto saúde
    ent_saude_perc.bind("<FocusOut>", lambda event: validate_percent(event, desconto_saude_perc_var))

    # Odontológico toggle
    row_disc += 1
    lbl_odonto = tk.Label(discounts_frame, text="Desconto Plano Odontológico?", bg="#909090", fg="black")
    lbl_odonto.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    cmb_odonto = ttk.Combobox(discounts_frame, textvariable=tem_desconto_odonto_var, values=["N", "S"],
                              state="readonly")
    cmb_odonto.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)

    row_disc += 1
    lbl_odonto_perc = tk.Label(discounts_frame, text="Desconto Odonto (Ex: 10%):", bg="#909090", fg="black")
    ent_odonto_perc = tk.Entry(discounts_frame, textvariable=desconto_odonto_perc_var, width=23, bg="#f0f0f0",
                               fg="black", validate="all", validatecommand=(vcmd, '%d', '%i', '%S', '%v', '%V', '%W'))
    lbl_odonto_perc.grid(row=row_disc, column=0, sticky="e", padx=10, pady=5)
    ent_odonto_perc.grid(row=row_disc, column=1, sticky="w", padx=10, pady=5)
    lbl_odonto_perc.grid_remove()
    ent_odonto_perc.grid_remove()

    def toggle_odonto(*args):
        if tem_desconto_odonto_var.get() == "S":
            lbl_odonto_perc.grid()
            ent_odonto_perc.grid()
        else:
            lbl_odonto_perc.grid_remove()
            ent_odonto_perc.grid_remove()
            desconto_odonto_perc_var.set("")

    tem_desconto_odonto_var.trace("w", toggle_odonto)

    # Validação de percentual para desconto odonto
    ent_odonto_perc.bind("<FocusOut>", lambda event: validate_percent(event, desconto_odonto_perc_var))

    # =============================================================================
    # Botões de ação
    # =============================================================================
    buttons_frame = tk.Frame(input_frame, bg="#909090")
    buttons_frame.pack(pady=10)

    # Função principal de cálculo (mantive validações e mensagens)
    def calcular():
        # Verificar se todos os campos principais estão vazios
        required_vars = [salario_bruto_var, adiantamento_var, ano_var, mes_var, dias_mes_var, insal_var, valor_vr_var, dias_vr_var]
        if all(not var.get().strip() for var in required_vars):
            messagebox.showerror("Erro", "Por favor, preencha os campos.")
            return

        try:
            # Conversões e limpeza de inputs
            salario_bruto = limpar_formato(salario_bruto_var.get())
            adiantamento_salario = limpar_formato(adiantamento_var.get())
            ano = int(ano_var.get() or 0)
            mes = int(mes_var.get() or 0)
            dias_mes = int(dias_mes_var.get() or 0)
            insal_perc = limpar_formato(insal_var.get())
            valor_vr = limpar_formato(valor_vr_var.get())
            dias_vr = int(dias_vr_var.get() or 0)
            desconto_vr_perc = limpar_formato(desconto_vr_perc_var.get())
            desconto_vt_perc = limpar_formato(desconto_vt_perc_var.get())
            desconto_saude_perc = limpar_formato(desconto_saude_perc_var.get())
            desconto_odonto_perc = limpar_formato(desconto_odonto_perc_var.get())

            # Validações lógicas
            if ano < 1900 or ano > 2100:
                messagebox.showerror("Erro", "Ano inválido. Por favor, insira um ano entre 1900 e 2100.")
                return

            if not verificar_dias_validos(ano, mes, dias_mes):
                messagebox.showerror("Erro", "Número de dias inválido para o mês/ano.")
                return

            # Obter string formatada de resultados e exibir
            resultados = get_resultados_string(
                salario_bruto,
                adiantamento_salario,
                insal_perc,
                valor_vr,
                dias_vr,
                desconto_vr_perc,
                desconto_vt_perc,
                desconto_saude_perc,
                desconto_odonto_perc,
            )

            result_text.config(state="normal")
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, resultados)
            result_text.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    calc_button = tk.Button(buttons_frame, text="Calcular", bg="#007bff", fg="white",
                            activebackground="#0062cc", relief="flat", font=("Arial", 10, "bold"),
                            width=10, command=calcular)
    calc_button.pack(side="left", padx=5)
    calc_button.bind("<Enter>", lambda e: calc_button.config(bg="#0069d9"))
    calc_button.bind("<Leave>", lambda e: calc_button.config(bg="#007bff"))

    # Botão limpar campos
    def limpar_campos():
        salario_bruto_var.set("")
        adiantamento_var.set("")
        ano_var.set("")
        mes_var.set("")
        dias_mes_var.set("")
        insal_var.set("")
        valor_vr_var.set("")
        dias_vr_var.set("")
        tem_desconto_vr_var.set("N")
        desconto_vr_perc_var.set("")
        tem_desconto_vt_var.set("N")
        desconto_vt_perc_var.set("")
        tem_desconto_saude_var.set("N")
        desconto_saude_perc_var.set("")
        tem_desconto_odonto_var.set("N")
        desconto_odonto_perc_var.set("")

        # Limpa a área de resultados
        result_text.config(state="normal")
        result_text.delete("1.0", tk.END)
        result_text.config(state="disabled")

        # Atualiza visibilidade dos percentuais
        toggle_vr()
        toggle_vt()
        toggle_saude()
        toggle_odonto()

    limpar_button = tk.Button(buttons_frame, text="Limpar Campos", bg="#ffc107", fg="black",
                              activebackground="#e0a800", relief="flat", font=("Arial", 10, "bold"),
                              width=12, command=limpar_campos)
    limpar_button.pack(side="left", padx=5)
    limpar_button.bind("<Enter>", lambda e: limpar_button.config(bg="#ffca2c"))
    limpar_button.bind("<Leave>", lambda e: limpar_button.config(bg="#ffc107"))

    # Botão sair
    def sair():
        root.quit()

    sair_button = tk.Button(buttons_frame, text="Sair", bg="#FF0000", fg="white",
                            activebackground="#FF6347", relief="flat", font=("Arial", 10, "bold"),
                            width=10, command=sair)
    sair_button.pack(side="left", padx=5)
    sair_button.bind("<Enter>", lambda e: sair_button.config(bg="#FF6347"))
    sair_button.bind("<Leave>", lambda e: sair_button.config(bg="#FF0000"))

    # =============================================================================
    # Frame - Resultado (direita)
    # =============================================================================
    result_frame = tk.Frame(main_frame, bg="black", relief="ridge", borderwidth=2)
    result_frame.pack(side="right", fill="both", expand=True, padx=10)

    result_title = tk.Label(result_frame, text="Resultado do Cálculo", bg="black", fg="white",
                            font=("Roboto", 14, "bold"))
    result_title.pack(pady=10)

    scroll_y = tk.Scrollbar(result_frame, orient="vertical")
    scroll_y.pack(side="right", fill="y")

    result_text = tk.Text(result_frame, font=("Roboto", 12, "bold"), wrap=tk.WORD,
                          yscrollcommand=scroll_y.set, bg="black", fg="yellow", height=30)
    result_text.pack(fill="both", expand=True, padx=10, pady=10)
    result_text.config(state="disabled")
    scroll_y.config(command=result_text.yview)

    # Rodapé
    footer_label = tk.Label(root, text=COPYRIGHT, bg='#606060', fg="yellow", font=("Roboto", 11,"bold"))
    footer_label.pack(side="bottom", pady=10)

    # =============================================================================
    # Handler para desfocar/blur
    # =============================================================================
    def blur_handler(event):
        # Se o widget clicado não for Entry/Combobox, tenta retirar foco dos campos pra nao deixar o ponteiro piscando
        if not isinstance(event.widget, (tk.Entry, ttk.Combobox)):
            try:
                current = root.focus_get()
            except KeyError:
                current = None
            if current and isinstance(current, (tk.Entry, ttk.Combobox)):
                root.focus_set()

    root.bind_all("<Button-1>", blur_handler)

    # Após construir a UI, destrói a splash e exibe a janela principal
    splash.destroy()
    root.deiconify()  # Mostra a janela principal
    root.mainloop()

# =============================================================================
# Execução principal
# =============================================================================
if __name__ == "__main__":
    gui_main()