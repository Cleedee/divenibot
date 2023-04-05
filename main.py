from pyrogram import Client, filters, enums
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import dotenv_values

import service
import teclados
import utils

config = dotenv_values('.env')

print('Iniciando...')

usuarios = {
    'Cleedee': 1,
}

app = Client(
    'DiveniBot',
    api_id=config['API_ID'],
    api_hash=config['API_HASH'],
    bot_token=config['TOKEN_API'],
)


def resposta_para_grupos(callback_query):
    username = callback_query.from_user.username
    usuario_id = usuarios[username]
    ids_grupos = service.procurar_ids_grupos_por_usuario(usuario_id)
    grupos = service.procurar_grupos_por_ids(ids_grupos)
    return teclados.teclado_de_grupos(grupos)


def resposta_para_grupo(callback_query):
    grupo_id = int(callback_query.data.replace('grupo_', ''))
    grupo = service.pegar_grupo_por_id(grupo_id)
    resposta = teclados.teclado_do_grupo(grupo)
    return resposta, grupo


def resposta_para_pontuacao(callback_query):
    grupo_id = int(callback_query.data.replace('pontuacao_', ''))
    grupo = service.pegar_grupo_por_id(grupo_id)
    # procurar jogadores ativos do grupo
    jogadores = service.procurar_jogadores_ativos_por_grupo(grupo_id)
    texto_jogadores = '\n'.join(
        ['{} {}'.format(j.nome, j.pontos) for j in jogadores]
    )
    texto = '**Pontuação dos Jogadores do Grupo**\n\n' + texto_jogadores
    resposta = teclados.teclado_do_grupo(grupo)
    return resposta, texto


def resposta_para_rodada_atual(callback_query):
    grupo_id = int(callback_query.data.replace('rodada_atual_', ''))
    grupo = service.pegar_grupo_por_id(grupo_id)
    rodada_atual = service.pegar_rodada_por_id(grupo.rodada_atual_id)
    resposta = teclados.teclado_da_rodada(grupo, rodada_atual)
    partidas = service.procurar_partidas_da_rodada(rodada_atual)

    textos = []
    for p in partidas:
        if p.resultado == 'E':
            textos.append(f'{p.mandante.nome} **X** {p.visitante.nome}')
        elif p.resultado == 'M':
            textos.append(f'**{p.mandante.nome}** X {p.visitante.nome}')
        elif p.resultado == 'V':
            textos.append(f'{p.mandante.nome} X **{p.visitante.nome}**')
        else:
            textos.append(f'{p.mandante.nome} X {p.visitante.nome}')

    texto = '**Partidas da Rodada {}**\n\n'.format(
        rodada_atual.nome
    ) + '\n'.join(textos)
    return resposta, texto


def resposta_para_ver_palpites(callback_query):
    """
    [Athletico-PR] x Goiás
    Fortaleza [x] Internacional
    América-MG [x] Fluminense
    """
    ids_separados = callback_query.data.replace('ver_palpites_', '')
    grupo_id, rodada_id = map(int, ids_separados.split('_'))
    username = callback_query.from_user.username
    usuario_id = usuarios[username]
    jogador = service.procurar_jogador(usuario_id, grupo_id)
    grupo = service.pegar_grupo_por_id(grupo_id)
    rodada = service.pegar_rodada_por_id(rodada_id)
    partidas_palpites = service.procurar_palpites(jogador, rodada)
    textos = utils.rodada_com_palpites(partidas_palpites)
    resposta = teclados.teclado_dos_palpites(grupo, partidas_palpites)
    texto = f'**Palpites da Rodada {rodada.nome}\n\n**' + '\n'.join(textos)
    return resposta, texto


def resposta_para_fazer_palpites(callback_query):
    ids_separados = callback_query.data.replace('fazer_palpites_', '')
    grupo_id, rodada_id = map(int, ids_separados.split('_'))
    username = callback_query.from_user.username
    usuario_id = usuarios[username]
    jogador = service.procurar_jogador(usuario_id, grupo_id)
    grupo = service.pegar_grupo_por_id(grupo_id)
    rodada = service.pegar_rodada_por_id(rodada_id)
    partidas_palpites = service.procurar_palpites(jogador, rodada)
    partida = partidas_palpites[0][0]
    palpite = partidas_palpites[0][1]
    resposta = teclados.teclado_de_fazer_palpites(grupo)
    textos = utils.rodada_com_palpites([partidas_palpites[0]])
    texto = f'**Dar Palpite na Rodada {rodada.nome}\n\n**' + '\n'.join(textos)    
    return resposta, texto


# entrar num grupo

# lista de jogadores

# keyboard
@app.on_message(filters.command('teclado'))
async def inicia_teclado(_, message):
    await message.reply(
        'Escolha algo!',
        reply_markup=InlineKeyboardMarkup(teclados.teclado_principal()),
    )


# resposta do teclado
@app.on_callback_query()
async def resposta_teclado(_, callback_query):
    if callback_query.data == 'grupos':
        resposta = resposta_para_grupos(callback_query)
        await callback_query.edit_message_text(
            'Meus Grupos', reply_markup=InlineKeyboardMarkup(resposta)
        )
    if callback_query.data == 'voltar':
        await callback_query.edit_message_text(
            'Escolha algo!',
            reply_markup=InlineKeyboardMarkup(teclados.teclado_principal()),
        )
    if 'grupo_' in callback_query.data:
        resposta, grupo = resposta_para_grupo(callback_query)
        await callback_query.edit_message_text(
            'Grupo {}'.format(grupo.nome),
            reply_markup=InlineKeyboardMarkup(resposta),
        )
    if 'pontuacao_' in callback_query.data:
        resposta, texto = resposta_para_pontuacao(callback_query)
        await callback_query.edit_message_text(
            texto, reply_markup=InlineKeyboardMarkup(resposta)
        )
    if 'rodada_atual_' in callback_query.data:
        resposta, texto = resposta_para_rodada_atual(callback_query)
        await callback_query.edit_message_text(
            texto, reply_markup=InlineKeyboardMarkup(resposta)
        )
    if 'ver_palpites_' in callback_query.data:
        resposta, texto = resposta_para_ver_palpites(callback_query)
        await callback_query.edit_message_text(
            texto, reply_markup=InlineKeyboardMarkup(resposta)
        )
    if 'fazer_palpites_' in callback_query.data:
        resposta, texto = resposta_para_fazer_palpites(callback_query)
        await callback_query.edit_message_text(
            texto, reply_markup=InlineKeyboardMarkup(resposta)
        )


app.run()
print('Encerrando...')
