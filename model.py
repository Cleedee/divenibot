from orator import DatabaseManager, Model
from orator.orm import has_one, belongs_to, belongs_to_many
from dotenv import dotenv_values

env = dotenv_values('.env')

config = {
    'sqlite': {
        'driver': 'sqlite',
        'database': env['DB_URI'],
    }
}

db = DatabaseManager(config)

Model.set_connection_resolver(db)


class Usuario(Model):
    __table__ = 'usuario'
    __timestamps__ = False


class Torneio(Model):
    __table__ = 'torneio'
    __timestamps__ = False


class Grupo(Model):
    __table__ = 'grupo'
    __timestamps__ = False

    @belongs_to
    def torneio(self):
        return Torneio


class Jogador(Model):
    __table__ = 'jogador'
    __timestamps__ = False

    @belongs_to
    def usuario(self):
        return Usuario

    @belongs_to
    def grupo(self):
        return Grupo


class Rodada(Model):
    __table__ = 'rodada'
    __timestamps__ = False

    @belongs_to
    def torneio(self):
        return Torneio


class Time(Model):
    __table__ = 'time'
    __timestamps__ = False


class Partida(Model):
    __table__ = 'partida'
    __timestamps__ = False

    @belongs_to
    def mandante(self):
        return Time

    @belongs_to
    def visitante(self):
        return Time


class Palpite(Model):
    __table__ = 'palpite'
    __timestamps__ = False