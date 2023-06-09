from pyrogram import Client, filters, enums
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import dotenv_values

from diveni import service
from diveni import teclados
from diveni import utils
from diveni.utils import SESSAO, BancoSessao

config = dotenv_values('.env')

usuarios = {
    'Cleedee': 1,
}

banco = BancoSessao(SESSAO)

# SESSAO = {
#     '1' : {
#         'palpites': [],
#         'posicao': 3
#     },
#     '5': {
#         'palpites': [],
#         'posicao': 0
#     }
# }


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
    [Athletico-PR] x Goias
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
    banco.informar_jogador(jogador.id)
    banco.informar_reserva_palpites(partidas_palpites)
    palpite = banco.palpite()
    resposta = teclados.teclado_de_fazer_palpites(grupo, palpite)
    textos = utils.rodada_com_palpites(
        [banco.palpites()[banco.posicao_atual()]]
    )
    texto = f'**Dar Palpite na Rodada {rodada.nome}\n\n**' + '\n'.join(textos)
    return resposta, texto


def resposta_para_escolher_mandante(callback_query):
    # obtenho do callback o id do palpite
    palpite_id = callback_query.data.replace('mandante_', '')
    resposta, texto = utils.salvar_palpite_e_montar_resposta(palpite_id, 'M')
    return resposta, texto


def resposta_para_escolher_visitante(callback_query):
    # obtenho do callback o id do palpite
    palpite_id = callback_query.data.replace('visitante_', '')
    resposta, texto = utils.salvar_palpite_e_montar_resposta(palpite_id, 'V')
    return resposta, texto


def resposta_para_escolher_empate(callback_query):
    # obtenho do callback o id do palpite
    palpite_id = callback_query.data.replace('empate_', '')
    resposta, texto = utils.salvar_palpite_e_montar_resposta(palpite_id, 'E')
    return resposta, texto


def resposta_para_posterior(callback_query):
    grupo_id = callback_query.data.replace('posterior_', '')
    username = callback_query.from_user.username
    usuario_id = usuarios[username]
    jogador = service.procurar_jogador(usuario_id, grupo_id)
    grupo = service.pegar_grupo_por_id(grupo_id)
    banco.informar_jogador(jogador.id)
    banco.avancar()
    resposta = teclados.teclado_de_fazer_palpites(grupo, banco.palpite())
    textos = utils.rodada_com_palpites(
        [banco.palpites()[banco.posicao_atual()]]
    )
    rodada = banco.palpite().partida.rodada
    texto = f'**Dar Palpite na Rodada {rodada.nome}\n\n**' + '\n'.join(textos)
    return resposta, texto

def resposta_para_anterior(callback_query):
    grupo_id = callback_query.data.replace('anterior_', '')
    username = callback_query.from_user.username
    usuario_id = usuarios[username]
    jogador = service.procurar_jogador(usuario_id, grupo_id)
    grupo = service.pegar_grupo_por_id(grupo_id)
    banco.informar_jogador(jogador.id)
    banco.retroceder()
    resposta = teclados.teclado_de_fazer_palpites(grupo, banco.palpite())
    textos = utils.rodada_com_palpites(
        [banco.palpites()[banco.posicao_atual()]]
    )
    rodada = banco.palpite().partida.rodada
    texto = f'**Dar Palpite na Rodada {rodada.nome}\n\n**' + '\n'.join(textos)
    return resposta, texto

def main():
    app = Client(
        'DiveniBot',
        api_id=config['API_ID'],
        api_hash=config['API_HASH'],
        bot_token=config['TOKEN_API'],
    )

    @app.on_message(filters.command('start'))
    async def start(_, message):
        await message.reply(
            'Bem vindo ao DiveniBot!',
            reply_markup=InlineKeyboardMarkup(teclados.teclado_principal()),
        )


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
        if 'mandante_' in callback_query.data:
            resposta, texto = resposta_para_escolher_mandante(callback_query)
            await callback_query.edit_message_text(
                texto, reply_markup=InlineKeyboardMarkup(resposta)
            )
        if 'visitante_' in callback_query.data:
            resposta, texto = resposta_para_escolher_visitante(callback_query)
            await callback_query.edit_message_text(
                texto, reply_markup=InlineKeyboardMarkup(resposta)
            )
        if 'empate_' in callback_query.data:
            resposta, texto = resposta_para_escolher_empate(callback_query)
            await callback_query.edit_message_text(
                texto, reply_markup=InlineKeyboardMarkup(resposta)
            )
        if 'posterior_' in callback_query.data:
            resposta, texto = resposta_para_posterior(callback_query)
            await callback_query.edit_message_text(
                texto, reply_markup=InlineKeyboardMarkup(resposta)
            )
        if 'anterior_' in callback_query.data:
            resposta, texto = resposta_para_anterior(callback_query)
            await callback_query.edit_message_text(
                texto, reply_markup=InlineKeyboardMarkup(resposta)
            )
    print('Iniciando...')
    app.run()
    print('Encerrando...')
