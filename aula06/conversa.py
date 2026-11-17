"""Conversa com Sofia no Colab ou terminal, preservando histórico por sessão."""
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ferramentas import NOME_AGENTE
from desafio_frameworks import criar_agente_langchain, _campo, _extrair_mensagens, _gravar

MENSAGEM_FALHA = 'Não consegui concluir a consulta agora. Tente novamente em instantes.'


class Conversa:
    def __init__(self, modelo: str = 'gpt-4o-mini', nome: str = NOME_AGENTE, *, agente=None):
        self.nome = nome.strip()
        if not self.nome:
            raise ValueError('Escolha um nome para o assistente.')
        self.modelo = modelo
        self._agente = agente if agente is not None else criar_agente_langchain(modelo, self.nome)
        self._mensagens = []
        self.turnos = []
        self.ultimas_fontes = []
        self.ultimo_arquivo = None

    def perguntar(self, texto: str) -> str:
        """Envia uma pergunta com o histórico; registra somente ferramentas deste turno."""
        if not texto.strip():
            return 'Digite sua pergunta sobre o atendimento de TI.'
        anteriores = len(self._mensagens)
        pedido = [*self._mensagens, {'role': 'user', 'content': texto.strip()}]
        try:
            resultado = self._agente.invoke({'messages': pedido}, config={'recursion_limit': 16})
            mensagens = resultado['messages']
            if not mensagens or (_campo(mensagens[-1], 'type') or _campo(mensagens[-1], 'role')) not in ('ai', 'assistant'):
                raise ValueError('Resposta final ausente.')
            conteudo = _campo(mensagens[-1], 'content')
            if isinstance(conteudo, list):
                conteudo = '\n'.join(b.get('text', '') for b in conteudo if isinstance(b, dict) and b.get('type') == 'text')
            if not isinstance(conteudo, str) or not conteudo.strip():
                raise ValueError('Resposta final vazia.')
            fontes = _extrair_mensagens(mensagens[anteriores:])
        except Exception as erro:
            self.ultimas_fontes = []
            self.turnos.append({'pergunta': texto.strip(), 'status': 'erro',
                                'tipo_erro': type(erro).__name__, 'resposta': MENSAGEM_FALHA, 'ferramentas': []})
            return MENSAGEM_FALHA
        self._mensagens = list(mensagens)
        self.ultimas_fontes = fontes
        self.turnos.append({'pergunta': texto.strip(), 'status': 'concluido',
                            'resposta': conteudo, 'ferramentas': fontes})
        return conteudo

    def limpar(self):
        """Inicia uma nova conversa, apagando histórico e registros em memória."""
        self._mensagens = []
        self.turnos = []
        self.ultimas_fontes = []
        self.ultimo_arquivo = None

    def salvar(self, pasta: str | Path = 'conversas') -> Path:
        """Exporta perguntas, respostas e ferramentas em JSON; não inclui credenciais."""
        data = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        caminho = Path(pasta) / f'conversa_{data}_{uuid4().hex[:6]}.json'
        _gravar(caminho, {'agente': self.nome, 'modelo': self.modelo, 'dados': 'laboratório; use apenas entradas fictícias ou anonimizadas',
                          'turnos': self.turnos})
        self.ultimo_arquivo = caminho
        return caminho


def conversar(conversa: Conversa, pasta: str | Path = 'conversas'):
    """Abre o diálogo por input(), compatível com uma célula do Google Colab."""
    print(f'{conversa.nome}: Olá! Posso ajudar com chamados, acesso, rede, arquivos e segurança de TI da SEFAZ-MT.')
    print('Usamos dados fictícios. Comandos: /fontes, /salvar, /limpar e /sair.')
    while True:
        try:
            texto = input('Você: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nConversa encerrada.')
            break
        comando = texto.lower()
        if comando in ('/sair', 'sair'):
            print(f'{conversa.nome}: Até a próxima!')
            break
        if comando == '/limpar':
            conversa.limpar()
            print(f'{conversa.nome}: Nova conversa iniciada.')
        elif comando == '/salvar':
            print('Conversa salva em:', conversa.salvar(pasta))
        elif comando == '/fontes':
            if not conversa.ultimas_fontes:
                print('Nenhuma consulta de ferramenta registrada na última resposta.')
            for fonte in conversa.ultimas_fontes:
                print(fonte['nome'], fonte['argumentos'], '→', fonte['retorno'])
        elif texto:
            print(f'{conversa.nome}: {conversa.perguntar(texto)}')


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).with_name('.env'))
    conversar(Conversa(modelo=os.getenv('MINILAB_MODELO') or 'gpt-4o-mini'))
