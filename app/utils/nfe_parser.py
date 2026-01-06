import xmltodict
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator

class NFeItemData(BaseModel):
    """Modelo Pydantic para um item de NF-e"""
    num_item: int
    codigo: str
    descricao: str
    unidade: str
    quantidade: float
    valor_unitario: float
    valor_total: float
    ncm: Optional[str] = None
    cfop: Optional[str] = None
    icms_valor: Optional[float] = None
    icms_aliquota: Optional[float] = None
    ipi_valor: Optional[float] = None
    ipi_aliquota: Optional[float] = None

class NFeFornecedorData(BaseModel):
    """Modelo Pydantic para o fornecedor da NF-e"""
    cnpj: str
    razao_social: str
    inscricao_estadual: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    
    @validator('cnpj')
    def cnpj_deve_ser_valido(cls, v):
        # Remove caracteres nu00e3o numu00e9ricos
        v = ''.join(filter(str.isdigit, v))
        
        # Valida tamanho
        if len(v) != 14:
            raise ValueError('CNPJ deve ter 14 du00edgitos')
        
        # Aqui poderia implementar validau00e7u00e3o completa de CNPJ
        # mas simplificamos para o exemplo
        
        return v

class NFeData(BaseModel):
    """Modelo Pydantic para os dados principais da NF-e"""
    chave_acesso: str
    numero: str
    serie: str
    data_emissao: datetime
    valor_produtos: float
    valor_total: float
    valor_frete: Optional[float] = 0
    valor_seguro: Optional[float] = 0
    valor_desconto: Optional[float] = 0
    valor_impostos: Optional[float] = 0
    fornecedor: NFeFornecedorData
    itens: List[NFeItemData]
    
    @validator('chave_acesso')
    def chave_acesso_deve_ser_valida(cls, v):
        # Remove caracteres nu00e3o numu00e9ricos
        v = ''.join(filter(str.isdigit, v))
        
        # Valida tamanho
        if len(v) != 44:
            raise ValueError('Chave de acesso deve ter 44 du00edgitos')
        
        return v

def extrair_dados_nfe(xml_content: str) -> NFeData:
    """Extrai os dados principais de um XML de NF-e
    
    Args:
        xml_content: Conteu00fado do arquivo XML da NF-e
        
    Returns:
        NFeData: Modelo Pydantic com os dados da NF-e
    
    Raises:
        ValueError: Se o XML nu00e3o estiver no formato esperado ou faltar informau00e7u00f5es
    """
    try:
        # Converter XML para dicionu00e1rio
        xml_dict = xmltodict.parse(xml_content)
        
        # Extrair os dados principais da NF-e
        nfe = xml_dict['nfeProc']['NFe']['infNFe']
        
        # Extrair chave de acesso
        chave_acesso = xml_dict['nfeProc']['protNFe']['infProt']['chNFe']
        
        # Informau00e7u00f5es da Nota
        ide = nfe['ide']
        numero = ide['nNF']
        serie = ide['serie']
        data_emissao = datetime.strptime(ide['dhEmi'].split('T')[0], '%Y-%m-%d')
        
        # Informau00e7u00f5es do Fornecedor (Emitente)
        emit = nfe['emit']
        cnpj = emit['CNPJ']
        razao_social = emit['xNome']
        inscricao_estadual = emit.get('IE')
        
        # Endereu00e7o do Fornecedor
        endereco = None
        cidade = None
        estado = None
        if 'enderEmit' in emit:
            end = emit['enderEmit']
            endereco = f"{end.get('xLgr', '')}, {end.get('nro', '')} - {end.get('xBairro', '')}"
            cidade = end.get('xMun')
            estado = end.get('UF')
        
        # Valores Totais
        total = nfe['total']['ICMSTot']
        valor_produtos = float(total['vProd'])
        valor_total = float(total['vNF'])
        valor_frete = float(total.get('vFrete', 0))
        valor_seguro = float(total.get('vSeg', 0))
        valor_desconto = float(total.get('vDesc', 0))
        valor_impostos = float(total.get('vIPI', 0)) + float(total.get('vICMS', 0))
        
        # Criar modelo do fornecedor
        fornecedor_data = NFeFornecedorData(
            cnpj=cnpj,
            razao_social=razao_social,
            inscricao_estadual=inscricao_estadual,
            endereco=endereco,
            cidade=cidade,
            estado=estado
        )
        
        # Itens da Nota
        itens_list = []
        det = nfe['det']
        
        # Se tiver apenas um item, colocu00e1-lo numa lista
        if isinstance(det, dict):
            det = [det]
        
        for item in det:
            num_item = int(item['@nItem'])
            prod = item['prod']
            
            # Extrair informau00e7u00f5es fiscais (ICMS, IPI)
            icms_valor = None
            icms_aliquota = None
            ipi_valor = None
            ipi_aliquota = None
            
            if 'imposto' in item:
                if 'ICMS' in item['imposto']:
                    for _, icms_data in item['imposto']['ICMS'].items():
                        if isinstance(icms_data, dict):
                            icms_valor = float(icms_data.get('vICMS', 0))
                            icms_aliquota = float(icms_data.get('pICMS', 0))
                            break
                
                if 'IPI' in item['imposto']:
                    for _, ipi_data in item['imposto']['IPI'].items():
                        if isinstance(ipi_data, dict):
                            ipi_valor = float(ipi_data.get('vIPI', 0))
                            ipi_aliquota = float(ipi_data.get('pIPI', 0))
                            break
            
            # Criar modelo do item
            item_data = NFeItemData(
                num_item=num_item,
                codigo=prod['cProd'],
                descricao=prod['xProd'],
                unidade=prod['uCom'],
                quantidade=float(prod['qCom']),
                valor_unitario=float(prod['vUnCom']),
                valor_total=float(prod['vProd']),
                ncm=prod.get('NCM'),
                cfop=prod.get('CFOP'),
                icms_valor=icms_valor,
                icms_aliquota=icms_aliquota,
                ipi_valor=ipi_valor,
                ipi_aliquota=ipi_aliquota
            )
            
            itens_list.append(item_data)
        
        # Criar modelo completo da NF-e
        nfe_data = NFeData(
            chave_acesso=chave_acesso,
            numero=numero,
            serie=serie,
            data_emissao=data_emissao,
            valor_produtos=valor_produtos,
            valor_total=valor_total,
            valor_frete=valor_frete,
            valor_seguro=valor_seguro,
            valor_desconto=valor_desconto,
            valor_impostos=valor_impostos,
            fornecedor=fornecedor_data,
            itens=itens_list
        )
        
        return nfe_data
        
    except Exception as e:
        raise ValueError(f"Erro ao processar XML da NF-e: {str(e)}")
