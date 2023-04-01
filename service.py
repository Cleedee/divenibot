from model import db, Torneio, Grupo, Jogador, Partida, Rodada


def procurar_torneios():
    return Torneio.all()


def procurar_grupos():
    return Grupo.all()


#        .where('grupo.ativo','=','1')\
def procurar_grupos_por_ids(ids):
    return (
        db.table('grupo')
        .join('torneio', 'grupo.torneio_id', '=', 'torneio.id')
        .where_in('grupo.id', ids)
        .select('grupo.id', 'grupo.nome', 'torneio.nome as nome_torneio')
        .get()
    )


def procurar_ids_grupos_por_usuario(usuario_id):
    return (
        db.table('jogador')
        .where('usuario_id', '=', usuario_id)
        .lists('grupo_id')
    )


def pegar_grupo_por_id(id):
    return Grupo.find(id)


def procurar_jogadores_ativos_por_grupo(grupo_id):
    return (
        Jogador.where('grupo_id', '=', grupo_id)
        .order_by('pontos', 'desc')
        .get()
    )


def procurar_rodada_por_id(id):
    return Rodada.find(id)


def procurar_rodadas_por_torneio(torneio):
    return Rodada.where('torneio_id', '=', torneio.id).get()


def procurar_partidas_da_rodada(rodada):
    return Partida.where('rodada_id', '=', rodada.id).get()
