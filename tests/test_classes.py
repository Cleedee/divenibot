from collections import namedtuple

import pytest

from diveni.utils import SESSAO, BancoSessao
from diveni.model import Partida, Time

@pytest.fixture
def sessao_com_jogadores():
    p1 = Partida()
    flamengo = Time()
    flamengo.nome = 'Flamengo'
    p1.mandante = flamengo
    p2 = Partida()
    gremio = Time()
    gremio.nome = 'Grêmio'
    p2.mandante = gremio
    return {
        1: {
            'palpites': [(p1, None), (p2, None)],
            'posicao': 0
        },
        2: {
            'palpites': [],
            'posicao': 3
        }
    }

def test_avancar(sessao_com_jogadores):
    banco = BancoSessao(sessao_com_jogadores)
    banco.informar_jogador(1)
    banco.avancar()
    assert banco.posicao_atual() == 1
    assert banco.partida().mandante.nome == 'Grêmio'

def test_retroceder(sessao_com_jogadores):
    banco = BancoSessao(sessao_com_jogadores)
    banco.informar_jogador(1)
    banco.retroceder()
    assert banco.posicao_atual() == 1

def test_avancar_limite(sessao_com_jogadores):
    banco = BancoSessao(sessao_com_jogadores)
    banco.informar_jogador(1)
    banco.avancar()
    banco.avancar()
    assert banco.posicao_atual() == 0
    assert banco.partida().mandante.nome == 'Flamengo'

def test_quando_nao_encontra_jogador(sessao_com_jogadores):
    banco = BancoSessao(sessao_com_jogadores)
    # with pytest.raises(Exception):
    banco.informar_jogador(3)
    assert banco.posicao_atual() == 0
    assert len(banco.palpites()) == 0

def test_quando_informa_partidas_palpites(sessao_com_jogadores):
    PartidaFake = namedtuple("PartidaFake", 'mandante')
    TimeFake = namedtuple("TimeFake", 'nome')
    pp = [
        (PartidaFake(TimeFake('Fortaleza')), ),
        (PartidaFake(TimeFake('Goiás')), )
    ]
    banco = BancoSessao(sessao_com_jogadores)
    banco.informar_jogador(3)
    banco.informar_reserva_palpites(pp)
    assert banco.partida().mandante.nome == 'Fortaleza'

