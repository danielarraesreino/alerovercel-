from app import create_app
from app.extensions import db
from app.models import *
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker('pt_BR')

def seed_database():
    """Popula o banco de dados com dados iniciais para teste"""
    app = create_app('development')
    with app.app_context():
        print("Criando dados de exemplo para teste...")
        
        # Criar fornecedores
        print("Criando fornecedores...")
        fornecedores = crear_fornecedores(5)
        
        # Criar produtos
        print("Criando produtos...")
        produtos = crear_produtos(20, fornecedores)
        
        # Criar notas fiscais
        print("Criando notas fiscais...")
        notas = crear_notas_fiscais(10, fornecedores, produtos)
        
        # Criar movimentau00e7u00f5es de estoque
        print("Criando movimentau00e7u00f5es de estoque...")
        movimentacoes = crear_movimentacoes(30, produtos)
        
        # Criar custos indiretos
        print("Criando custos indiretos...")
        custos = crear_custos_indiretos(3)
        
        # Criar pratos
        print("Criando pratos...")
        pratos = crear_pratos(8, produtos)
        
        # Criar cardápios
        print("Criando cardápios...")
        cardapios = crear_cardapios(2, pratos)
        
        print("Dados de exemplo criados com sucesso!")
        
        return {
            "fornecedores": len(fornecedores),
            "produtos": len(produtos),
            "notas": len(notas),
            "movimentacoes": len(movimentacoes),
            "custos": len(custos),
            "pratos": len(pratos),
            "cardapios": len(cardapios)
        }

def crear_fornecedores(quantidade):
    """Cria fornecedores de exemplo"""
    fornecedores = []
    
    for _ in range(quantidade):
        cnpj = ''.join([str(random.randint(0, 9)) for _ in range(14)])
        razao_social = fake.company()
        
        fornecedor = Fornecedor(
            cnpj=cnpj,
            razao_social=razao_social,
            nome_fantasia=razao_social.split()[0],
            endereco=fake.street_address(),
            cidade=fake.city(),
            estado=fake.state_abbr(),
            cep=fake.postcode().replace('-', ''),
            telefone=fake.phone_number(),
            email=fake.company_email(),
            inscricao_estadual=''.join([str(random.randint(0, 9)) for _ in range(9)])
        )
        
        db.session.add(fornecedor)
        fornecedores.append(fornecedor)
    
    db.session.commit()
    return fornecedores

def crear_produtos(quantidade, fornecedores):
    """Cria produtos de exemplo"""
    produtos = []
    categorias = ['Carnes', 'Vegetais', 'Lu00e1cteos', 'Gru00e3os', 'Temperos', 'Bebidas']
    unidades = ['kg', 'g', 'l', 'ml', 'un', 'cx']
    
    for i in range(quantidade):
        codigo = f"PRD{i+1:04d}"
        categoria = random.choice(categorias)
        unidade = random.choice(unidades)
        fornecedor = random.choice(fornecedores)
        preco = round(random.uniform(1.5, 150.0), 2)
        
        descricao = None
        if random.random() > 0.3:
            descricao = fake.paragraph(nb_sentences=2)
        
        # Criar nomes de acordo com a categoria
        if categoria == 'Carnes':
            nome = f"{random.choice(['Filu00e9', 'Costela', 'Peito', 'Paleta', 'Picanha'])} de {random.choice(['Boi', 'Frango', 'Porco', 'Peixe'])}"
        elif categoria == 'Vegetais':
            nome = random.choice(['Cebola', 'Alho', 'Tomate', 'Batata', 'Cenoura', 'Alface', 'Couve', 'Repolho', 'Abobrinha'])
        elif categoria == 'Lu00e1cteos':
            nome = f"{random.choice(['Leite', 'Queijo', 'Manteiga', 'Iogurte', 'Creme de Leite'])} {random.choice(['Integral', 'Desnatado', 'Semi-desnatado', ''])}"
        elif categoria == 'Gru00e3os':
            nome = random.choice(['Arroz', 'Feiju00e3o', 'Lentilha', 'Gru00e3o de Bico', 'Milho', 'Ervilha'])
        elif categoria == 'Temperos':
            nome = random.choice(['Sal', 'Pimenta', 'Oru00e9gano', 'Alecrim', 'Manjericu00e3o', 'Au00e7afru00e3o', 'Cominho'])
        else:  # Bebidas
            nome = f"{random.choice(['Suco', 'Refrigerante', 'Água', 'Vinho', 'Cerveja'])} {random.choice(['Natural', 'Artesanal', 'Importado', ''])}"
        
        # Estoque mínimo e atual
        estoque_minimo = round(random.uniform(5, 50), 2)
        estoque_atual = round(random.uniform(0, 100), 2)
        
        produto = Produto(
            codigo=fake.unique.ean13(),
            nome=nome,
            descricao=fake.sentence(),
            unidade=unidade,
            preco_unitario=preco,
            estoque_minimo=random.randint(5, 20),
            estoque_atual=random.randint(20, 100),
            categoria=categoria,
            marca=fake.company(),
            fornecedor_id=fornecedor.id,
            ativo=True
        )
        db.session.add(produto)
        produtos.append(produto)
    
    db.session.commit()
    return produtos

def crear_notas_fiscais(quantidade, fornecedores, produtos):
    """Cria notas fiscais de exemplo"""
    notas = []
    
    for i in range(quantidade):
        # Escolher um fornecedor aleatu00f3rio
        fornecedor = random.choice(fornecedores)
        
        # Gerar dados da nota
        chave_acesso = ''.join([str(random.randint(0, 9)) for _ in range(44)])
        numero = str(random.randint(1000, 9999))
        serie = str(random.randint(1, 9))
        data_emissao = datetime.now() - timedelta(days=random.randint(1, 60))
        
        # Valores
        valor_produtos = 0.0
        valor_frete = round(random.uniform(0, 100), 2)
        valor_seguro = round(random.uniform(0, 50), 2)
        valor_desconto = round(random.uniform(0, 30), 2)
        valor_impostos = 0.0
        
        # Criar a nota
        nota = NFNota(
            chave_acesso=chave_acesso,
            numero=numero,
            serie=serie,
            data_emissao=data_emissao,
            fornecedor_id=fornecedor.id,
            valor_frete=valor_frete,
            valor_seguro=valor_seguro,
            valor_desconto=valor_desconto,
            valor_total=0.0,
            valor_produtos=0.0,
            valor_impostos=0.0,
            xml_data="<xml>Simulação de XML</xml>"
        )
        
        db.session.add(nota)
        db.session.flush()  # Para obter o ID da nota
        
        # Criar itens da nota
        num_itens = random.randint(2, 6)
        produtos_escolhidos = random.sample(produtos, num_itens)
        
        for j, produto in enumerate(produtos_escolhidos, 1):
            quantidade = round(random.uniform(1, 10), 2)
            valor_unitario = float(produto.preco_unitario)
            valor_total = quantidade * valor_unitario
            
            # Valores fiscais
            percentual_icms = random.randint(0, 18)
            valor_icms = round((percentual_icms / 100) * valor_total, 2)
            percentual_ipi = random.randint(0, 10)
            valor_ipi = round((percentual_ipi / 100) * valor_total, 2)
            
            # Atualizar valores da nota
            valor_produtos += valor_total
            valor_impostos += valor_icms + valor_ipi
            
            # Criar o item
            item = NFItem(
                nf_nota_id=nota.id,
                produto_id=produto.id,
                num_item=j,
                quantidade=quantidade,
                valor_unitario=valor_unitario,
                valor_total=valor_total,
                unidade_medida=produto.unidade,
                percentual_icms=percentual_icms,
                valor_icms=valor_icms,
                percentual_ipi=percentual_ipi,
                valor_ipi=valor_ipi
            )
            
            db.session.add(item)
            
            # Atualizar estoque e preu00e7o do produto
            produto.preco_unitario = valor_unitario
            produto.estoque_atual += quantidade
        
        # Atualizar valores finais da nota
        nota.valor_produtos = valor_produtos
        nota.valor_impostos = valor_impostos
        nota.valor_total = valor_produtos + valor_frete + valor_seguro + valor_impostos - valor_desconto
        
        notas.append(nota)
    
    db.session.commit()
    return notas

def crear_movimentacoes(quantidade, produtos):
    """Cria movimentau00e7u00f5es de estoque de exemplo"""
    movimentacoes = []
    tipos = ['entrada', 'sau00edda']
    referencias = ['Compra Direta', 'Ajuste Manual', 'Consumo', 'Produu00e7u00e3o', 'Venda']
    
    for i in range(quantidade):
        produto = random.choice(produtos)
        tipo = random.choice(tipos)
        quantidade_mov = round(random.uniform(0.5, 5), 2)
        data = datetime.now() - timedelta(days=random.randint(0, 30))
        referencia = random.choice(referencias)
        
        # Verificar se u00e9 possu00edvel realizar sau00edda
        if tipo == 'sau00edda' and produto.estoque_atual < quantidade_mov:
            # Se nu00e3o tiver estoque suficiente, fazer uma entrada primeiro
            entrada = EstoqueMovimentacao(
                produto_id=produto.id,
                quantidade=quantidade_mov * 2,  # Garante que teru00e1 estoque suficiente
                tipo='entrada',
                data_movimentacao=data - timedelta(hours=1),  # 1 hora antes
                referencia='Compra Emergencial',
                valor_unitario=produto.preco_unitario
            )
            
            db.session.add(entrada)
            db.session.flush()
            
            produto.estoque_atual += quantidade_mov * 2
            movimentacoes.append(entrada)
        
        # Criar a movimentau00e7u00e3o
        movimento = EstoqueMovimentacao(
            produto_id=produto.id,
            quantidade=quantidade_mov,
            tipo=tipo,
            data_movimentacao=data,
            referencia=referencia,
            valor_unitario=produto.preco_unitario,
            observacao=fake.sentence() if random.random() > 0.5 else None
        )
        
        # Atualizar o estoque do produto
        if tipo == 'entrada':
            produto.estoque_atual += quantidade_mov
        else:  # sau00edda
            produto.estoque_atual -= quantidade_mov
        
        db.session.add(movimento)
        movimentacoes.append(movimento)
    
    db.session.commit()
    return movimentacoes

def crear_custos_indiretos(quantidade_meses):
    """Cria custos indiretos de exemplo para os u00faltimos meses"""
    custos = []
    tipos_custos = [
        {'nome': 'Aluguel', 'valor_base': 5000},
        {'nome': 'Energia Elu00e9trica', 'valor_base': 2000},
        {'nome': 'Salu00e1rios', 'valor_base': 15000},
        {'nome': 'u00c1gua', 'valor_base': 800},
        {'nome': 'Internet', 'valor_base': 300},
        {'nome': 'Material de Limpeza', 'valor_base': 500},
        {'nome': 'Manutenu00e7u00e3o', 'valor_base': 1000},
    ]
    
    # Criar custos para os u00faltimos meses
    for i in range(quantidade_meses):
        data_ref = datetime.now().replace(day=1) - timedelta(days=30*i)
        
        for tipo in tipos_custos:
            # Variau00e7u00e3o aleatu00f3ria no valor
            variacao = random.uniform(0.9, 1.1)  # 10% para mais ou menos
            valor = round(tipo['valor_base'] * variacao, 2)
            
            custo = CustoIndireto(
                descricao=tipo['nome'],
                valor=valor,
                data_referencia=data_ref,
                tipo=tipo['nome'],
                recorrente=True,
                observacao=f"Custo de {tipo['nome']} para {data_ref.strftime('%B/%Y')}"
            )
            
            db.session.add(custo)
            custos.append(custo)
    
    db.session.commit()
    return custos

def crear_pratos(quantidade, produtos):
    """Cria pratos de exemplo"""
    pratos = []
    categorias = ['Entrada', 'Prato Principal', 'Sobremesa', 'Bebida']
    
    # Nomes de pratos por categoria
    nomes_pratos = {
        'Entrada': [
            'Bruschetta de Tomate', 'Salada Caprese', 'Croquetes de Carne',
            'Camaru00e3o Empanado', 'Carpaccio de Filu00e9 Mignon'
        ],
        'Prato Principal': [
            'Filu00e9 u00e0 Parmegiana', 'Risoto de Cogumelos', 'Lasanha Bolonhesa',
            'Picanha Grelhada', 'Frango Assado com Batatas', 'Peixe ao Molho de Camaru00e3o'
        ],
        'Sobremesa': [
            'Pudim de Leite', 'Mousse de Chocolate', 'Torta de Limu00e3o',
            'Sorvete Artesanal', 'Cheesecake de Frutas Vermelhas'
        ],
        'Bebida': [
            'Suco Natural', 'Caipirinha', 'Vinho Tinto', 'Cerveja Artesanal',
            'Coquetel de Frutas', 'u00c1gua Saborizada'
        ]
    }
    
    for i in range(quantidade):
        # Escolher uma categoria
        categoria = random.choice(categorias)
        
        # Escolher um nome de prato da categoria
        nome = random.choice(nomes_pratos[categoria])
        
        # Remover da lista para evitar duplicidade
        nomes_pratos[categoria].remove(nome)
        
        # Definir rendimento e unidades dependendo da categoria
        if categoria in ['Entrada', 'Prato Principal', 'Sobremesa']:
            rendimento = random.randint(1, 10)
            unidade_rendimento = 'poru00e7u00f5es'
        else:  # Bebida
            rendimento = random.randint(1, 5)
            unidade_rendimento = 'litros'
        
        tempo_preparo = random.randint(10, 120)
        margem = random.uniform(30, 70)
        descricao = fake.paragraph(nb_sentences=3)
        
        # Criar o prato
        prato = Prato(
            nome=nome,
            descricao=descricao,
            categoria=categoria,
            rendimento=rendimento,
            unidade_rendimento=unidade_rendimento,
            porcoes_rendimento=int(rendimento),
            tempo_preparo=tempo_preparo,
            margem=margem,
            custo_indireto=random.uniform(2, 10)  # Valor base de custo indireto
        )
        
        db.session.add(prato)
        db.session.flush()  # Para obter o ID do prato
        
        # Adicionar insumos ao prato
        num_insumos = random.randint(3, 8)
        
        # Filtrar produtos por categoria relevante para o tipo de prato
        produtos_relevantes = []
        
        if categoria == 'Entrada':
            categorias_produtos = ['Vegetais', 'Lu00e1cteos', 'Temperos']
        elif categoria == 'Prato Principal':
            categorias_produtos = ['Carnes', 'Vegetais', 'Gru00e3os', 'Temperos']
        elif categoria == 'Sobremesa':
            categorias_produtos = ['Lu00e1cteos', 'Temperos']
        else:  # Bebida
            categorias_produtos = ['Bebidas', 'Vegetais']
        
        for p in produtos:
            if p.categoria in categorias_produtos:
                produtos_relevantes.append(p)
        
        if not produtos_relevantes:  # Fallback se nu00e3o encontrar produtos relevantes
            produtos_relevantes = produtos
        
        # Escolher produtos aleatu00f3rios, sem repetir
        produtos_escolhidos = random.sample(produtos_relevantes, min(num_insumos, len(produtos_relevantes)))
        
        for j, produto in enumerate(produtos_escolhidos, 1):
            quantidade = round(random.uniform(0.1, 2), 2)
            obrigatorio = random.random() > 0.2  # 80% su00e3o obrigatu00f3rios
            
            insumo = PratoInsumo(
                prato_id=prato.id,
                produto_id=produto.id,
                quantidade=quantidade,
                ordem=j,
                obrigatorio=obrigatorio,
                observacao=fake.sentence() if random.random() > 0.7 else None
            )
            
            db.session.add(insumo)
        
        # Calcular e atualizar o preu00e7o sugerido
        db.session.flush()
        prato.atualizar_preco_sugerido()
        
        pratos.append(prato)
    
    db.session.commit()
    return pratos

def crear_cardapios(quantidade, pratos):
    """Cria cardu00e1pios de exemplo com seu00e7u00f5es e itens"""
    from app.models.modelo_cardapio import Cardapio, CardapioSecao, CardapioItem
    from datetime import date, timedelta
    
    cardapios = []
    
    # Tipos de cardu00e1pios e temporadas
    tipos_cardapios = ['Diu00e1rio', 'Semanal', 'Executivo', 'Especial', 'Eventos']
    temporadas = ['Normal', 'Veru00e3o', 'Inverno', 'Natal', 'Pu00e1scoa', 'Festival Gastronômico']
    nomes_secoes = {
        'Entrada': ['Entradas Frias', 'Entradas Quentes', 'Aperitivos', 'Saladas'],
        'Prato Principal': ['Carnes', 'Aves', 'Peixes', 'Massas', 'Risotos', 'Vegetarianos'],
        'Sobremesa': ['Sobremesas', 'Doces', 'Frutas', 'Gelados'],
        'Bebida': ['Bebidas', 'Vinhos', 'Cervejas', 'Drinks', 'Nu00e3o Alcoólicos']
    }
    
    # Agrupar pratos por categoria para usar depois
    pratos_por_categoria = {}
    for prato in pratos:
        categoria = prato.categoria or 'Sem Categoria'
        if categoria not in pratos_por_categoria:
            pratos_por_categoria[categoria] = []
        pratos_por_categoria[categoria].append(prato)
    
    for i in range(quantidade):
        # Gerar dados do cardu00e1pio
        tipo = random.choice(tipos_cardapios)
        temporada = random.choice(temporadas)
        data_inicio = date.today() - timedelta(days=random.randint(0, 30))
        data_fim = data_inicio + timedelta(days=random.randint(30, 180)) if random.random() > 0.3 else None
        
        nome = f"Cardu00e1pio {tipo} - {temporada}"
        if temporada == 'Normal':
            nome = f"Cardu00e1pio {tipo} {i+1}"
        
        # Criar o cardu00e1pio
        cardapio = Cardapio(
            nome=nome,
            descricao=fake.paragraph(nb_sentences=2),
            tipo=tipo,
            temporada=temporada,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=True
        )
        
        db.session.add(cardapio)
        db.session.flush()  # Para obter o ID do cardu00e1pio
        
        # Criar seu00e7u00f5es com base nas categorias de pratos
        secoes_criadas = {}
        
        for categoria, lista_pratos in pratos_por_categoria.items():
            if not lista_pratos:
                continue
            
            # Escolher nomes de seções para esta categoria
            if categoria in nomes_secoes and nomes_secoes[categoria]:
                nomes_possiveis = nomes_secoes[categoria]
                nome_secao = random.choice(nomes_possiveis)
            else:
                nome_secao = categoria
            
            # Criar a seu00e7u00e3o
            secao = CardapioSecao(
                cardapio_id=cardapio.id,
                nome=nome_secao,
                descricao=f"Seu00e7u00e3o de {nome_secao.lower()}",
                ordem=len(secoes_criadas) + 1  # Sua ordem na exibiçãu00e3o
            )
            
            db.session.add(secao)
            db.session.flush()  # Para obter o ID da seu00e7u00e3o
            
            secoes_criadas[categoria] = secao
            
            # Adicionar itens u00e0 seu00e7u00e3o
            itens_adicionados = 0
            
            # Escolher alguns pratos (nãu00e3o todos) para esta seu00e7u00e3o
            max_itens = min(len(lista_pratos), 5)  # No máximo 5 itens por seu00e7u00e3o
            pratos_para_adicionar = random.sample(lista_pratos, max_itens)
            
            for j, prato in enumerate(pratos_para_adicionar, 1):
                # Decidir se terá  preu00e7o especial ou vai usar o preu00e7o do prato
                preco_especial = None
                if random.random() > 0.7 and prato.preco_venda:  # 30% chance de ter preu00e7o especial
                    variacao = random.uniform(0.9, 1.2)  # 10% menos ou 20% mais
                    preco_especial = float(prato.preco_venda) * variacao
                
                item = CardapioItem(
                    secao_id=secao.id,
                    prato_id=prato.id,
                    preco_venda=preco_especial,
                    ordem=j,
                    destaque=random.random() > 0.8,  # 20% chance de ser destaque
                    disponivel=random.random() > 0.1,  # 90% chance de estar disponível
                    observacao=fake.sentence() if random.random() > 0.7 else None
                )
                
                db.session.add(item)
                itens_adicionados += 1
        
        cardapios.append(cardapio)
    
    db.session.commit()
    return cardapios

if __name__ == '__main__':
    import sys
    
    resultados = seed_database()
    print("\nResumo:")
    for key, value in resultados.items():
        print(f"  - {key.capitalize()}: {value}")
