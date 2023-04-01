from pyrogram import Client, filters, enums
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import dotenv_values

import service
import teclados

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
    resposta = teclados.teclado_do_grupo(grupo)
    rodada_atual = service.procurar_rodada_por_id(grupo.rodada_atual_id)
    partidas = service.procurar_partidas_da_rodada(rodada_atual)
    texto_partidas = '\n'.join(
        ['{} x {}'.format(p.mandante.nome, p.visitante.nome) for p in partidas]
    )
    texto = (
        '**Partidas da Rodada {}**\n\n'.format(rodada_atual.nome)
        + texto_partidas
    )
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


app.run()
print('Encerrando...')
