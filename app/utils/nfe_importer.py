import xml.etree.ElementTree as ET
from datetime import datetime
from app.models.modelo_nfe import NFNota, NFItem
from app.models.modelo_fornecedor import Fornecedor
from app.models.modelo_produto import Produto
from app.extensions import db
import os

def importar_nfe_xml(xml_content, save_xml=True):
    """
    Importa uma NFe a partir do conteúdo XML.
    
    Args:
        xml_content (str): Conteúdo XML da NFe
        save_xml (bool): Se True, salva o XML em um arquivo
        
    Returns:
        tuple: (NFNota, list) - A nota fiscal importada e lista de mensagens
    """
    mensagens = []
    
    try:
        # Parse do XML
        root = ET.fromstring(xml_content)
        
        # Define os namespaces
        nsNFe = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Obtém o elemento NFe
        nfe = root.find('.//nfe:NFe', nsNFe)
        if nfe is None:
            raise ValueError("XML inválido: elemento NFe não encontrado")
            
        infNFe = nfe.find('.//nfe:infNFe', nsNFe)
        if infNFe is None:
            raise ValueError("XML inválido: elemento infNFe não encontrado")
            
        # Extrai dados básicos da nota
        ide = infNFe.find('.//nfe:ide', nsNFe)
        emit = infNFe.find('.//nfe:emit', nsNFe)
        dest = infNFe.find('.//nfe:dest', nsNFe)
        total = infNFe.find('.//nfe:total/nfe:ICMSTot', nsNFe)
        
        # Verifica se a nota já existe
        chave_acesso = infNFe.get('Id').replace('NFe', '')
        nota_existente = NFNota.query.filter_by(chave_acesso=chave_acesso).first()
        if nota_existente:
            return nota_existente, ["Nota fiscal já importada anteriormente"]
            
        # Processa o fornecedor
        cnpj_emitente = emit.find('.//nfe:CNPJ', nsNFe).text
        fornecedor = Fornecedor.query.filter_by(cnpj=cnpj_emitente).first()
        
        if not fornecedor:
            # Cria novo fornecedor
            fornecedor = Fornecedor(
                cnpj=cnpj_emitente,
                razao_social=emit.find('.//nfe:xNome', nsNFe).text,
                nome_fantasia=emit.find('.//nfe:xFant', nsNFe).text,
                endereco=f"{emit.find('.//nfe:enderEmit/nfe:xLgr', nsNFe).text}, {emit.find('.//nfe:enderEmit/nfe:nro', nsNFe).text}",
                cidade=emit.find('.//nfe:enderEmit/nfe:xMun', nsNFe).text,
                estado=emit.find('.//nfe:enderEmit/nfe:UF', nsNFe).text,
                cep=emit.find('.//nfe:enderEmit/nfe:CEP', nsNFe).text,
                telefone=emit.find('.//nfe:enderEmit/nfe:fone', nsNFe).text,
                inscricao_estadual=emit.find('.//nfe:IE', nsNFe).text
            )
            db.session.add(fornecedor)
            mensagens.append(f"Fornecedor {fornecedor.razao_social} cadastrado com sucesso")
        
        # Cria a nota fiscal
        nota = NFNota(
            chave_acesso=chave_acesso,
            numero=ide.find('.//nfe:nNF', nsNFe).text,
            serie=ide.find('.//nfe:serie', nsNFe).text,
            data_emissao=datetime.strptime(ide.find('.//nfe:dhEmi', nsNFe).text, '%Y-%m-%dT%H:%M:%S%z'),
            valor_total=float(total.find('.//nfe:vNF', nsNFe).text),
            valor_produtos=float(total.find('.//nfe:vProd', nsNFe).text),
            valor_frete=float(total.find('.//nfe:vFrete', nsNFe).text or 0),
            valor_seguro=float(total.find('.//nfe:vSeg', nsNFe).text or 0),
            valor_desconto=float(total.find('.//nfe:vDesc', nsNFe).text or 0),
            valor_impostos=float(total.find('.//nfe:vTotTrib', nsNFe).text or 0),
            fornecedor=fornecedor,
            xml_data=xml_content
        )
        
        # Processa os itens
        for det in infNFe.findall('.//nfe:det', nsNFe):
            prod = det.find('.//nfe:prod', nsNFe)
            imposto = det.find('.//nfe:imposto', nsNFe)
            
            # Procura ou cria o produto
            codigo_produto = prod.find('.//nfe:cProd', nsNFe).text
            produto = Produto.query.filter_by(codigo=codigo_produto).first()
            
            if not produto:
                produto = Produto(
                    codigo=codigo_produto,
                    nome=prod.find('.//nfe:xProd', nsNFe).text,
                    fornecedor=fornecedor,
                    unidade_medida=prod.find('.//nfe:uCom', nsNFe).text,
                    ncm=prod.find('.//nfe:NCM', nsNFe).text
                )
                db.session.add(produto)
                mensagens.append(f"Produto {produto.nome} cadastrado com sucesso")
            
            # Cria o item da nota
            item = NFItem(
                nota=nota,
                produto=produto,
                num_item=int(det.get('nItem')),
                quantidade=float(prod.find('.//nfe:qCom', nsNFe).text),
                valor_unitario=float(prod.find('.//nfe:vUnCom', nsNFe).text),
                valor_total=float(prod.find('.//nfe:vProd', nsNFe).text),
                unidade_medida=prod.find('.//nfe:uCom', nsNFe).text,
                cfop=prod.find('.//nfe:CFOP', nsNFe).text,
                ncm=prod.find('.//nfe:NCM', nsNFe).text
            )
            
            # Processa impostos
            icms = imposto.find('.//nfe:ICMS/nfe:ICMS00', nsNFe)
            if icms is not None:
                item.percentual_icms = float(icms.find('.//nfe:pICMS', nsNFe).text or 0)
                item.valor_icms = float(icms.find('.//nfe:vICMS', nsNFe).text or 0)
            
            db.session.add(item)
        
        # Salva o XML se necessário
        if save_xml:
            pasta_notas = 'notas fiscais'
            os.makedirs(pasta_notas, exist_ok=True)
            xml_path = os.path.join(pasta_notas, f'{chave_acesso}.xml')
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            mensagens.append(f"XML salvo em {xml_path}")
        
        # Atualiza o estoque
        nota.atualizar_estoque()
        
        db.session.commit()
        mensagens.append(f"Nota fiscal {nota.numero}/{nota.serie} importada com sucesso")
        
        return nota, mensagens
        
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao importar NFe: {str(e)}") 