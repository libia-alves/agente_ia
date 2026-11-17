# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Aplicação: o formulário que põe o agente na frente do servidor
# Seção 6 – O agente atrás de um formulário
# Requisitos: pip install streamlit agno openai python-dotenv pydantic
# Execução: streamlit run app_revisor.py
# ============================================================
"""Formulário de revisão de minutas de resposta ao cidadão.

Esta aplicação não sabe qual framework está atrás dela. Ela importa a função
`revisar` do `revisor.py`, recebe um objeto `Revisao` validado e desenha os
campos. Trocar o Agno por LangChain ou CrewAI significa reescrever o
`revisor.py` e não tocar em nenhuma linha deste arquivo.

A interface de conversa da Aula 13 do módulo anterior não serve aqui: o
servidor não quer dialogar, quer a minuta de volta. O padrão é o formulário —
um envio, uma devolução, e o resultado em campo editável.
"""
import streamlit as st

from revisor import MANUAL, MANUAL_CONFIG, construir_agente, revisar
from configuracao import MENSAGEM_PADRAO

ROTULOS = {
    "consultar_manual_redacao": "Consultando o manual de redação oficial",
    "verificar_dados_pessoais": "Verificando dados pessoais no texto",
    "medir_legibilidade": "Medindo o tamanho das frases",
}

EXEMPLO = ("Prezado, em sede de análise exordial do pleito formulado por Vossa Senhoria, "
           "protocolo 2026001234, cumpre informar que o requerimento encontra-se em fase "
           "de instrução processual, restando pendente a juntada de documentação "
           "complementar a ser oportunamente especificada pelo setor competente.")

st.set_page_config(page_title="Revisor de minutas", page_icon="📝", layout="wide")


@st.cache_resource
def agente_em_cache():
    """Mantém um único agente para todas as interações.

    Sem o cache, cada reexecução do script construiria um agente novo, e o
    Streamlit reexecuta o script a cada interação do usuário. O agente não
    guarda histórico, e por isso pode ser compartilhado entre execuções.
    """
    return construir_agente()


st.title("Revisão de minuta de resposta ao cidadão")
st.info("Laboratório de TI da SEFAZ-MT — manual hipotético. Use minutas anonimizadas.")
st.caption("A revisão é uma sugestão de redação. O texto só sai do setor depois "
           "da conferência de quem assina.")

with st.form("formulario_minuta"):
    coluna_texto, coluna_opcoes = st.columns([3, 1])
    with coluna_texto:
        minuta = st.text_area(
            "Minuta redigida pelo servidor",
            height=200,
            placeholder=EXEMPLO,
            help="Cole o texto como ele está. O agente corrige a forma, não o mérito.",
        )
    with coluna_opcoes:
        tipo = st.selectbox("Tipo de documento", list(MANUAL))
        st.markdown("&nbsp;", unsafe_allow_html=True)
        enviado = st.form_submit_button("Revisar", type="primary", use_container_width=True)

if enviado and minuta.strip():
    # O `st.status` é o lugar onde o progresso aparece. Cada ferramenta
    # anunciada é uma linha nova, e é isso que ocupa os segundos em que a
    # resposta ainda não existe.
    with st.status("Revisando a minuta", expanded=True) as status:
        try:
            revisao, medidas = revisar(
                minuta, tipo, agente=agente_em_cache(),
                ao_chamar_ferramenta=lambda nome: st.write(ROTULOS.get(nome, nome)),
            )
        except Exception:
            st.session_state.pop("revisao", None)
            status.update(label=MENSAGEM_PADRAO, state="error")
            st.stop()
        status.update(label=f"Revisão concluída em {medidas['segundos']} s", state="complete")
    st.session_state["revisao"] = (minuta, revisao, medidas)
elif enviado:
    st.error("Cole a minuta antes de pedir a revisão.")

if "revisao" in st.session_state:
    original, revisao, medidas = st.session_state["revisao"]

    coluna_antes, coluna_depois = st.columns(2)
    with coluna_antes:
        st.subheader("Como foi escrito")
        st.text_area("Original", value=original, height=280, disabled=True,
                     label_visibility="collapsed")
    with coluna_depois:
        st.subheader("Sugestão do agente")
        # Campo editável de propósito: a conferência humana obrigatória de que
        # a Aula 01 fala acontece aqui, e não em um relatório posterior.
        aprovado = st.text_area("Texto para conferência e ajuste",
                                value=revisao.texto_revisado, height=280,
                                label_visibility="collapsed")

    if revisao.avisos:
        st.warning("**Decisões que o agente não tomou**\n\n"
                   + "\n".join(f"- {aviso}" for aviso in revisao.avisos))

    if revisao.alteracoes:
        st.subheader(f"O que mudou ({len(revisao.alteracoes)} alterações)")
        st.dataframe(
            [{"Como estava": a.trecho_original,
              "Como ficou": a.trecho_novo,
              "Motivo": a.motivo} for a in revisao.alteracoes],
            hide_index=True,
        )

    st.download_button("Baixar registro da revisão", revisao.model_dump_json(indent=2),
                       file_name="revisao.json", mime="application/json")
    st.download_button("Baixar o texto conferido", aprovado,
                       file_name="resposta-ao-cidadao.txt")

    st.caption(
        f"{medidas['chamadas']} chamadas ao modelo · "
        f"{len(medidas['ferramentas'])} ferramentas · "
        f"{medidas['tokens_entrada']} tokens de entrada · "
        f"{medidas['tokens_saida']} de saída · "
        f"Custo US$: {medidas['custo'] if medidas['custo'] is not None else 'não configurado'} · {medidas['segundos']} s"
    )
