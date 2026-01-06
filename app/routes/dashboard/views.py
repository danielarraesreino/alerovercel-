from flask import render_template, redirect, url_for, request, jsonify, current_app, Response
from app.extensions import db
from sqlalchemy import func, desc, extract, and_, or_, case
from app.models.modelo_prato import Prato, PratoInsumo
from app.models.modelo_produto import Produto
from app.models.modelo_cardapio import Cardapio, CardapioItem, CardapioSecao
from app.models.modelo_previsao import HistoricoVendas
from app.models.modelo_desperdicio import RegistroDesperdicio
from app.models.modelo_custo import CustoIndireto
from app.routes.dashboard import bp
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import json
import calendar
import io

# Funções auxiliares para cálculos de lucratividade
def calcular_metricas_principais(data_inicio, data_fim):
    """Calcula as métricas principais de lucratividade para o período"""
    # Obter vendas no período
    vendas = HistoricoVendas.query.filter(
        HistoricoVendas.data >= data_inicio,
        HistoricoVendas.data <= data_fim
    ).all()
    
    # Calcular receita total
    receita_total = sum(float(v.valor_total or 0) for v in vendas)
    
    # Calcular custos totais
    custo_total = 0
    for venda in vendas:
        # Custo do item vendido
        if venda.cardapio_item_id:
            item = CardapioItem.query.get(venda.cardapio_item_id)
            if item and item.prato:
                custo_total += float(item.prato.custo_total_por_porcao or 0) * venda.quantidade
        elif venda.prato_id:
            prato = Prato.query.get(venda.prato_id)
            if prato:
                custo_total += float(prato.custo_total_por_porcao or 0) * venda.quantidade
    
    # Adicionar custos indiretos do período
    custos_indiretos = CustoIndireto.query.filter(
        CustoIndireto.data_referencia >= data_inicio,
        CustoIndireto.data_referencia <= data_fim
    ).all()
    custo_indireto_total = sum(float(c.valor or 0) for c in custos_indiretos)
    custo_total += custo_indireto_total
    
    # Calcular lucro e margem
    lucro_total = receita_total - custo_total
    margem_media = (lucro_total / receita_total * 100) if receita_total > 0 else 0
    
    return receita_total, custo_total, lucro_total, margem_media


def obter_dados_diarios(data_inicio, data_fim):
    """Obtém dados diários de receitas e custos para gráfico"""
    # Criar dicionários para armazenar os valores por dia
    receitas_por_dia = {}
    custos_por_dia = {}
    lucros_por_dia = {}
    
    # Inicializar todos os dias do período com zero
    data_atual = data_inicio
    while data_atual <= data_fim:
        data_str = data_atual.strftime('%Y-%m-%d')
        receitas_por_dia[data_str] = 0
        custos_por_dia[data_str] = 0
        lucros_por_dia[data_str] = 0
        data_atual += timedelta(days=1)
    
    # Obter vendas no período
    vendas = HistoricoVendas.query.filter(
        HistoricoVendas.data >= data_inicio,
        HistoricoVendas.data <= data_fim
    ).all()
    
    # Calcular receitas e custos diretos por dia
    for venda in vendas:
        data_str = venda.data.strftime('%Y-%m-%d')
        
        # Adicionar receita
        receitas_por_dia[data_str] += float(venda.valor_total or 0)
        
        # Calcular custo direto
        custo_item = 0
        if venda.cardapio_item_id:
            item = CardapioItem.query.get(venda.cardapio_item_id)
            if item and item.prato:
                custo_item = float(item.prato.custo_total_por_porcao or 0) * venda.quantidade
        elif venda.prato_id:
            prato = Prato.query.get(venda.prato_id)
            if prato:
                custo_item = float(prato.custo_total_por_porcao or 0) * venda.quantidade
        
        custos_por_dia[data_str] += custo_item
    
    # Adicionar custos indiretos por dia
    custos_indiretos = CustoIndireto.query.filter(
        CustoIndireto.data_referencia >= data_inicio,
        CustoIndireto.data_referencia <= data_fim
    ).all()
    
    for custo in custos_indiretos:
        data_str = custo.data_referencia.strftime('%Y-%m-%d')
        if data_str in custos_por_dia:  # Verificar se o dia está no período
            custos_por_dia[data_str] += float(custo.valor or 0)
    
    # Calcular lucros por dia
    for data_str in receitas_por_dia.keys():
        lucros_por_dia[data_str] = receitas_por_dia[data_str] - custos_por_dia[data_str]
    
    # Preparar dados para o gráfico
    datas = []
    receitas = []
    custos = []
    lucros = []
    
    for data_str in sorted(receitas_por_dia.keys()):
        data_formatada = datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m')
        datas.append(data_formatada)
        receitas.append(receitas_por_dia[data_str])
        custos.append(custos_por_dia[data_str])
        lucros.append(lucros_por_dia[data_str])
    
    return {
        'datas': datas,
        'receitas': receitas,
        'custos': custos,
        'lucros': lucros
    }


def obter_top_pratos(data_inicio, data_fim, limite=5):
    """Obtém os pratos mais lucrativos no período"""
    # Consultar vendas de pratos no período
    vendas_pratos = db.session.query(
        Prato.id,
        Prato.nome,
        func.sum(HistoricoVendas.quantidade).label('quantidade_vendida'),
        func.sum(HistoricoVendas.valor_total).label('receita_total')
    ).join(
        HistoricoVendas,
        HistoricoVendas.prato_id == Prato.id
    ).filter(
        HistoricoVendas.data >= data_inicio,
        HistoricoVendas.data <= data_fim
    ).group_by(
        Prato.id
    ).order_by(
        func.sum(HistoricoVendas.valor_total).desc()
    ).limit(limite).all()
    
    # Preparar dados com cálculo de lucro
    top_pratos = []
    for p in vendas_pratos:
        prato = Prato.query.get(p.id)
        if prato:
            custo_unitario = float(prato.custo_total_por_porcao or 0)
            custo_total = custo_unitario * p.quantidade_vendida
            lucro = float(p.receita_total or 0) - custo_total
            margem = (lucro / float(p.receita_total)) * 100 if float(p.receita_total) > 0 else 0
            
            top_pratos.append({
                'id': p.id,
                'nome': p.nome,
                'quantidade_vendida': p.quantidade_vendida,
                'receita_total': float(p.receita_total or 0),
                'custo_total': custo_total,
                'lucro': lucro,
                'margem': margem
            })
    
    return top_pratos


def obter_distribuicao_categorias(data_inicio, data_fim):
    """Obtém a distribuição de vendas por categoria"""
    # Consultar vendas de itens de cardápio agrupadas por seção
    vendas_por_secao = db.session.query(
        CardapioSecao.nome,
        func.sum(HistoricoVendas.valor_total).label('receita_total')
    ).join(
        CardapioItem,
        CardapioItem.secao_id == CardapioSecao.id
    ).join(
        HistoricoVendas,
        HistoricoVendas.cardapio_item_id == CardapioItem.id
    ).filter(
        HistoricoVendas.data >= data_inicio,
        HistoricoVendas.data <= data_fim
    ).group_by(
        CardapioSecao.nome
    ).all()
    
    # Preparar dados para o gráfico de pizza
    categorias = []
    valores = []
    cores = []
    
    # Cores padrão para as categorias
    cores_padrao = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#8AC249', '#EA5F89', '#00B8D4', '#6D4C41'
    ]
    
    for i, (secao, receita) in enumerate(vendas_por_secao):
        categorias.append(secao)
        valores.append(float(receita or 0))
        cores.append(cores_padrao[i % len(cores_padrao)])
    
    return {
        'categorias': categorias,
        'valores': valores,
        'cores': cores
    }


def obter_tendencia_lucratividade(meses=6):
    """Obtém a tendência de lucratividade dos últimos meses"""
    hoje = date.today()
    dados_mensais = []
    
    # Calcular para cada mês
    for i in range(meses - 1, -1, -1):
        # Calcular o mês de referência (mês atual - i)
        mes_ref = hoje.month - i
        ano_ref = hoje.year
        
        # Ajustar para meses anteriores
        while mes_ref <= 0:
            mes_ref += 12
            ano_ref -= 1
        
        # Definir período
        data_inicio = date(ano_ref, mes_ref, 1)
        if mes_ref == 12:
            data_fim = date(ano_ref + 1, 1, 1) - timedelta(days=1)
        else:
            data_fim = date(ano_ref, mes_ref + 1, 1) - timedelta(days=1)
        
        # Calcular métricas
        receita, custo, lucro, margem = calcular_metricas_principais(data_inicio, data_fim)
        
        # Adicionar aos dados mensais
        dados_mensais.append({
            'mes': calendar.month_name[mes_ref],
            'receita': receita,
            'custo': custo,
            'lucro': lucro,
            'margem': margem
        })
    
    # Preparar dados para o gráfico
    meses = [d['mes'] for d in dados_mensais]
    receitas = [d['receita'] for d in dados_mensais]
    custos = [d['custo'] for d in dados_mensais]
    lucros = [d['lucro'] for d in dados_mensais]
    margens = [d['margem'] for d in dados_mensais]
    
    return {
        'meses': meses,
        'receitas': receitas,
        'custos': custos,
        'lucros': lucros,
        'margens': margens
    }


def obter_indicadores_desperdicio(data_inicio, data_fim):
    """Obtém indicadores de desperdício para o período"""
    # Consultar registros de desperdício no período
    desperdicios = RegistroDesperdicio.query.filter(
        RegistroDesperdicio.data_registro >= data_inicio,
        RegistroDesperdicio.data_registro <= data_fim
    ).all()
    
    # Calcular valor total do desperdício
    valor_total = sum(float(d.valor_estimado or 0) for d in desperdicios)
    
    # Contar registros por categoria
    contagem_por_categoria = {}
    valor_por_categoria = {}
    
    for desp in desperdicios:
        if desp.categoria:
            categoria = desp.categoria.nome
            if categoria not in contagem_por_categoria:
                contagem_por_categoria[categoria] = 0
                valor_por_categoria[categoria] = 0
            
            contagem_por_categoria[categoria] += 1
            valor_por_categoria[categoria] += float(desp.valor_estimado or 0)
    
    # Obter receita total do período (para calcular percentual de desperdício)
    receita_total, _, _, _ = calcular_metricas_principais(data_inicio, data_fim)
    
    # Calcular percentual de desperdício em relação à receita
    percentual_desperdicio = (valor_total / receita_total * 100) if receita_total > 0 else 0
    
    return {
        'total_registros': len(desperdicios),
        'valor_total': valor_total,
        'percentual_receita': percentual_desperdicio,
        'categorias': contagem_por_categoria,
        'valores_por_categoria': valor_por_categoria
    }

@bp.route('/')
@bp.route('/index')
def index():
    """Página principal do dashboard de lucratividade"""
    try:
        # Obter período selecionado
        periodo = request.args.get('periodo', 'mensal')
        hoje = date.today()
        
        if periodo == 'mensal':
            inicio_periodo = date(hoje.year, hoje.month, 1)
            fim_periodo = date(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])
            titulo_periodo = f"Mês de {inicio_periodo.strftime('%B/%Y')}"
        elif periodo == 'trimestral':
            trimestre = (hoje.month - 1) // 3
            inicio_periodo = date(hoje.year, trimestre * 3 + 1, 1)
            fim_periodo = date(hoje.year, (trimestre + 1) * 3, calendar.monthrange(hoje.year, (trimestre + 1) * 3)[1])
            titulo_periodo = f"{trimestre + 1}º Trimestre de {hoje.year}"
        elif periodo == 'anual':
            inicio_periodo = date(hoje.year, 1, 1)
            fim_periodo = date(hoje.year, 12, 31)
            titulo_periodo = f"Ano de {hoje.year}"
        else:  # personalizado
            inicio_periodo = request.args.get('data_inicio', date(hoje.year, hoje.month, 1))
            fim_periodo = request.args.get('data_fim', date(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1]))
            titulo_periodo = f"Período de {inicio_periodo} a {fim_periodo}"
        
        # Calcular métricas principais
        receita_total, custo_total, lucro_total, margem_media = calcular_metricas_principais(inicio_periodo, fim_periodo)
        
        # Obter dados para gráficos
        dados_diarios = obter_dados_diarios(inicio_periodo, fim_periodo)
        top_pratos = obter_top_pratos(inicio_periodo, fim_periodo)
        distribuicao_categorias = obter_distribuicao_categorias(inicio_periodo, fim_periodo)
        tendencia_lucratividade = obter_tendencia_lucratividade()
        
        # Calcular valor do desperdício
        desperdicios = RegistroDesperdicio.query.filter(
            RegistroDesperdicio.data_registro >= inicio_periodo,
            RegistroDesperdicio.data_registro <= fim_periodo
        ).all()
        valor_desperdicio = sum(float(d.valor_estimado or 0) for d in desperdicios)
        
        # Calcular impacto do desperdício em relação ao custo total
        impacto_desperdicio = (valor_desperdicio / custo_total * 100) if custo_total > 0 else 0
        
        return render_template('dashboard/index.html',
                            titulo_periodo=titulo_periodo,
                            periodo=periodo,
                            inicio_periodo=inicio_periodo,
                            fim_periodo=fim_periodo,
                            receita_total=receita_total,
                            custo_total=custo_total,
                            lucro_total=lucro_total,
                            margem_media=margem_media,
                            dados_diarios=dados_diarios,
                            top_pratos=top_pratos,
                            distribuicao_categorias=distribuicao_categorias,
                            tendencia_lucratividade=tendencia_lucratividade,
                            valor_desperdicio=valor_desperdicio,
                            impacto_desperdicio=impacto_desperdicio)
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": "Erro interno no Dashboard",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@bp.route('/relatorio/pratos')
def relatorio_pratos():
    """Relatório detalhado de lucratividade por prato"""
    # Obter período para análise
    hoje = date.today()
    data_inicio = request.args.get('data_inicio', (hoje - timedelta(days=30)).strftime('%Y-%m-%d'))
    data_fim = request.args.get('data_fim', hoje.strftime('%Y-%m-%d'))
    
    try:
        inicio_periodo = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        fim_periodo = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        inicio_periodo = hoje - timedelta(days=30)
        fim_periodo = hoje
        
    # Consultar todos os pratos com vendas no período
    vendas_pratos = db.session.query(
        Prato.id,
        Prato.nome,
        Prato.categoria,
        func.sum(HistoricoVendas.quantidade).label('quantidade_vendida'),
        func.sum(HistoricoVendas.valor_total).label('receita_total')
    ).join(
        HistoricoVendas,
        HistoricoVendas.prato_id == Prato.id
    ).filter(
        HistoricoVendas.data >= inicio_periodo,
        HistoricoVendas.data <= fim_periodo
    ).group_by(
        Prato.id
    ).order_by(
        func.sum(HistoricoVendas.valor_total).desc()
    ).all()
    
    # Preparar dados detalhados para cada prato
    pratos_detalhes = []
    for p in vendas_pratos:
        prato = Prato.query.get(p.id)
        if prato:
            # Custos diretos
            custo_unitario = float(prato.custo_total_por_porcao or 0)
            custo_direto_total = custo_unitario * p.quantidade_vendida
            
            # Estimar custos indiretos 
            # (baseado na proporção das vendas deste prato em relação ao total)
            receita_total_periodo, _, _, _ = calcular_metricas_principais(inicio_periodo, fim_periodo)
            proporcao_receita = float(p.receita_total) / receita_total_periodo if receita_total_periodo > 0 else 0
            
            custos_indiretos = CustoIndireto.query.filter(
                CustoIndireto.data_referencia >= inicio_periodo,
                CustoIndireto.data_referencia <= fim_periodo
            ).all()
            total_indiretos = sum(float(c.valor or 0) for c in custos_indiretos)
            custo_indireto_estimado = total_indiretos * proporcao_receita
            
            # Cálculos finais
            custo_total = custo_direto_total + custo_indireto_estimado
            lucro = float(p.receita_total) - custo_total
            margem = (lucro / float(p.receita_total)) * 100 if float(p.receita_total) > 0 else 0
            
            pratos_detalhes.append({
                'id': p.id,
                'nome': p.nome,
                'categoria': p.categoria,
                'quantidade_vendida': p.quantidade_vendida,
                'receita_total': float(p.receita_total),
                'custo_direto_total': custo_direto_total,
                'custo_indireto_estimado': custo_indireto_estimado,
                'custo_total': custo_total,
                'lucro': lucro,
                'margem': margem,
                'custo_unitario': custo_unitario,
                'preco_venda': float(p.receita_total) / p.quantidade_vendida if p.quantidade_vendida > 0 else 0
            })
    
    # Ordenar por margem de lucro (do maior para o menor)
    pratos_detalhes.sort(key=lambda x: x['margem'], reverse=True)
    
    # Calcular totais gerais
    total_receita = sum(p['receita_total'] for p in pratos_detalhes)
    total_custo = sum(p['custo_total'] for p in pratos_detalhes)
    total_lucro = total_receita - total_custo
    margem_media_geral = (total_lucro / total_receita * 100) if total_receita > 0 else 0
    
    # Agrupar por categoria
    categorias = {}
    for prato in pratos_detalhes:
        categoria = prato['categoria'] or 'Sem Categoria'
        if categoria not in categorias:
            categorias[categoria] = {
                'receita': 0,
                'custo': 0,
                'lucro': 0,
                'pratos': []
            }
        
        categorias[categoria]['receita'] += prato['receita_total']
        categorias[categoria]['custo'] += prato['custo_total']
        categorias[categoria]['lucro'] += prato['lucro']
        categorias[categoria]['pratos'].append(prato)
    
    # Calcular margens por categoria
    for cat, dados in categorias.items():
        dados['margem'] = (dados['lucro'] / dados['receita'] * 100) if dados['receita'] > 0 else 0
    
    # Ordenar categorias por margem
    categorias_ordenadas = sorted(
        [(cat, dados) for cat, dados in categorias.items()],
        key=lambda x: x[1]['margem'],
        reverse=True
    )
    
    return render_template('dashboard/relatorio_pratos.html',
                          data_inicio=inicio_periodo.strftime('%Y-%m-%d'),
                          data_fim=fim_periodo.strftime('%Y-%m-%d'),
                          pratos=pratos_detalhes,
                          categorias=categorias_ordenadas,
                          total_receita=total_receita,
                          total_custo=total_custo,
                          total_lucro=total_lucro,
                          margem_media=margem_media_geral)


@bp.route('/relatorio/categorias')
def relatorio_categorias():
    """Relatório de lucratividade por categoria"""
    # Obter período para análise
    hoje = date.today()
    data_inicio = request.args.get('data_inicio', (hoje - timedelta(days=30)).strftime('%Y-%m-%d'))
    data_fim = request.args.get('data_fim', hoje.strftime('%Y-%m-%d'))
    
    try:
        inicio_periodo = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        fim_periodo = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        inicio_periodo = hoje - timedelta(days=30)
        fim_periodo = hoje
    
    # Consultar vendas por seção de cardápio
    vendas_secoes = db.session.query(
        CardapioSecao.id,
        CardapioSecao.nome,
        func.sum(HistoricoVendas.quantidade).label('quantidade_vendida'),
        func.sum(HistoricoVendas.valor_total).label('receita_total')
    ).join(
        CardapioItem,
        CardapioItem.secao_id == CardapioSecao.id
    ).join(
        HistoricoVendas,
        HistoricoVendas.cardapio_item_id == CardapioItem.id
    ).filter(
        HistoricoVendas.data >= inicio_periodo,
        HistoricoVendas.data <= fim_periodo
    ).group_by(
        CardapioSecao.id
    ).all()
    
    # Consultar vendas por categoria de prato
    vendas_categorias_prato = db.session.query(
        Prato.categoria,
        func.sum(HistoricoVendas.quantidade).label('quantidade_vendida'),
        func.sum(HistoricoVendas.valor_total).label('receita_total')
    ).join(
        HistoricoVendas,
        HistoricoVendas.prato_id == Prato.id
    ).filter(
        HistoricoVendas.data >= inicio_periodo,
        HistoricoVendas.data <= fim_periodo,
        Prato.categoria != None
    ).group_by(
        Prato.categoria
    ).all()
    
    # Combinar dados (seções de cardápio e categorias de pratos)
    categorias_dados = {}
    
    # Processar seções de cardápio
    for secao in vendas_secoes:
        # Obter itens da seção para calcular custos
        itens = CardapioItem.query.filter_by(secao_id=secao.id).all()
        custo_total = 0
        
        for item in itens:
            # Obter vendas específicas deste item no período
            vendas_item = HistoricoVendas.query.filter(
                HistoricoVendas.cardapio_item_id == item.id,
                HistoricoVendas.data >= inicio_periodo,
                HistoricoVendas.data <= fim_periodo
            ).all()
            
            # Calcular custo
            if item.prato:
                for venda in vendas_item:
                    custo_total += float(item.prato.custo_total_por_porcao or 0) * venda.quantidade
        
        # Adicionar aos dados por categoria
        categorias_dados[f'Seção: {secao.nome}'] = {
            'tipo': 'Seção',
            'nome': secao.nome,
            'quantidade': secao.quantidade_vendida,
            'receita': float(secao.receita_total),
            'custo': custo_total,
            'lucro': float(secao.receita_total) - custo_total
        }
    
    # Processar categorias de pratos
    for cat in vendas_categorias_prato:
        categoria = cat.categoria or 'Sem Categoria'
        nome_categoria = f'Categoria: {categoria}'
        
        # Obter pratos desta categoria
        pratos = Prato.query.filter_by(categoria=categoria).all()
        custo_total = 0
        
        for prato in pratos:
            # Obter vendas específicas deste prato no período
            vendas_prato = HistoricoVendas.query.filter(
                HistoricoVendas.prato_id == prato.id,
                HistoricoVendas.data >= inicio_periodo,
                HistoricoVendas.data <= fim_periodo
            ).all()
            
            # Calcular custo
            if prato:
                for venda in vendas_prato:
                    custo_total += float(prato.custo_total_por_porcao or 0) * venda.quantidade
        
        # Adicionar aos dados por categoria
        if nome_categoria not in categorias_dados:
            categorias_dados[nome_categoria] = {
                'tipo': 'Categoria',
                'nome': categoria,
                'quantidade': 0,
                'receita': 0,
                'custo': 0,
                'lucro': 0
            }
        
        categorias_dados[nome_categoria]['quantidade'] += cat.quantidade_vendida
        categorias_dados[nome_categoria]['receita'] += float(cat.receita_total)
        categorias_dados[nome_categoria]['custo'] += custo_total
        categorias_dados[nome_categoria]['lucro'] += float(cat.receita_total) - custo_total
    
    # Calcular margens
    for nome, dados in categorias_dados.items():
        dados['margem'] = (dados['lucro'] / dados['receita'] * 100) if dados['receita'] > 0 else 0
    
    # Converter para lista e ordenar por margem de lucro
    categorias_lista = []
    for nome, dados in categorias_dados.items():
        categorias_lista.append({
            'nome': nome,
            'tipo': dados['tipo'],
            'categoria': dados['nome'],
            'quantidade': dados['quantidade'],
            'receita': dados['receita'],
            'custo': dados['custo'],
            'lucro': dados['lucro'],
            'margem': dados['margem']
        })
    
    # Ordenar por margem (maior para menor)
    categorias_lista.sort(key=lambda x: x['margem'], reverse=True)
    
    # Calcular totais gerais
    total_receita = sum(c['receita'] for c in categorias_lista)
    total_custo = sum(c['custo'] for c in categorias_lista)
    total_lucro = total_receita - total_custo
    margem_media_geral = (total_lucro / total_receita * 100) if total_receita > 0 else 0
    
    # Preparar dados para gráficos
    dados_grafico = {
        'categorias': [c['nome'] for c in categorias_lista],
        'receitas': [c['receita'] for c in categorias_lista],
        'lucros': [c['lucro'] for c in categorias_lista],
        'margens': [c['margem'] for c in categorias_lista]
    }
    
    return render_template('dashboard/relatorio_categorias.html',
                          data_inicio=inicio_periodo.strftime('%Y-%m-%d'),
                          data_fim=fim_periodo.strftime('%Y-%m-%d'),
                          categorias=categorias_lista,
                          dados_grafico=json.dumps(dados_grafico),
                          total_receita=total_receita,
                          total_custo=total_custo,
                          total_lucro=total_lucro,
                          margem_media=margem_media_geral)
