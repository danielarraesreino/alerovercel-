from app.models import HistoricoVendas, db
from datetime import datetime, timedelta
import random

def criar_historico_vendas(pratos, dias=30):
    """
    Cria histórico de vendas aleatório para os pratos
    
    Args:
        pratos: Lista de objetos Prato
        dias: Número de dias de histórico a serem criados (padrão: 30)
    """
    hoje = datetime.now().date()
    
    for dias_atras in range(dias, 0, -1):
        data = hoje - timedelta(days=dias_atras)
        
        # Ajusta a quantidade de vendas com base no dia da semana (mais vendas nos finais de semana)
        fator_dia = 1.5 if data.weekday() >= 5 else 1.0
        
        for prato in pratos:
            # Gera um número aleatório de vendas para cada prato em cada dia
            # Considera a popularidade do prato (preço mais baixo = mais vendas)
            fator_popularidade = 1.0 - (prato.preco_venda / 100)  # Pratos mais baratos são mais populares
            quantidade_base = random.randint(0, 10)  # Base de 0 a 10 vendas por dia
            
            quantidade = max(0, int(quantidade_base * fator_dia * fator_popularidade))
            
            if quantidade > 0:
                venda = HistoricoVendas(
                    prato_id=prato.id,
                    data=data,
                    quantidade=quantidade,
                    valor_total=quantidade * prato.preco_venda,
                    tipo_venda='balcão',
                    forma_pagamento=random.choice(['dinheiro', 'cartao_credito', 'pix']),
                    data_cadastro=datetime.now(),
                    data_atualizacao=datetime.now()
                )
                db.session.add(venda)
    
    db.session.commit()

def criar_fatores_sazonais():
    """Cria fatores sazonais para o AleroVeg"""
    # Fatores sazonais para dias da semana
    dias_semana = [
        ('Segunda-feira', 0.8, 'Menor movimento no início da semana'),
        ('Terça-feira', 0.9, 'Movimento abaixo da média'),
        ('Quarta-feira', 1.0, 'Dia de movimento médio'),
        ('Quinta-feira', 1.1, 'Movimento acima da média'),
        ('Sexta-feira', 1.3, 'Alto movimento'),
        ('Sábado', 1.5, 'Dia de maior movimento'),
        ('Domingo', 1.4, 'Alto movimento')
    ]
    
    for nome, fator, descricao in dias_semana:
        fator_sazonal = FatorSazonalidade(
            nome=nome,
            tipo='dia_semana',
            valor=nome.split('-')[0].strip().lower(),
            fator=fator,
            descricao=descricao,
            ativo=True,
            data_inicio=datetime.now().date(),
            data_fim=datetime.now().date() + timedelta(days=365),
            data_cadastro=datetime.now(),
            data_atualizacao=datetime.now()
        )
        db.session.add(fator_sazonal)
    
    # Fatores sazonais para meses do ano
    meses_ano = [
        ('Janeiro', 0.9, 'Férias escolares, movimento abaixo da média'),
        ('Fevereiro', 0.9, 'Pós-carnaval, movimento abaixo da média'),
        ('Março', 1.0, 'Volta às aulas, movimento normal'),
        ('Abril', 1.1, 'Período de festas juninas, movimento acima da média'),
        ('Maio', 1.0, 'Mês de mães, movimento normal'),
        ('Junho', 1.3, 'Festas juninas, alto movimento'),
        ('Julho', 1.2, 'Férias escolares, movimento acima da média'),
        ('Agosto', 1.0, 'Mês dos pais, movimento normal'),
        ('Setembro', 1.1, 'Primavera, movimento acima da média'),
        ('Outubro', 1.2, 'Mês das crianças, movimento acima da média'),
        ('Novembro', 1.3, 'Pré-Natal, alto movimento'),
        ('Dezembro', 1.5, 'Natal e Réveillon, maior movimento do ano')
    ]
    
    for nome, fator, descricao in meses_ano:
        fator_sazonal = FatorSazonalidade(
            nome=nome,
            tipo='mes_ano',
            valor=nome.lower(),
            fator=fator,
            descricao=descricao,
            ativo=True,
            data_inicio=datetime.now().date(),
            data_fim=datetime.now().date() + timedelta(days=365),
            data_cadastro=datetime.now(),
            data_atualizacao=datetime.now()
        )
        db.session.add(fator_sazonal)
    
    # Fatores sazonais para eventos especiais
    eventos_especiais = [
        ('Carnaval', 1.8, 'Alto movimento durante o carnaval', '2024-02-10', '2024-02-17'),
        ('Páscoa', 1.6, 'Aumento nas vendas de itens especiais', '2024-03-25', '2024-04-01'),
        ('Dia das Mães', 1.7, 'Alto movimento no almoço', '2024-05-12', '2024-05-12'),
        ('Dia dos Pais', 1.5, 'Aumento nas vendas', '2024-08-11', '2024-08-11'),
        ('Dia das Crianças', 1.6, 'Aumento nas vendas', '2024-10-12', '2024-10-12'),
        ('Natal', 2.0, 'Maior movimento do ano', '2024-12-20', '2024-12-25'),
        ('Réveillon', 1.9, 'Alto movimento', '2024-12-30', '2025-01-01')
    ]
    
    for nome, fator, descricao, data_inicio, data_fim in eventos_especiais:
        fator_sazonal = FatorSazonalidade(
            nome=nome,
            tipo='evento_especial',
            valor=nome.lower().replace(' ', '_'),
            fator=fator,
            descricao=descricao,
            ativo=True,
            data_inicio=datetime.strptime(data_inicio, '%Y-%m-%d').date(),
            data_fim=datetime.strptime(data_fim, '%Y-%m-%d').date(),
            data_cadastro=datetime.now(),
            data_atualizacao=datetime.now()
        )
        db.session.add(fator_sazonal)
    
    db.session.commit()
