import service, teclados

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