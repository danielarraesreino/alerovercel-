#!/usr/bin/env python
from app import create_app
from app.extensions import db
from app.models.modelo_previsao import HistoricoVendas
from app.models.modelo_cardapio import CardapioItem
from app.models.modelo_prato import Prato
from datetime import datetime, timedelta
import random

def seed_historico_vendas():
    """Popula a tabela historico_vendas com dados de exemplo"""
    app = create_app('development')
    with app.app_context():
        print("Criando dados de histórico de vendas...")
        
        # Obter todos os pratos e itens de cardápio disponíveis
        pratos = Prato.query.all()
        cardapio_itens = CardapioItem.query.all()
        
        if not pratos and not cardapio_itens:
            print("Não há pratos ou itens de cardápio cadastrados. Criando dados de exemplo sem referências.")
        
        # Data atual
        hoje = datetime.now().date()
        
        # Criar registros para os últimos 90 dias
        registros_criados = 0
        for dias_atras in range(90, 0, -1):
            data = hoje - timedelta(days=dias_atras)
            
            # Gerar entre 5 e 20 vendas por dia
            num_vendas = random.randint(5, 20)
            
            for _ in range(num_vendas):
                # Decidir se é venda de prato ou item de cardápio
                if random.choice([True, False]) and pratos:
                    prato = random.choice(pratos)
                    prato_id = prato.id
                    cardapio_item_id = None
                    valor_unitario = float(prato.preco_venda or random.uniform(15.0, 50.0))
                elif cardapio_itens:
                    cardapio_item = random.choice(cardapio_itens)
                    cardapio_item_id = cardapio_item.id
                    prato_id = None
                    valor_unitario = float(cardapio_item.preco_venda or random.uniform(15.0, 50.0))
                else:
                    # Se não houver pratos nem itens de cardápio, criar dados fictícios
                    prato_id = None
                    cardapio_item_id = None
                    valor_unitario = random.uniform(15.0, 50.0)
                
                # Quantidade vendida (entre 1 e 5)
                quantidade = random.randint(1, 5)
                
                # Calcular valor total
                valor_total = quantidade * valor_unitario
                
                # Período do dia
                periodo_dia = random.choice(['Manhã', 'Tarde', 'Noite'])
                
                # Dia da semana (0 = Segunda, 6 = Domingo)
                dia_semana = data.weekday()
                
                # Semana do mês (aproximação)
                semana_mes = (data.day - 1) // 7 + 1
                
                # Mês
                mes = data.month
                
                # Feriado (aleatório, 10% de chance)
                feriado = random.random() < 0.1
                
                # Evento especial (aleatório, 5% de chance)
                evento_especial = None
                if random.random() < 0.05:
                    eventos = ['Aniversário da Cidade', 'Festival Gastronômico', 'Feriado Municipal', 'Evento Corporativo']
                    evento_especial = random.choice(eventos)
                
                # Clima (aleatório)
                climas = ['Ensolarado', 'Nublado', 'Chuvoso', 'Tempestade', 'Parcialmente Nublado']
                clima = random.choice(climas)
                
                # Temperatura (entre 15 e 35 graus)
                temperatura = random.uniform(15.0, 35.0)
                
                # Criar o registro de venda
                venda = HistoricoVendas(
                    data=data,
                    cardapio_item_id=cardapio_item_id,
                    prato_id=prato_id,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total,
                    periodo_dia=periodo_dia,
                    dia_semana=dia_semana,
                    semana_mes=semana_mes,
                    mes=mes,
                    feriado=feriado,
                    evento_especial=evento_especial,
                    clima=clima,
                    temperatura=temperatura
                )
                
                db.session.add(venda)
                registros_criados += 1
        
        # Commit das alterações
        db.session.commit()
        print(f"Foram criados {registros_criados} registros de histórico de vendas.")

if __name__ == '__main__':
    seed_historico_vendas()
