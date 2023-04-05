

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