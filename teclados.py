from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def teclado_principal():
    return [
        [
            InlineKeyboardButton('Meus Grupos', callback_data='grupos'),
            InlineKeyboardButton('Convites', callback_data='convites'),
        ],
        [
            InlineKeyboardButton('Admin', callback_data='admin'),
            InlineKeyboardButton('Novo Grupo', callback_data='novo_grupo'),
        ],
    ]


def teclado_de_grupos(grupos):
    botoes = []
    for grupo in grupos:
        botao = InlineKeyboardButton(
            '{}'.format(grupo.nome),
            callback_data='grupo_{}'.format(str(grupo.id)),
        )
        botoes.append([botao])
    botoes.append([InlineKeyboardButton('Voltar', callback_data='voltar')])
    return botoes


def teclado_do_grupo(grupo):
    botoes = []
    botao_pontuacao = InlineKeyboardButton(
        'Pontuação', callback_data='pontuacao_{}'.format(str(grupo.id))
    )
    botao_rodada_atual = InlineKeyboardButton(
        'Rodada Atual', callback_data='rodada_atual_{}'.format(str(grupo.id))
    )
    botao_voltar = InlineKeyboardButton('Voltar', callback_data='grupos')
    botoes.append([botao_pontuacao])
    botoes.append([botao_rodada_atual])
    botoes.append([botao_voltar])
    return botoes
