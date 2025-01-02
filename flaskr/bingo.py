from flask import (
    Blueprint, g, redirect, render_template, request, url_for, make_response,
    current_app
)
from .db import execute_fetchall, execute_commit
from .auth import login_required
import random
import ast
# from xhtml2pdf import pisa
# from io import StringIO

bp = Blueprint('bingo', __name__)
BolasDoBingo = list()
BolasSorteadas = list()
QtdBolas = 75
Cartelas = dict()
Vencedores = dict()
Premiacao = {"1": 100, "2": 50, "3": 25}


def IniciarBingo(HashSet, maxBolas: int = 75):
    n = 1
    while n <= maxBolas:
        HashSet.append(n)
        n += 1
    return HashSet, maxBolas


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index(imagem: str = 'images/globo.gif'):
    global BolasSorteadas, BolasDoBingo, BolaEscolhida, QtdBolas, Cartelas, Vencedores, Premiacao
    # print(g.user['username'])
    if len(BolasDoBingo) == 0:
        BolasDoBingo, _ = IniciarBingo(BolasDoBingo)
    sql = ('SELECT p.id, author_id, bolasDoBingoJson, rankingJson, username'
           ' FROM bolasDoBingo p JOIN user u ON p.author_id =%s AND u.id =%s')
    parameters = (str(g.user["id"]), str(g.user["id"]))
    bolas = [dict(row)for row in execute_fetchall(sql=sql,
                                                  parameters=parameters)]
    print(bolas)
    if len(bolas) == 0:
        bolas = [{'bolasDoBingoJson': {}, 'rankingJson': {}}]

        sql = ("INSERT INTO `bolasDoBingo` (author_id, bolasDoBingoJson, "
               "rankingJson) VALUES (%s, %s, %s)")
        parameters = (g.user["id"], str(bolas[0]['bolasDoBingoJson']),
                      str(bolas[0]['rankingJson']))
        execute_commit(sql=sql, parameters=parameters)
    if 'BolasDoBingo' in bolas[0]['bolasDoBingoJson']:
        bolas[0]['bolasDoBingoJson'] = dict(ast.literal_eval(str(bolas[0]['bolasDoBingoJson'])))
        BolasDoBingo = bolas[0]['bolasDoBingoJson']['BolasDoBingo']
        BolasSorteadas = bolas[0]['bolasDoBingoJson']['BolasSorteadas']
        BolaEscolhida = bolas[0]['bolasDoBingoJson']['BolaEscolhida']
        QtdBolas = bolas[0]['bolasDoBingoJson']['QtdBolas']
    if 'Vencedores' in bolas[0]['rankingJson']:
        bolas[0]['rankingJson'] = dict(ast.literal_eval(str(bolas[0]['rankingJson'])))
        Vencedores = bolas[0]['rankingJson']['Vencedores']
        Cartelas = bolas[0]['rankingJson']['Cartelas']
    if 'Premiacao' in bolas[0]['rankingJson']:
        Premiacao = bolas[0]['rankingJson']['Premiacao']
    # print(request.form)
    if request.method == 'POST' and 'novaBola' in request.form:
        # print('Bolas do Bingo:', BolasDoBingo)
        if len(BolasDoBingo) != 0:
            BolaEscolhida = [random.choice(BolasDoBingo)]
            # print('Bola Escolhida:', BolaEscolhida)
            BolasSorteadas.append(BolaEscolhida[0])
            # print('Bolas Sorteadas:', BolasSorteadas)
            BolasDoBingo.remove(BolaEscolhida[0])
        jsonMontado = {
            'BolasDoBingo': BolasDoBingo,  # lista de bolas
            'BolasSorteadas': BolasSorteadas,  # lista de bolas
            'BolaEscolhida': BolaEscolhida,  # Bola única
            'QtdBolas': QtdBolas  # Quantidade de bolas
        }
        id = bolas[0]['id']
        sql = ('UPDATE bolasDoBingo SET bolasDoBingoJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)

        def reduzirCartelas():
            for cartela in Cartelas:
                if BolaEscolhida[0] in Cartelas[cartela]:
                    Cartelas[cartela].remove(BolaEscolhida[0])
            return Cartelas

        jsonMontado2 = {
            'Vencedores': Vencedores,  # lista de vencedores
            'Cartelas': reduzirCartelas() if len(Cartelas) > 0 else Cartelas,  # lista de cartelas
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.index'))

    if request.method == 'POST' and 'reset' in request.form:
        BolasDoBingo, QtdBolas = IniciarBingo(list(), QtdBolas)
        jsonMontado = {
            'BolasDoBingo': BolasDoBingo,  # lista de bolas
            'BolasSorteadas': [],  # lista de bolas
            'BolaEscolhida': [],  # Bola única
            'QtdBolas': QtdBolas  # Quantidade de bolas
        }
        print(bolas)
        id = (bolas[0]['id'] if 'id' in bolas[0] else g.user['id'])
        sql = ('UPDATE bolasDoBingo SET bolasDoBingoJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        jsonMontado2 = {
            'Vencedores': {},  # lista de vencedores
            'Cartelas': {},  # lista de cartelas
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.index'))

    if request.method == 'POST' and 'alterarBolas' in request.form:
        id = (bolas[0]['id'] if 'id' in bolas[0] else g.user['id'])
        return redirect(url_for(f'bingo.update', id=id))

    if request.method == 'POST' and 'ranking' in request.form:
        id = (bolas[0]['id'] if 'id' in bolas[0] else g.user['id'])
        return redirect(url_for(f'bingo.ranking', id=id))

    if request.method == 'POST' and 'conferir' in request.form:
        id = (bolas[0]['id'] if 'id' in bolas[0] else g.user['id'])
        return redirect(url_for(f'bingo.conferir', id=id))

    if request.method == 'POST' and 'config' in request.form:
        id = (bolas[0]['id'] if 'id' in bolas[0] else g.user['id'])
        return redirect(url_for(f'bingo.config', id=id))

    if request.method == 'POST' and 'gerador' in request.form:
        id = (bolas[0]['id'] if 'id' in bolas[0] else g.user['id'])
        return redirect(url_for(f'bingo.gerador', id=id))

    return render_template('bingo/index.html', bolas=bolas[0], qtdBolas=QtdBolas,
                           imagem=url_for('static', filename=imagem))


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    sql = ('SELECT p.id, author_id, bolasDoBingoJson, rankingJson, username'
           ' FROM bolasDoBingo p JOIN user u ON p.id =%s AND u.id =%s')
    parameters = (id, str(g.user["id"]))
    bolas = [dict(row) for row in execute_fetchall(sql=sql,
                                                   parameters=parameters)]
    if 'BolasDoBingo' in bolas[0]['bolasDoBingoJson']:
        bolas[0]['bolasDoBingoJson'] = dict(ast.literal_eval(str(bolas[0]['bolasDoBingoJson'])))
    if 'Vencedores' in bolas[0]['rankingJson']:
        bolas[0]['rankingJson'] = dict(ast.literal_eval(str(bolas[0]['rankingJson'])))

    if request.method == 'POST' and not 'cancel' in request.form:
        qtdBolasNova = int(request.form['alterarBolas'])
        BolasDoBingo, QtdBolas = IniciarBingo(list(), qtdBolasNova)
        jsonMontado = {
            'BolasDoBingo': BolasDoBingo,  # lista de bolas
            'BolasSorteadas': [],  # lista de bolas
            'BolaEscolhida': [],  # Bola única
            'QtdBolas': QtdBolas  # Quantidade de bolas
        }
        sql = ('UPDATE bolasDoBingo SET bolasDoBingoJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        jsonMontado2 = {
            'Vencedores': {},  # lista de vencedores
            'Cartelas': {},  # lista de cartelas
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.index'))

    if request.method == 'POST' and 'cancel' in request.form:
        return redirect(url_for('bingo.index'))

    print(bolas[0])
    return render_template('bingo/update.html', bolas=bolas[0])


@bp.route('/<int:id>/ranking', methods=('GET', 'POST'))
@login_required
def ranking(id):
    sql = ('SELECT p.id, author_id, bolasDoBingoJson, rankingJson, username'
           ' FROM bolasDoBingo p JOIN user u ON p.id =%s AND u.id =%s')
    parameters = (id, str(g.user["id"]))
    bolas = [dict(row) for row in execute_fetchall(sql=sql,
                                                   parameters=parameters)]
    if 'BolasDoBingo' in bolas[0]['bolasDoBingoJson']:
        bolas[0]['bolasDoBingoJson'] = dict(ast.literal_eval(str(bolas[0]['bolasDoBingoJson'])))
    if 'Vencedores' in bolas[0]['rankingJson']:
        bolas[0]['rankingJson'] = dict(ast.literal_eval(str(bolas[0]['rankingJson'])))

    if request.method == 'POST' and 'cancel' in request.form:
        return redirect(url_for('bingo.index'))
    print(bolas[0])
    return render_template('bingo/ranking.html', bolas=bolas[0])


@bp.route('/<int:id>/conferir', methods=('GET', 'POST'))
@login_required
def conferir(id):
    sql = ('SELECT p.id, author_id, bolasDoBingoJson, rankingJson, username'
           ' FROM bolasDoBingo p JOIN user u ON p.id =%s AND u.id =%s')
    parameters = (id, str(g.user["id"]))
    bolas = [dict(row) for row in execute_fetchall(sql=sql,
                                                   parameters=parameters)]
    if 'BolasDoBingo' in bolas[0]['bolasDoBingoJson']:
        bolas[0]['bolasDoBingoJson'] = dict(ast.literal_eval(str(bolas[0]['bolasDoBingoJson'])))
    if 'Vencedores' in bolas[0]['rankingJson']:
        bolas[0]['rankingJson'] = dict(ast.literal_eval(str(bolas[0]['rankingJson'])))

    if request.method == 'POST' and 'cartela' in request.form:
        Vencedores = bolas[0]['rankingJson']['Vencedores']
        Cartelas = bolas[0]['rankingJson']['Cartelas']
        numCartelas = str(request.form['cartela']).zfill(4)
        jsonMontado2 = {
            'Vencedores': Vencedores,  # lista de vencedores
            'Cartelas': Cartelas,  # lista de cartelas
            'Conferindo': numCartelas,  # só aparece ao conferir a cartela
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.conferir', id=id))

    if request.method == 'POST' and 'cancel' in request.form:
        Vencedores = bolas[0]['rankingJson']['Vencedores']
        Cartelas = bolas[0]['rankingJson']['Cartelas']
        if 'tamanho' in Vencedores:
            if Vencedores['tamanho'] == len(Vencedores['nomes']):
                Vencedores['tamanho'] += 1
        jsonMontado2 = {
            'Vencedores': Vencedores,  # lista de vencedores
            'Cartelas': Cartelas,  # lista de cartelas
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.index'))

    if request.method == 'POST' and 'adicionar' in request.form:
        Vencedores = bolas[0]['rankingJson']['Vencedores']
        Cartelas = bolas[0]['rankingJson']['Cartelas']
        Conferindo = bolas[0]['rankingJson']['Conferindo']
        CartelasBingo = Vencedores['CartelasBingo'] if 'CartelasBingo' in Vencedores else []
        if 'tamanho' not in Vencedores:
            Vencedores['tamanho'] = 1
            Vencedores['nomes'] = {}
        if str(Vencedores['tamanho']).zfill(4) not in Vencedores['nomes']:
            Vencedores['nomes'][str(Vencedores['tamanho']).zfill(4)] = [request.form['adicionar']]
        else:
            Vencedores['nomes'][str(Vencedores['tamanho']).zfill(4)].append(request.form['adicionar'])
        CartelasBingo.append(Conferindo)
        Vencedores['CartelasBingo'] = CartelasBingo
        jsonMontado2 = {
            'Vencedores': Vencedores,  # lista de vencedores
            'Cartelas': Cartelas,  # lista de cartelas
            'Premiacao': Premiacao,
            'Conferindo': Conferindo,  # só aparece ao conferir a cartela
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.conferir', id=id))

    print(bolas[0])
    return render_template('bingo/conferir.html', bolas=bolas[0])


@bp.route('/<int:id>/configuracao', methods=('GET', 'POST'))
@login_required
def config(id):
    sql = ('SELECT p.id, author_id, bolasDoBingoJson, rankingJson, username'
           ' FROM bolasDoBingo p JOIN user u ON p.id =%s AND u.id =%s')
    parameters = (id, str(g.user["id"]))
    bolas = [dict(row) for row in execute_fetchall(sql=sql,
                                                   parameters=parameters)]
    if 'BolasDoBingo' in bolas[0]['bolasDoBingoJson']:
        bolas[0]['bolasDoBingoJson'] = dict(ast.literal_eval(str(bolas[0]['bolasDoBingoJson'])))
    if 'Vencedores' in bolas[0]['rankingJson']:
        bolas[0]['rankingJson'] = dict(ast.literal_eval(str(bolas[0]['rankingJson'])))

    if request.method == 'POST' and 'alterarBolas' in request.form:
        Premiacao = bolas[0]['rankingJson']['Premiacao']
        qtdBolasNova = int(request.form['alterarBolas'])
        BolasDoBingo, QtdBolas = IniciarBingo(list(), qtdBolasNova)
        jsonMontado = {
            'BolasDoBingo': BolasDoBingo,  # lista de bolas
            'BolasSorteadas': [],  # lista de bolas
            'BolaEscolhida': [],  # Bola única
            'QtdBolas': QtdBolas  # Quantidade de bolas
        }
        sql = ('UPDATE bolasDoBingo SET bolasDoBingoJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        jsonMontado2 = {
            'Vencedores': {},  # lista de vencedores
            'Cartelas': {},  # lista de cartelas
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.index'))

    if request.method == 'POST' and 'cancel' in request.form:
        Vencedores = bolas[0]['rankingJson']['Vencedores']
        Cartelas = bolas[0]['rankingJson']['Cartelas']
        Premiacao = bolas[0]['rankingJson']['Premiacao']
        if 'tamanho' in Vencedores:
            if Vencedores['tamanho'] == len(Vencedores['nomes']):
                Vencedores['tamanho'] += 1
        jsonMontado2 = {
            'Vencedores': Vencedores,  # lista de vencedores
            'Cartelas': Cartelas,  # lista de cartelas
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.index'))

    if request.method == 'POST' and 'adicionar' in request.form:
        Vencedores = bolas[0]['rankingJson']['Vencedores']
        Cartelas = bolas[0]['rankingJson']['Cartelas']
        lugar = bolas[0]['rankingJson']['lugar'] if 'lugar' in bolas[0]['rankingJson'] else 1
        Premiacao = bolas[0]['rankingJson']['Premiacao'] if lugar > 1 else {}
        Premiacao[str(lugar)] = request.form['adicionar']
        lugar += 1
        jsonMontado2 = {
            'Vencedores': Vencedores,  # lista de vencedores
            'Cartelas': Cartelas,  # lista de cartelas
            'Premiacao': Premiacao,
            'lugar': lugar,  # só aparece ao conferir a cartela
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.config', id=id))

    print(bolas[0])
    return render_template('bingo/configuracao.html', bolas=bolas[0])


@bp.route('/<int:id>/gerador', methods=('GET', 'POST'))
@login_required
def gerador(id):
    global BolasSorteadas, BolasDoBingo, BolaEscolhida, QtdBolas, Cartelas, Premiacao
    # print(g.user['username'])
    if len(BolasDoBingo) == 0:
        BolasDoBingo = IniciarBingo(BolasDoBingo)
    sql = ('SELECT p.id, author_id, bolasDoBingoJson, rankingJson, username'
           ' FROM bolasDoBingo p JOIN user u ON p.author_id =%s AND u.id =%s')
    parameters = (str(g.user["id"]), str(g.user["id"]))
    bolas = [dict(row) for row in execute_fetchall(sql=sql,
                                                   parameters=parameters)]
    if len(bolas) == 0:
        bolas = [{'bolasDoBingoJson': {},
                  'rankingJson': {}}]
    if 'BolasDoBingo' in bolas[0]['bolasDoBingoJson']:
        bolas[0]['bolasDoBingoJson'] = dict(ast.literal_eval(str(bolas[0]['bolasDoBingoJson'])))
        BolasDoBingo = bolas[0]['bolasDoBingoJson']['BolasDoBingo']
        BolasSorteadas = bolas[0]['bolasDoBingoJson']['BolasSorteadas']
        BolaEscolhida = bolas[0]['bolasDoBingoJson']['BolaEscolhida']
        QtdBolas = bolas[0]['bolasDoBingoJson']['QtdBolas']
    if 'Vencedores' in bolas[0]['rankingJson']:
        bolas[0]['rankingJson'] = dict(ast.literal_eval(str(bolas[0]['rankingJson'])))
        Vencedores = bolas[0]['rankingJson']['Vencedores']
        Cartelas = bolas[0]['rankingJson']['Cartelas']
    # print(request.form)

    if request.method == 'POST' and 'gerar' in request.form:
        BolasDoBingo, QtdBolas = IniciarBingo(list(), QtdBolas)
        jsonMontado = {
            'BolasDoBingo': BolasDoBingo,  # lista de bolas
            'BolasSorteadas': [],  # lista de bolas
            'BolaEscolhida': [],  # Bola única
            'QtdBolas': QtdBolas  # Quantidade de bolas
        }
        # id = bolas[0]['id']
        sql = ('UPDATE bolasDoBingo SET bolasDoBingoJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        separaGerar = request.form['gerar'].split(',')
        qtdCartelas = int(separaGerar[0])
        if len(separaGerar) > 1:
            qtdCasas = int(separaGerar[1])
        else:
            qtdCasas = 25 if len(BolasDoBingo) > 25 else len(BolasDoBingo)
        Cartelas = {}

        def geradorDeNumeros(totalDeBolas, casas=25):
            bolasCartela = set()
            while len(bolasCartela) < casas:
                bolasCartela.add([random.choice(totalDeBolas)][0])
            bolasCartela = list(bolasCartela)
            bolasCartela.sort()
            return bolasCartela

        for i in range(qtdCartelas):
            Cartelas[str(i + 1).zfill(4)] = geradorDeNumeros(BolasDoBingo, qtdCasas)
            # BolaEscolhida = [random.choice(BolasDoBingo)]
            # BolasSorteadas.append(BolaEscolhida[0])
        print('Número de cartelas: ', len(Cartelas))
        print(Cartelas)
        jsonMontado2 = {
            'Vencedores': {},  # lista de vencedores
            'Cartelas': Cartelas,  # lista de cartelas
            'Premiacao': Premiacao
        }
        sql = ('UPDATE bolasDoBingo SET rankingJson = %s, author_id = %s'
               ' WHERE id = %s')
        parameters = (str(jsonMontado2), g.user['id'], id)
        execute_commit(sql=sql, parameters=parameters)
        return redirect(url_for('bingo.gerador', id=id))

    if request.method == 'POST' and 'cancel' in request.form:
        print(1)
        return redirect(url_for('bingo.index'))

    if request.method == 'POST' and 'cartelas' in request.form:
        print(1)
        return redirect(url_for('bingo.cartelas', id=id))

    return render_template('bingo/gerador.html', bolas=bolas[0], qtdBolas=QtdBolas)


@bp.route('/<int:id>/cartelas', methods=('GET', 'POST'))
@login_required
def cartelas(id):
    sql = ('SELECT p.id, author_id, bolasDoBingoJson, rankingJson, username'
           ' FROM bolasDoBingo p JOIN user u ON p.id =%s AND u.id =%s')
    parameters = (id, str(g.user["id"]))
    bolas = [dict(row) for row in execute_fetchall(sql=sql,
                                                   parameters=parameters)]
    if 'BolasDoBingo' in bolas[0]['bolasDoBingoJson']:
        bolas[0]['bolasDoBingoJson'] = dict(ast.literal_eval(str(bolas[0]['bolasDoBingoJson'])))
    if 'Vencedores' in bolas[0]['rankingJson']:
        bolas[0]['rankingJson'] = dict(ast.literal_eval(str(bolas[0]['rankingJson'])))

    if request.method == 'POST' and 'voltar' in request.form:
        return redirect(url_for('bingo.index'))

    html = render_template('bingo/cartelas.html', bolas=bolas[0], qtdBolas=QtdBolas)
    # html = render_template('bingo/abd.html')
    response = make_response(html)
    response.mimetype = 'application/pdf'

    def create_pdf(pdf_data):
        result_file = open('test.pdf', "w+b")
        # pdf = 'test.pdf'
        # pisa.CreatePDF(pdf_data, pdf, encoding="utf-8")
        # pisa.CreatePDF(StringIO(pdf_data), result_file, encoding="utf-8")

        return ''

    try:
        result_file = open('test.pdf', "w+b")
        pdf = create_pdf(html)
        # print(pdf.getvalue())
        result_file.close()
    finally:
        pass
    return html


if __name__ == '__main__':
    BolasDoBingo = list()
    IniciarBingo(BolasDoBingo)
    # print(BolasDoBingo)
    desejo = 'S'
    BolasSorteadas = list()
    BolaEscolhida = 0
    while desejo.upper() == 'S':
        print('Quantidade de bolas restantes: ' + str(len(BolasDoBingo)))
        BolaEscolhida = random.choice(BolasDoBingo)
        print(BolaEscolhida)
        BolasSorteadas.append(BolaEscolhida)
        desejo = input('Deseja continuar(S/N)? ')
        while True:
            if desejo.upper() == 'S' or desejo.upper() == 'N':
                break
            else:
                desejo = input("Digite 'S' ou 'N':  ")
        # ImprimirQuadro(BolasSorteadas)
        BolasDoBingo.remove(BolaEscolhida)
    print('O último número foi: ' + str(BolaEscolhida))
