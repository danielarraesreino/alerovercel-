from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Tuple, Optional
from calendar import monthrange

def calcular_preco_medio_ponderado(estoque_atual: float, preco_atual: float, 
                                 quantidade_nova: float, preco_novo: float) -> float:
    """Calcula o preu00e7o mu00e9dio ponderado apu00f3s uma nova compra
    
    Args:
        estoque_atual: Quantidade atual em estoque
        preco_atual: Preu00e7o unitu00e1rio atual
        quantidade_nova: Quantidade da nova compra
        preco_novo: Preu00e7o unitu00e1rio da nova compra
        
    Returns:
        float: Novo preu00e7o mu00e9dio ponderado
    """
    if estoque_atual <= 0 and quantidade_nova <= 0:
        return 0.0
    
    valor_estoque_atual = estoque_atual * preco_atual
    valor_nova_compra = quantidade_nova * preco_novo
    quantidade_total = estoque_atual + quantidade_nova
    
    if quantidade_total <= 0:
        return 0.0
    
    preco_medio = (valor_estoque_atual + valor_nova_compra) / quantidade_total
    return round(preco_medio, 4)

def calcular_custo_direto_prato(insumos: List[Dict]) -> Tuple[float, float, float]:
    """Calcula o custo direto de um prato com base em seus insumos
    
    Args:
        insumos: Lista de dicionu00e1rios, cada um com 'quantidade', 'preco_unitario' e 'obrigatorio'
        rendimento: Quantidade de poru00e7u00f5es que o prato produz
        
    Returns:
        Tuple[float, float, float]: Custo total, custo de itens obrigatu00f3rios, custo de itens opcionais
    """
    custo_total = 0.0
    custo_obrigatorios = 0.0
    custo_opcionais = 0.0
    
    for insumo in insumos:
        quantidade = insumo.get('quantidade', 0)
        preco_unitario = insumo.get('preco_unitario', 0)
        obrigatorio = insumo.get('obrigatorio', True)
        
        custo_item = quantidade * preco_unitario
        custo_total += custo_item
        
        if obrigatorio:
            custo_obrigatorios += custo_item
        else:
            custo_opcionais += custo_item
    
    return (custo_total, custo_obrigatorios, custo_opcionais)

def calcular_custo_por_porcao(custo_total: float, rendimento: float) -> float:
    """Calcula o custo por poru00e7u00e3o
    
    Args:
        custo_total: Custo total do prato
        rendimento: Quantidade de poru00e7u00f5es que o prato produz
        
    Returns:
        float: Custo por poru00e7u00e3o
    """
    if rendimento <= 0:
        return 0.0
    
    return custo_total / rendimento

def calcular_preco_venda(custo_total: float, margem: float) -> float:
    """Calcula o preu00e7o de venda baseado no custo e margem desejada
    
    Args:
        custo_total: Custo total por unidade
        margem: Margem de lucro desejada (em percentual, ex: 30 para 30%)
        
    Returns:
        float: Preu00e7o de venda sugerido
    """
    margem_decimal = margem / 100
    return custo_total * (1 + margem_decimal)

def calcular_margem_atual(preco_venda: float, custo_total: float) -> float:
    """Calcula a margem atual com base no preu00e7o de venda e custo
    
    Args:
        preco_venda: Preu00e7o de venda atual
        custo_total: Custo total por unidade
        
    Returns:
        float: Margem atual em percentual
    """
    if custo_total <= 0 or preco_venda <= 0:
        return 0.0
    
    lucro = preco_venda - custo_total
    margem = (lucro / custo_total) * 100
    return round(margem, 2)

def calcular_rateio_custos_indiretos(custos_indiretos: float, criterio_rateio: Dict) -> Dict:
    """Calcula o rateio de custos indiretos entre produtos/pratos
    
    Args:
        custos_indiretos: Valor total de custos indiretos a ratear
        criterio_rateio: Dicionu00e1rio com 'id' e 'peso' para cada item a receber rateio
        
    Returns:
        Dict: Dicionu00e1rio com 'id' e 'valor_rateio' para cada item
    """
    # Calcular soma total dos pesos
    total_pesos = sum(item['peso'] for item in criterio_rateio.values())
    
    if total_pesos <= 0:
        return {}
    
    # Calcular valor de rateio para cada item
    resultado = {}
    for id, dados in criterio_rateio.items():
        peso = dados['peso']
        percentual = peso / total_pesos
        valor_rateio = custos_indiretos * percentual
        resultado[id] = {
            'percentual': percentual,
            'valor_rateio': valor_rateio
        }
    
    return resultado

def calcular_custos_indiretos_periodo(data_inicio: date, data_fim: date, 
                                     custos_por_tipo: Dict[str, List[Dict]]) -> Dict[str, float]:
    """Calcula os custos indiretos em um peru00edodo
    
    Args:
        data_inicio: Data de inu00edcio do peru00edodo
        data_fim: Data de fim do peru00edodo
        custos_por_tipo: Dicionu00e1rio com tipo de custo e lista de valores
        
    Returns:
        Dict[str, float]: Dicionu00e1rio com tipo de custo e valor total no peru00edodo
    """
    resultado = {}
    total_geral = 0.0
    
    for tipo, custos in custos_por_tipo.items():
        total_tipo = 0.0
        
        for custo in custos:
            data_custo = custo.get('data')
            if data_inicio <= data_custo <= data_fim:
                total_tipo += custo.get('valor', 0)
        
        resultado[tipo] = total_tipo
        total_geral += total_tipo
    
    resultado['total'] = total_geral
    return resultado

def calcular_total_dias_mes(mes: int, ano: int) -> int:
    """Calcula o total de dias em um mu00eas especu00edfico
    
    Args:
        mes: Mu00eas (1-12)
        ano: Ano com 4 du00edgitos
        
    Returns:
        int: Total de dias no mu00eas
    """
    return monthrange(ano, mes)[1]

def calcular_validade_por_periodo(data_producao: date, dias_validade: int) -> date:
    """Calcula a data de validade com base na data de produu00e7u00e3o e dias de validade
    
    Args:
        data_producao: Data de produu00e7u00e3o
        dias_validade: Quantidade de dias de validade
        
    Returns:
        date: Data de validade
    """
    from datetime import timedelta
    return data_producao + timedelta(days=dias_validade)

def calcular_estoque_minimo(consumo_medio: float, tempo_reposicao: int, 
                           estoque_seguranca: float = 0.5) -> float:
    """Calcula o estoque mu00ednimo recomendado
    
    Args:
        consumo_medio: Consumo mu00e9dio diu00e1rio
        tempo_reposicao: Tempo mu00e9dio de reposiu00e7u00e3o em dias
        estoque_seguranca: Fator de seguranu00e7a (ex: 0.5 = 50% extra)
        
    Returns:
        float: Estoque mu00ednimo recomendado
    """
    estoque_minimo = consumo_medio * tempo_reposicao * (1 + estoque_seguranca)
    return round(estoque_minimo, 2)
