from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from app.extensions import db
from app.models.modelo_estoque import EstoqueMovimentacao
from app.models.modelo_produto import Produto
from app.models.modelo_fornecedor import Fornecedor
from app.routes.estoque import bp
from datetime import datetime, timedelta
import pandas as pd
import io

@bp.route('/')
@bp.route('/index')
def index():
    """Lista movimentau00e7u00f5es de estoque"""
    page = request.args.get('page', 1, type=int)
    
    # Paru00e2metros de filtro
    produto_id = request.args.get('produto_id', type=int)
    tipo = request.args.get('tipo')  # 'entrada' ou 'sau00edda'
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Construir a query base
    query = EstoqueMovimentacao.query
    
    # Aplicar filtros
    if produto_id:
        query = query.filter_by(produto_id=produto_id)
    if tipo:
        query = query.filter_by(tipo=tipo)
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(EstoqueMovimentacao.data_movimentacao >= data_inicio)
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        data_fim = data_fim + timedelta(days=1)  # Incluir o dia completo
        query = query.filter(EstoqueMovimentacao.data_movimentacao < data_fim)
    
    # Ordenar e paginar
    movimentacoes = query.order_by(EstoqueMovimentacao.data_movimentacao.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Obter lista de produtos para filtro
    produtos = Produto.query.order_by(Produto.nome).all()
    
    return render_template('estoque/index.html', 
                          movimentacoes=movimentacoes, 
                          produtos=produtos)

@bp.route('/entrada', methods=['GET', 'POST'])
def entrada():
    """Registra entrada manual de estoque"""
    try:
        if request.method == 'POST':
            produto_id = request.form.get('produto_id', type=int)
            quantidade = request.form.get('quantidade', type=float)
            valor_unitario = request.form.get('valor_unitario', type=float)
            referencia = request.form.get('referencia')
            observacao = request.form.get('observacao')
            
            if not produto_id or not quantidade or quantidade <= 0:
                flash('Produto e quantidade vu00e1lida su00e3o obrigatu00f3rios!', 'danger')
                produtos = Produto.query.order_by(Produto.nome).all()
                return render_template('estoque/entrada.html', produtos=produtos)
            
            # Registrar movimento de entrada
            try:
                movimento = EstoqueMovimentacao.registrar_entrada(
                    produto_id=produto_id,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    referencia=referencia or 'Entrada Manual',
                    observacao=observacao
                )
                
                produto = Produto.query.get(produto_id)
                flash(f'Entrada registrada com sucesso! Novo estoque: {produto.estoque_atual} {produto.unidade_medida}', 'success')
                return redirect(url_for('estoque.index'))
                
            except ValueError as e:
                flash(f'Erro ao registrar entrada: {str(e)}', 'danger')
                produtos = Produto.query.order_by(Produto.nome).all()
                return render_template('estoque/entrada.html', produtos=produtos)
        
        produtos = Produto.query.order_by(Produto.nome).all()
        return render_template('estoque/entrada.html', produtos=produtos)
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": "Erro na página de entrada de estoque",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@bp.route('/saida', methods=['GET', 'POST'])
def saida():
    """Registra sau00edda manual de estoque"""
    if request.method == 'POST':
        produto_id = request.form.get('produto_id', type=int)
        quantidade = request.form.get('quantidade', type=float)
        referencia = request.form.get('referencia')
        observacao = request.form.get('observacao')
        
        if not produto_id or not quantidade or quantidade <= 0:
            flash('Produto e quantidade vu00e1lida su00e3o obrigatu00f3rios!', 'danger')
            produtos = Produto.query.order_by(Produto.nome).all()
            return render_template('estoque/saida.html', produtos=produtos)
        
        # Registrar movimento de sau00edda
        try:
            movimento = EstoqueMovimentacao.registrar_saida(
                produto_id=produto_id,
                quantidade=quantidade,
                referencia=referencia or 'Sau00edda Manual',
                observacao=observacao
            )
            
            produto = Produto.query.get(produto_id)
            flash(f'Sau00edda registrada com sucesso! Novo estoque: {produto.estoque_atual} {produto.unidade_medida}', 'success')
            return redirect(url_for('estoque.index'))
            
        except ValueError as e:
            flash(f'Erro ao registrar sau00edda: {str(e)}', 'danger')
            produtos = Produto.query.order_by(Produto.nome).all()
            return render_template('estoque/saida.html', produtos=produtos)
    
    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template('estoque/saida.html', produtos=produtos)

@bp.route('/detalhe_produto/<int:id>')
def detalhe_produto(id):
    """Mostra detalhes do estoque de um produto"""
    try:
        produto = Produto.query.get_or_404(id)
        
        # Buscar movimentau00e7u00f5es deste produto
        page = request.args.get('page', 1, type=int)
        movimentacoes = EstoqueMovimentacao.query.filter_by(produto_id=id).order_by(
            EstoqueMovimentacao.data_movimentacao.desc()
        ).paginate(page=page, per_page=10, error_out=False)
        
        return render_template('estoque/detalhe_produto.html', 
                            produto=produto, 
                            movimentacoes=movimentacoes)
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": "Erro ao exibir detalhes do produto",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@bp.route('/relatorio')
def relatorio():
    """Relatu00f3rio de estoque atual"""
    # Obter todos os produtos com seu valor em estoque
    produtos = Produto.query.order_by(Produto.categoria, Produto.nome).all()
    
    # Calcular totais
    total_valor_estoque = sum(p.calcular_valor_em_estoque() for p in produtos)
    total_itens = len(produtos)
    itens_em_falta = sum(1 for p in produtos if p.esta_em_falta())
    
    # Agrupar por categoria
    categorias = {}
    for produto in produtos:
        categoria = produto.categoria or 'Sem Categoria'
        if categoria not in categorias:
            categorias[categoria] = {
                'produtos': [],
                'total_valor': 0
            }
        
        valor_estoque = produto.calcular_valor_em_estoque()
        categorias[categoria]['produtos'].append(produto)
        categorias[categoria]['total_valor'] += valor_estoque
    
    return render_template('estoque/relatorio.html',
                          produtos=produtos,
                          categorias=categorias,
                          total_valor_estoque=total_valor_estoque,
                          total_itens=total_itens,
                          itens_em_falta=itens_em_falta)

@bp.route('/exportar_relatorio')
def exportar_relatorio():
    """Exporta relatu00f3rio de estoque para CSV"""
    from flask import Response
    
    # Obter todos os produtos
    produtos = Produto.query.order_by(Produto.categoria, Produto.nome).all()
    
    # Criar DataFrame
    data = [
        {
            'ID': p.id,
            'Cu00f3digo': p.codigo,
            'Nome': p.nome,
            'Categoria': p.categoria,
            'Unidade': p.unidade_medida,
            'Estoque Atual': p.estoque_atual,
            'Estoque Mu00ednimo': p.estoque_minimo,
            'Preu00e7o Unitu00e1rio': float(p.preco_unitario),
            'Valor em Estoque': p.calcular_valor_em_estoque(),
            'Fornecedor': p.fornecedor.razao_social if p.fornecedor else 'N/A',
            'Status': 'Em Falta' if p.esta_em_falta() else 'Normal'
        } for p in produtos
    ]
    
    df = pd.DataFrame(data)
    
    # Gerar CSV
    output = io.StringIO()
    df.to_csv(output, index=False)
    
    # Retornar como download
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename=relatorio_estoque_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

# API Endpoints
@bp.route('/api/movimentacoes/<int:produto_id>')
def api_movimentacoes(produto_id):
    """API para obter movimentau00e7u00f5es de um produto (JSON)"""
    # Limite opcional
    limite = request.args.get('limite', type=int, default=100)
    
    movimentacoes = EstoqueMovimentacao.query.filter_by(
        produto_id=produto_id
    ).order_by(
        EstoqueMovimentacao.data_movimentacao.desc()
    ).limit(limite).all()
    
    return jsonify([
        {
            'id': m.id,
            'tipo': m.tipo,
            'quantidade': m.quantidade,
            'data': m.data_movimentacao.strftime('%d/%m/%Y %H:%M'),
            'referencia': m.referencia,
            'valor_unitario': float(m.valor_unitario) if m.valor_unitario else None,
            'observacao': m.observacao
        } for m in movimentacoes
    ])

@bp.route('/api/em_falta')
def api_em_falta():
    """API para listar produtos com estoque abaixo do mu00ednimo (JSON)"""
    produtos = Produto.query.filter(
        Produto.estoque_atual < Produto.estoque_minimo
    ).all()
    
    return jsonify([
        {
            'id': p.id,
            'nome': p.nome,
            'estoque_atual': p.estoque_atual,
            'estoque_minimo': p.estoque_minimo,
            'unidade': p.unidade_medida,
            'percentual': (p.estoque_atual / p.estoque_minimo * 100) if p.estoque_minimo > 0 else 0
        } for p in produtos
    ])

@bp.route('/novo_produto', methods=['GET', 'POST'])
def novo_produto():
    """Cria um novo produto no estoque"""
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome')
        codigo = request.form.get('codigo')
        descricao = request.form.get('descricao')
        unidade = request.form.get('unidade')
        preco_unitario = request.form.get('preco_unitario', type=float, default=0)
        estoque_minimo = request.form.get('estoque_minimo', type=float, default=0)
        estoque_atual = request.form.get('estoque_atual', type=float, default=0)
        categoria = request.form.get('categoria')
        marca = request.form.get('marca')
        fornecedor_id = request.form.get('fornecedor_id', type=int)
        
        # Validações básicas
        if not nome or not unidade:
            flash('Nome e Unidade são obrigatórios!', 'danger')
            return redirect(url_for('estoque.novo_produto'))
        
        # Verificar se código já existe (se informado)
        if codigo and Produto.query.filter_by(codigo=codigo).first():
            flash('Código de produto já cadastrado!', 'danger')
            return redirect(url_for('estoque.novo_produto'))
        
        # Criar novo produto
        produto = Produto(
            nome=nome,
            codigo=codigo,
            descricao=descricao,
            unidade=unidade,
            preco_unitario=preco_unitario,
            estoque_minimo=estoque_minimo,
            estoque_atual=estoque_atual,
            categoria=categoria,
            marca=marca,
            fornecedor_id=fornecedor_id
        )
        
        db.session.add(produto)
        db.session.commit()
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('estoque.index'))
    
    # Obter lista de fornecedores para o formulário
    fornecedores = Fornecedor.query.order_by(Fornecedor.razao_social).all()
    return render_template('estoque/novo_produto.html', fornecedores=fornecedores)
