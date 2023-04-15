from diveni import service, teclados

SESSAO = {}

class BancoSessao:
    def __init__(self, sessao):
        self._sessao = sessao
        self._jogador = 0

    def avancar(self):
        """
        partidas = [ P1, P2, P3]
        posição 2 == len(partidas) - 1 -> limite superior
        """
        if self.posicao_atual() == len(self.palpites()) - 1:
            nova_posicao = 0
        else:
            nova_posicao = self.posicao_atual() + 1
        self._sessao.get(self._jogador)['posicao'] = nova_posicao

    def retroceder(self):
        """
        partidas = [ P1, P2, P3]
        posição 0 -> limite inferior
        nova_posicao = len(partidas) - 1
        """
        nova_posicao = None
        if self.posicao_atual() == 0:
            nova_posicao = len(self.palpites()) - 1
        else:
            nova_posicao = self.posicao_atual() - 1
        self._sessao.get(self._jogador)['posicao'] = nova_posicao


    def informar_jogador(self, id):
        if id not in self._sessao:
            self._sessao[id] = {
                'palpites': [],
                'posicao': 0
            }
        self._jogador = id

    def posicao_atual(self):
        return self._sessao.get(self._jogador).get('posicao')

    def palpites(self):
        return self._sessao.get(self._jogador).get('palpites')

    def partida(self):
        return self.palpites()[self.posicao_atual()][0]

    def palpite(self):
        return self.palpites()[self.posicao_atual()][1]

    def informar_reserva_palpites(self, partidas_palpites):
        if not self.palpites():
            self._sessao[self._jogador]['palpites'] = partidas_palpites


def rodada_com_palpites(partidas_palpites):
    textos = []
    for partida, palpite in partidas_palpites:
        if palpite and palpite.resultado != 'S':
            mandante = (
                f'[{partida.mandante.nome}]'
                if (palpite.resultado == 'M')
                else f'{partida.mandante.nome}'
            )
            empate = '[X]' if (palpite.resultado == 'E') else 'X'
            visitante = (
                f'[{partida.visitante.nome}]'
                if (palpite.resultado == 'V')
                else f'{partida.visitante.nome}'
            )
            textos.append(f'{mandante} {empate} {visitante}')
        else:
            textos.append(
                f'{partida.mandante.nome} x {partida.visitante.nome}'
            )
    return textos


def salvar_palpite_e_montar_resposta(palpite_id, resultado):
    # pesquiso no banco
    palpite = service.pegar_palpite_por_id(palpite_id)
    texto_extra = ''
    if palpite.resultado == resultado:
        texto_extra = '\n\nO palpite não foi alterado.'
    # mudo o resultado
    palpite.resultado = resultado
    # salvo no banco a mudança
    palpite.save()
    # seleciono o teclado de fazer palpites
    grupo = palpite.apostador.grupo
    resposta = teclados.teclado_de_fazer_palpites(grupo, palpite)
    # mando o texto com a mudança do palpite escolhido
    jogador = palpite.apostador
    rodada = palpite.partida.rodada
    partidas_palpites = service.procurar_palpites(jogador, rodada)
    textos = rodada_com_palpites([partidas_palpites[0]])
    texto = f'**Dar Palpite na Rodada {rodada.nome}\n\n**' + '\n'.join(textos) + texto_extra
    return resposta, texto