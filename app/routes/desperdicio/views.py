from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, Response
from app.extensions import db
from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_produto import Produto
from app.models.modelo_prato import Prato
from app.routes.desperdicio import bp
from datetime import datetime, date, timedelta
import pandas as pd
import io
import json

@bp.route('/')
@bp.route('/index')
def index():
    """Página principal do módulo de monitoramento de desperdício"""
    # Obter estatísticas gerais
    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    
    # Registros do mês atual
    registros_mes = RegistroDesperdicio.query.filter(
        RegistroDesperdicio.data_registro >= inicio_mes
    ).all()
    
    # Calcular valores gerais
    total_registros = len(registros_mes)
    total_valor = sum(float(r.valor_estimado or 0) for r in registros_mes)
    
    # Agrupar por categoria
    por_categoria = {}
    for registro in registros_mes:
        categoria = registro.categoria.nome
        if categoria not in por_categoria:
            por_categoria[categoria] = {
                'quantidade': 0,
                'valor': 0,
                'cor': registro.categoria.cor or '#CCCCCC'
            }
        por_categoria[categoria]['quantidade'] += 1
        por_categoria[categoria]['valor'] += float(registro.valor_estimado or 0)
    
    # Agrupar por tipo de item
    por_tipo = {
        'Produtos': {'quantidade': 0, 'valor': 0},
        'Pratos': {'quantidade': 0, 'valor': 0}
    }
    for registro in registros_mes:
        if registro.produto_id:
            por_tipo['Produtos']['quantidade'] += 1
            por_tipo['Produtos']['valor'] += float(registro.valor_estimado or 0)
        elif registro.prato_id:
            por_tipo['Pratos']['quantidade'] += 1
            por_tipo['Pratos']['valor'] += float(registro.valor_estimado or 0)
    
    # Metas ativas
    metas_ativas = MetaDesperdicio.query.filter_by(ativo=True).all()
    
    # Dados para gráficos (JSON)
    dados_categorias = []
    for cat, dados in por_categoria.items():
        dados_categorias.append({
            'categoria': cat,
            'valor': dados['valor'],
            'cor': dados['cor']
        })
    
    # Últimos registros
    ultimos_registros = RegistroDesperdicio.query.order_by(
        RegistroDesperdicio.data_registro.desc()
    ).limit(10).all()
    
    return render_template('desperdicio/index.html',
                          total_registros=total_registros,
                          total_valor=total_valor,
                          por_categoria=por_categoria,
                          por_tipo=por_tipo,
                          metas_ativas=metas_ativas,
                          dados_categorias=json.dumps(dados_categorias),
                          ultimos_registros=ultimos_registros,
                          mes_atual=inicio_mes.strftime('%B, %Y'))


@bp.route('/categorias')
def listar_categorias():
    """Lista todas as categorias de desperdício"""
    categorias = CategoriaDesperdicio.query.all()
    return render_template('desperdicio/categorias.html', categorias=categorias)


@bp.route('/categoria/criar', methods=['GET', 'POST'])
def criar_categoria():
    """Cria uma nova categoria de desperdício"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        cor = request.form.get('cor', '#CCCCCC')
        
        if not nome:
            flash('Nome da categoria é obrigatório!', 'danger')
            return redirect(url_for('desperdicio.criar_categoria'))
        
        # Verificar se já existe categoria com este nome
        if CategoriaDesperdicio.query.filter_by(nome=nome).first():
            flash('Já existe uma categoria com este nome!', 'danger')
            return redirect(url_for('desperdicio.criar_categoria'))
        
        categoria = CategoriaDesperdicio(
            nome=nome,
            descricao=descricao,
            cor=cor,
            ativo=True
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('desperdicio.listar_categorias'))
        
    return render_template('desperdicio/criar_categoria.html')


@bp.route('/categoria/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    """Edita uma categoria de desperdício"""
    categoria = CategoriaDesperdicio.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        cor = request.form.get('cor')
        ativo = 'ativo' in request.form
        
        if not nome:
            flash('Nome da categoria é obrigatório!', 'danger')
            return render_template('desperdicio/editar_categoria.html', categoria=categoria)
        
        # Verificar se já existe outra categoria com este nome
        categoria_existente = CategoriaDesperdicio.query.filter_by(nome=nome).first()
        if categoria_existente and categoria_existente.id != id:
            flash('Já existe outra categoria com este nome!', 'danger')
            return render_template('desperdicio/editar_categoria.html', categoria=categoria)
        
        # Atualizar categoria
        categoria.nome = nome
        categoria.descricao = descricao
        categoria.cor = cor
        categoria.ativo = ativo
        
        db.session.commit()
        
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('desperdicio.listar_categorias'))
        
    return render_template('desperdicio/editar_categoria.html', categoria=categoria)


@bp.route('/registros')
def listar_registros():
    """Lista todos os registros de desperdício"""
    page = request.args.get('page', 1, type=int)
    
    # Filtros opcionais
    categoria_id = request.args.get('categoria_id', type=int)
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    tipo_item = request.args.get('tipo_item')  # 'produto' ou 'prato'
    
    # Construir query
    query = RegistroDesperdicio.query
    
    # Aplicar filtros
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(RegistroDesperdicio.data_registro >= data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        data_fim = data_fim + timedelta(days=1)  # Incluir o dia todo
        query = query.filter(RegistroDesperdicio.data_registro < data_fim)
    
    if tipo_item == 'produto':
        query = query.filter(RegistroDesperdicio.produto_id != None)
    elif tipo_item == 'prato':
        query = query.filter(RegistroDesperdicio.prato_id != None)
    
    # Ordenar e paginar
    registros = query.order_by(RegistroDesperdicio.data_registro.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Obter categorias para filtro
    categorias = CategoriaDesperdicio.query.order_by(CategoriaDesperdicio.nome).all()
    
    return render_template('desperdicio/registros.html',
                          registros=registros,
                          categorias=categorias)


@bp.route('/registro/criar', methods=['GET', 'POST'])
def criar_registro():
    """Cria um novo registro de desperdício"""
    if request.method == 'POST':
        categoria_id = request.form.get('categoria_id', type=int)
        tipo_item = request.form.get('tipo_item')  # 'produto' ou 'prato'
        item_id = request.form.get('item_id', type=int)
        quantidade = request.form.get('quantidade', type=float)
        unidade_medida = request.form.get('unidade_medida')
        valor_estimado = request.form.get('valor_estimado', type=float)
        motivo = request.form.get('motivo')
        responsavel = request.form.get('responsavel')
        local = request.form.get('local')
        descricao = request.form.get('descricao')
        acoes_corretivas = request.form.get('acoes_corretivas')
        
        # Validações básicas
        if not categoria_id or not tipo_item or not item_id or not quantidade or not unidade_medida:
            flash('Categoria, tipo de item, item, quantidade e unidade de medida são obrigatórios!', 'danger')
            categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
            produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
            pratos = Prato.query.filter_by(ativo=True).order_by(Prato.nome).all()
            return render_template('desperdicio/criar_registro.html', categorias=categorias, produtos=produtos, pratos=pratos)
        
        # Criar o registro
        registro = RegistroDesperdicio(
            categoria_id=categoria_id,
            quantidade=quantidade,
            unidade_medida=unidade_medida,
            valor_estimado=valor_estimado,
            motivo=motivo,
            responsavel=responsavel,
            local=local,
            descricao=descricao,
            acoes_corretivas=acoes_corretivas
        )
        
        # Definir produto ou prato conforme o tipo selecionado
        if tipo_item == 'produto':
            registro.produto_id = item_id
        else:  # prato
            registro.prato_id = item_id
        
        db.session.add(registro)
        db.session.commit()
        
        flash('Registro de desperdício criado com sucesso!', 'success')
        return redirect(url_for('desperdicio.listar_registros'))
    
    # Obter listas para os selectboxes
    categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
    pratos = Prato.query.filter_by(ativo=True).order_by(Prato.nome).all()
    
    return render_template('desperdicio/criar_registro.html',
                          categorias=categorias,
                          produtos=produtos,
                          pratos=pratos)


@bp.route('/registro/visualizar/<int:id>')
def visualizar_registro(id):
    """Visualiza detalhes de um registro de desperdício"""
    registro = RegistroDesperdicio.query.get_or_404(id)
    return render_template('desperdicio/visualizar_registro.html', registro=registro)


@bp.route('/metas')
def listar_metas():
    """Lista todas as metas de redução de desperdício"""
    metas = MetaDesperdicio.query.all()
    return render_template('desperdicio/metas.html', metas=metas)


@bp.route('/meta/criar', methods=['GET', 'POST'])
def criar_meta():
    """Cria uma nova meta de redução de desperdício"""
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        categoria_id = request.form.get('categoria_id', type=int)
        produto_id = request.form.get('produto_id', type=int)
        valor_inicial = request.form.get('valor_inicial', type=float)
        meta_reducao_percentual = request.form.get('meta_reducao_percentual', type=float)
        acoes_propostas = request.form.get('acoes_propostas')
        responsavel = request.form.get('responsavel')
        
        # Validações básicas
        if not descricao or not data_inicio or not data_fim or not valor_inicial or not meta_reducao_percentual:
            flash('Descrição, período, valor inicial e percentual de redução são obrigatórios!', 'danger')
            categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
            produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
            return render_template('desperdicio/criar_meta.html', categorias=categorias, produtos=produtos)
        
        # Converter datas
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            
            if data_fim <= data_inicio:
                flash('A data final deve ser posterior à data inicial!', 'danger')
                categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
                produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
                return render_template('desperdicio/criar_meta.html', categorias=categorias, produtos=produtos)
        except ValueError:
            flash('Formato de data inválido!', 'danger')
            categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
            produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
            return render_template('desperdicio/criar_meta.html', categorias=categorias, produtos=produtos)
        
        # Criar a meta
        meta = MetaDesperdicio(
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            categoria_id=categoria_id,
            produto_id=produto_id,
            valor_inicial=valor_inicial,
            meta_reducao_percentual=meta_reducao_percentual,
            acoes_propostas=acoes_propostas,
            responsavel=responsavel,
            ativo=True
        )
        
        db.session.add(meta)
        db.session.commit()
        
        flash('Meta de redução de desperdício criada com sucesso!', 'success')
        return redirect(url_for('desperdicio.listar_metas'))
    
    # Obter listas para os selectboxes
    categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
    
    return render_template('desperdicio/criar_meta.html',
                          categorias=categorias,
                          produtos=produtos)


@bp.route('/meta/editar/<int:id>', methods=['GET', 'POST'])
def editar_meta(id):
    """Edita uma meta de redução de desperdício"""
    meta = MetaDesperdicio.query.get_or_404(id)
    
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        categoria_id = request.form.get('categoria_id', type=int)
        produto_id = request.form.get('produto_id', type=int)
        valor_inicial = request.form.get('valor_inicial', type=float)
        valor_atual = request.form.get('valor_atual', type=float)
        meta_reducao_percentual = request.form.get('meta_reducao_percentual', type=float)
        acoes_propostas = request.form.get('acoes_propostas')
        responsavel = request.form.get('responsavel')
        ativo = 'ativo' in request.form
        concluido = 'concluido' in request.form
        
        # Validações básicas
        if not descricao or not data_inicio or not data_fim or not valor_inicial or not meta_reducao_percentual:
            flash('Descrição, período, valor inicial e percentual de redução são obrigatórios!', 'danger')
            categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
            produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
            return render_template('desperdicio/editar_meta.html', meta=meta, categorias=categorias, produtos=produtos)
        
        # Converter datas
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            
            if data_fim <= data_inicio:
                flash('A data final deve ser posterior à data inicial!', 'danger')
                categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
                produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
                return render_template('desperdicio/editar_meta.html', meta=meta, categorias=categorias, produtos=produtos)
        except ValueError:
            flash('Formato de data inválido!', 'danger')
            categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
            produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
            return render_template('desperdicio/editar_meta.html', meta=meta, categorias=categorias, produtos=produtos)
        
        # Atualizar a meta
        meta.descricao = descricao
        meta.data_inicio = data_inicio
        meta.data_fim = data_fim
        meta.categoria_id = categoria_id
        meta.produto_id = produto_id
        meta.valor_inicial = valor_inicial
        meta.valor_atual = valor_atual
        meta.meta_reducao_percentual = meta_reducao_percentual
        meta.acoes_propostas = acoes_propostas
        meta.responsavel = responsavel
        meta.ativo = ativo
        meta.concluido = concluido
        
        db.session.commit()
        
        flash('Meta de redução de desperdício atualizada com sucesso!', 'success')
        return redirect(url_for('desperdicio.listar_metas'))
    
    # Obter listas para os selectboxes
    categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
    
    return render_template('desperdicio/editar_meta.html',
                          meta=meta,
                          categorias=categorias,
                          produtos=produtos)


@bp.route('/meta/visualizar/<int:id>')
def visualizar_meta(id):
    """Visualiza detalhes de uma meta de redução de desperdício"""
    meta = MetaDesperdicio.query.get_or_404(id)
    
    # Calcular progresso
    progresso = 0
    if meta.valor_inicial and meta.valor_atual is not None:
        reducao_almejada = meta.valor_inicial * (meta.meta_reducao_percentual / 100)
        reducao_atual = meta.valor_inicial - meta.valor_atual
        if reducao_almejada > 0:
            progresso = min(100, (reducao_atual / reducao_almejada) * 100)
    
    return render_template('desperdicio/visualizar_meta.html', meta=meta, progresso=progresso)


@bp.route('/relatorios')
def relatorios():
    """Página de relatórios de desperdício"""
    # Obter parâmetros para filtros
    periodo = request.args.get('periodo', 'mensal')  # mensal, trimestral, anual
    ano = request.args.get('ano', date.today().year, type=int)
    mes = request.args.get('mes', date.today().month, type=int)
    categoria_id = request.args.get('categoria_id', type=int)
    
    # Definir período base para o relatório
    hoje = date.today()
    data_inicio = None
    data_fim = None
    
    if periodo == 'mensal':
        data_inicio = date(ano, mes, 1)
        # Obter último dia do mês
        if mes == 12:
            data_fim = date(ano + 1, 1, 1) - timedelta(days=1)
        else:
            data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
        titulo_periodo = data_inicio.strftime('%B de %Y')
    elif periodo == 'trimestral':
        trimestre = (mes - 1) // 3 + 1
        mes_inicio = (trimestre - 1) * 3 + 1
        data_inicio = date(ano, mes_inicio, 1)
        if mes_inicio + 3 > 12:
            data_fim = date(ano + 1, mes_inicio + 3 - 12, 1) - timedelta(days=1)
        else:
            data_fim = date(ano, mes_inicio + 3, 1) - timedelta(days=1)
        titulo_periodo = f'{trimestre}º Trimestre de {ano}'
    else:  # anual
        data_inicio = date(ano, 1, 1)
        data_fim = date(ano, 12, 31)
        titulo_periodo = str(ano)
    
    # Consultar registros no período
    query = RegistroDesperdicio.query.filter(
        RegistroDesperdicio.data_registro >= data_inicio,
        RegistroDesperdicio.data_registro <= data_fim
    )
    
    # Aplicar filtro de categoria se houver
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
        categoria_nome = CategoriaDesperdicio.query.get(categoria_id).nome
        titulo_periodo += f' - Categoria: {categoria_nome}'
    
    registros = query.all()
    
    # Agrupar dados por categoria para o gráfico
    dados_por_categoria = {}
    for registro in registros:
        categoria = registro.categoria.nome
        if categoria not in dados_por_categoria:
            dados_por_categoria[categoria] = {
                'quantidade': 0,
                'valor': 0,
                'cor': registro.categoria.cor or '#CCCCCC'
            }
        dados_por_categoria[categoria]['quantidade'] += 1
        dados_por_categoria[categoria]['valor'] += float(registro.valor_estimado or 0)
    
    # Dados para gráfico
    dados_grafico = []
    for cat, dados in dados_por_categoria.items():
        dados_grafico.append({
            'categoria': cat,
            'valor': dados['valor'],
            'quantidade': dados['quantidade'],
            'cor': dados['cor']
        })
    
    # Calcular totais
    total_registros = len(registros)
    total_valor = sum(float(r.valor_estimado or 0) for r in registros)
    
    # Agrupar dados por mês para gráfico de tendência (caso relatório anual)
    dados_por_mes = {}
    if periodo == 'anual':
        for mes in range(1, 13):
            nome_mes = date(ano, mes, 1).strftime('%b')
            dados_por_mes[nome_mes] = 0
        
        for registro in registros:
            mes = registro.data_registro.strftime('%b')
            dados_por_mes[mes] += float(registro.valor_estimado or 0)
    
    # Calcular médias e períodos comparativos
    media_diaria = 0
    if total_registros > 0:
        dias_periodo = (data_fim - data_inicio).days + 1
        media_diaria = total_valor / dias_periodo
    
    # Obter todas as categorias para o filtro
    todas_categorias = CategoriaDesperdicio.query.all()
    
    return render_template('desperdicio/relatorios.html',
                          registros=registros,
                          total_registros=total_registros,
                          total_valor=total_valor,
                          media_diaria=media_diaria,
                          dados_grafico=json.dumps(dados_grafico),
                          dados_por_mes=json.dumps(dados_por_mes) if periodo == 'anual' else None,
                          titulo_periodo=titulo_periodo,
                          periodo=periodo,
                          ano=ano,
                          mes=mes,
                          categoria_id=categoria_id,
                          todas_categorias=todas_categorias,
                          data_inicio=data_inicio.strftime('%d/%m/%Y'),
                          data_fim=data_fim.strftime('%d/%m/%Y'))


@bp.route('/exportar/registros')
def exportar_registros():
    """Exporta registros de desperdício para CSV"""
    # Obter parâmetros para filtros
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    categoria_id = request.args.get('categoria_id', type=int)
    tipo_item = request.args.get('tipo_item')  # 'produto' ou 'prato'
    
    # Construir query
    query = RegistroDesperdicio.query
    
    # Aplicar filtros
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(RegistroDesperdicio.data_registro >= data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        data_fim = data_fim + timedelta(days=1)  # Incluir o dia todo
        query = query.filter(RegistroDesperdicio.data_registro < data_fim)
    
    if tipo_item == 'produto':
        query = query.filter(RegistroDesperdicio.produto_id != None)
    elif tipo_item == 'prato':
        query = query.filter(RegistroDesperdicio.prato_id != None)
    
    # Executar a query
    registros = query.all()
    
    # Preparar dados para exportação
    dados = []
    for registro in registros:
        item = ''
        tipo = ''
        if registro.produto_id:
            item = registro.produto.nome if registro.produto else ''
            tipo = 'Produto'
        elif registro.prato_id:
            item = registro.prato.nome if registro.prato else ''
            tipo = 'Prato'
        
        dados.append({
            'ID': registro.id,
            'Data': registro.data_registro.strftime('%d/%m/%Y %H:%M'),
            'Categoria': registro.categoria.nome if registro.categoria else '',
            'Tipo': tipo,
            'Item': item,
            'Quantidade': registro.quantidade,
            'Unidade': registro.unidade_medida,
            'Valor Estimado': float(registro.valor_estimado or 0),
            'Motivo': registro.motivo or '',
            'Responsável': registro.responsavel or '',
            'Local': registro.local or ''
        })
    
    # Criar DataFrame e exportar para CSV
    df = pd.DataFrame(dados)
    
    # Criar um buffer de memória para o CSV
    output = io.StringIO()
    df.to_csv(output, index=False, sep=';', encoding='utf-8')
    csv_data = output.getvalue()
    
    # Criar resposta para download
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=desperdicios_{timestamp}.csv'}
    )


@bp.route('/registrar', methods=['GET', 'POST'])
def registrar_desperdicio():
    """Registra um novo desperdício"""
    if request.method == 'POST':
        categoria_id = request.form.get('categoria_id', type=int)
        tipo_item = request.form.get('tipo_item')  # 'produto' ou 'prato'
        produto_id = request.form.get('produto_id', type=int)
        prato_id = request.form.get('prato_id', type=int)
        quantidade = request.form.get('quantidade', type=float)
        unidade = request.form.get('unidade')
        valor_estimado = request.form.get('valor_estimado', type=float)
        motivo = request.form.get('motivo')
        responsavel = request.form.get('responsavel')
        local = request.form.get('local')
        descricao = request.form.get('descricao')
        acoes_corretivas = request.form.get('acoes_corretivas')
        data_registro = request.form.get('data_registro')
        
        # Validações básicas
        if not categoria_id or not tipo_item or not quantidade or not unidade:
            flash('Categoria, tipo de item, quantidade e unidade são obrigatórios!', 'danger')
            categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
            produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
            pratos = Prato.query.filter_by(ativo=True).order_by(Prato.nome).all()
            return render_template('desperdicio/registrar_desperdicio.html', 
                                categorias=categorias, 
                                produtos=produtos, 
                                pratos=pratos,
                                hoje=datetime.now().strftime('%Y-%m-%d'))
        
        # Validar produto ou prato conforme o tipo
        if tipo_item == 'produto' and not produto_id:
            flash('Selecione um produto!', 'danger')
            return redirect(url_for('desperdicio.registrar_desperdicio'))
        elif tipo_item == 'prato' and not prato_id:
            flash('Selecione um prato!', 'danger')
            return redirect(url_for('desperdicio.registrar_desperdicio'))
        
        # Criar o registro
        registro = RegistroDesperdicio(
            categoria_id=categoria_id,
            quantidade=quantidade,
            unidade=unidade,
            valor_estimado=valor_estimado,
            motivo=motivo,
            responsavel=responsavel,
            local=local,
            descricao=descricao,
            acoes_corretivas=acoes_corretivas
        )
        
        # Definir produto ou prato conforme o tipo selecionado
        if tipo_item == 'produto':
            registro.produto_id = produto_id
        else:  # prato
            registro.prato_id = prato_id
        
        # Definir data do registro se informada
        if data_registro:
            registro.data_registro = datetime.strptime(data_registro, '%Y-%m-%d')
        
        db.session.add(registro)
        db.session.commit()
        
        flash('Registro de desperdício criado com sucesso!', 'success')
        return redirect(url_for('desperdicio.listar_registros'))
    
    # Obter listas para os selectboxes
    categorias = CategoriaDesperdicio.query.filter_by(ativo=True).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
    pratos = Prato.query.filter_by(ativo=True).order_by(Prato.nome).all()
    
    return render_template('desperdicio/registrar_desperdicio.html',
                          categorias=categorias,
                          produtos=produtos,
                          pratos=pratos,
                          hoje=datetime.now().strftime('%Y-%m-%d'))

