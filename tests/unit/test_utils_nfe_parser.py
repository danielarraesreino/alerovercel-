import pytest
import json
from datetime import datetime
from pydantic import ValidationError

from app.utils.nfe_parser import (
    NFeItemData,
    NFeFornecedorData, 
    NFeData,
    extrair_dados_nfe
)

# XML de exemplo para testes
XML_NFE_EXEMPLO = '''
<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <NFe xmlns="http://www.portalfiscal.inf.br/nfe">
        <infNFe Id="NFe35230507128945000137550010000000011234567890" versao="4.00">
            <ide>
                <cUF>35</cUF>
                <cNF>12345678</cNF>
                <natOp>Venda de mercadoria</natOp>
                <mod>55</mod>
                <serie>1</serie>
                <nNF>000000001</nNF>
                <dhEmi>2023-05-10T10:30:00-03:00</dhEmi>
                <tpNF>1</tpNF>
            </ide>
            <emit>
                <CNPJ>07128945000137</CNPJ>
                <xNome>FORNECEDOR TESTE LTDA</xNome>
                <xFant>FORNECEDOR TESTE</xFant>
                <enderEmit>
                    <xLgr>Rua Exemplo</xLgr>
                    <nro>1234</nro>
                    <xBairro>Centro</xBairro>
                    <cMun>3550308</cMun>
                    <xMun>São Paulo</xMun>
                    <UF>SP</UF>
                    <CEP>01001000</CEP>
                </enderEmit>
                <IE>123456789012</IE>
            </emit>
            <dest>
                <CNPJ>12345678000123</CNPJ>
                <xNome>RESTAURANTE ALERO PRICE LTDA</xNome>
                <enderDest>
                    <xLgr>Avenida Cliente</xLgr>
                    <nro>987</nro>
                    <xBairro>Jardins</xBairro>
                    <cMun>3550308</cMun>
                    <xMun>São Paulo</xMun>
                    <UF>SP</UF>
                    <CEP>04001000</CEP>
                </enderDest>
                <IE>987654321012</IE>
            </dest>
            <det nItem="1">
                <prod>
                    <cProd>001</cProd>
                    <xProd>Arroz Branco 5kg</xProd>
                    <NCM>10063021</NCM>
                    <CFOP>5102</CFOP>
                    <uCom>UN</uCom>
                    <qCom>10.0000</qCom>
                    <vUnCom>20.0000</vUnCom>
                    <vProd>200.00</vProd>
                </prod>
                <imposto>
                    <ICMS>
                        <ICMS00>
                            <orig>0</orig>
                            <CST>00</CST>
                            <modBC>0</modBC>
                            <vBC>200.00</vBC>
                            <pICMS>18.00</pICMS>
                            <vICMS>36.00</vICMS>
                        </ICMS00>
                    </ICMS>
                    <IPI>
                        <cEnq>999</cEnq>
                        <IPINT>
                            <CST>53</CST>
                        </IPINT>
                    </IPI>
                </imposto>
            </det>
            <det nItem="2">
                <prod>
                    <cProd>002</cProd>
                    <xProd>Feijão Carioca 1kg</xProd>
                    <NCM>07133319</NCM>
                    <CFOP>5102</CFOP>
                    <uCom>UN</uCom>
                    <qCom>20.0000</qCom>
                    <vUnCom>8.5000</vUnCom>
                    <vProd>170.00</vProd>
                </prod>
                <imposto>
                    <ICMS>
                        <ICMS00>
                            <orig>0</orig>
                            <CST>00</CST>
                            <modBC>0</modBC>
                            <vBC>170.00</vBC>
                            <pICMS>18.00</pICMS>
                            <vICMS>30.60</vICMS>
                        </ICMS00>
                    </ICMS>
                    <IPI>
                        <cEnq>999</cEnq>
                        <IPINT>
                            <CST>53</CST>
                        </IPINT>
                    </IPI>
                </imposto>
            </det>
            <total>
                <ICMSTot>
                    <vBC>370.00</vBC>
                    <vICMS>66.60</vICMS>
                    <vProd>370.00</vProd>
                    <vFrete>30.00</vFrete>
                    <vSeg>10.00</vSeg>
                    <vDesc>5.00</vDesc>
                    <vII>0.00</vII>
                    <vIPI>0.00</vIPI>
                    <vNF>405.00</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
    <protNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
        <infProt>
            <tpAmb>1</tpAmb>
            <verAplic>SP_NFE_PL_008i2</verAplic>
            <chNFe>35230507128945000137550010000000011234567890</chNFe>
            <dhRecbto>2023-05-10T10:31:15-03:00</dhRecbto>
            <nProt>135230000012345</nProt>
            <digVal>ABC123==</digVal>
            <cStat>100</cStat>
            <xMotivo>Autorizado o uso da NF-e</xMotivo>
        </infProt>
    </protNFe>
</nfeProc>
'''

# Testes para NFeItemData
def test_nfe_item_data_validacao():
    """Testa a validau00e7u00e3o dos dados de item da NF-e"""
    # Caso vru00e1lido
    item = NFeItemData(
        num_item=1,
        codigo="001",
        descricao="Arroz Branco 5kg",
        unidade="UN",
        quantidade=10.0,
        valor_unitario=20.0,
        valor_total=200.0,
        ncm="10063021",
        cfop="5102",
        icms_valor=36.0,
        icms_aliquota=18.0
    )
    
    assert item.num_item == 1
    assert item.codigo == "001"
    assert item.descricao == "Arroz Branco 5kg"
    assert item.quantidade == 10.0
    assert item.valor_total == 200.0
    
    # Caso com valores opcionais omitidos
    item_simples = NFeItemData(
        num_item=2,
        codigo="002",
        descricao="Feiju00e3o Carioca 1kg",
        unidade="UN",
        quantidade=20.0,
        valor_unitario=8.5,
        valor_total=170.0
    )
    
    assert item_simples.num_item == 2
    assert item_simples.ncm is None
    assert item_simples.icms_valor is None

# Testes para NFeFornecedorData
def test_nfe_fornecedor_data_validacao():
    """Testa a validau00e7u00e3o dos dados de fornecedor da NF-e"""
    # Caso vru00e1lido
    fornecedor = NFeFornecedorData(
        cnpj="07.128.945/0001-37",
        razao_social="FORNECEDOR TESTE LTDA",
        inscricao_estadual="123456789012",
        endereco="Rua Exemplo, 1234",
        cidade="Su00e3o Paulo",
        estado="SP"
    )
    
    # Valida que o CNPJ foi normalizado (removidos pontos e traços)
    assert fornecedor.cnpj == "07128945000137"
    assert fornecedor.razao_social == "FORNECEDOR TESTE LTDA"
    
    # Caso com CNPJ invru00e1lido (tamanho incorreto)
    with pytest.raises(ValidationError):
        NFeFornecedorData(
            cnpj="1234567890",  # CNPJ curto demais
            razao_social="FORNECEDOR TESTE LTDA"
        )
    
    # Caso com valores opcionais omitidos
    fornecedor_simples = NFeFornecedorData(
        cnpj="07128945000137",
        razao_social="FORNECEDOR TESTE LTDA"
    )
    
    assert fornecedor_simples.inscricao_estadual is None
    assert fornecedor_simples.endereco is None

# Testes para NFeData
def test_nfe_data_validacao():
    """Testa a validau00e7u00e3o dos dados principais da NF-e"""
    # Criar itens e fornecedor para o teste
    item = NFeItemData(
        num_item=1,
        codigo="001",
        descricao="Arroz Branco 5kg",
        unidade="UN",
        quantidade=10.0,
        valor_unitario=20.0,
        valor_total=200.0
    )
    
    fornecedor = NFeFornecedorData(
        cnpj="07128945000137",
        razao_social="FORNECEDOR TESTE LTDA"
    )
    
    # Caso vru00e1lido
    nfe_data = NFeData(
        chave_acesso="35230507128945000137550010000000011234567890",
        numero="000000001",
        serie="1",
        data_emissao=datetime(2023, 5, 10, 10, 30),
        valor_produtos=200.0,
        valor_total=230.0,
        valor_frete=30.0,
        fornecedor=fornecedor,
        itens=[item]
    )
    
    # Valida que a chave de acesso foi normalizada
    assert nfe_data.chave_acesso == "35230507128945000137550010000000011234567890"
    assert nfe_data.numero == "000000001"
    assert nfe_data.valor_total == 230.0
    assert len(nfe_data.itens) == 1
    
    # Caso com chave de acesso invru00e1lida (tamanho incorreto)
    with pytest.raises(ValidationError):
        NFeData(
            chave_acesso="12345",  # Chave muito curta
            numero="000000001",
            serie="1",
            data_emissao=datetime(2023, 5, 10),
            valor_produtos=200.0,
            valor_total=230.0,
            fornecedor=fornecedor,
            itens=[item]
        )

# Testes para a funu00e7u00e3o extrair_dados_nfe
def test_extrair_dados_nfe():
    """Testa a extreu00e7u00e3o de dados de um XML de NF-e"""
    # Extrair dados do XML de exemplo
    nfe_data = extrair_dados_nfe(XML_NFE_EXEMPLO)
    
    # Verificar dados gerais da NF-e
    assert nfe_data.chave_acesso == "35230507128945000137550010000000011234567890"
    assert nfe_data.numero == "000000001"
    assert nfe_data.serie == "1"
    assert nfe_data.data_emissao.date() == datetime(2023, 5, 10).date()
    assert nfe_data.valor_produtos == 370.0
    assert nfe_data.valor_total == 405.0
    assert nfe_data.valor_frete == 30.0
    assert nfe_data.valor_seguro == 10.0
    assert nfe_data.valor_desconto == 5.0
    
    # Verificar dados do fornecedor
    assert nfe_data.fornecedor.cnpj == "07128945000137"
    assert nfe_data.fornecedor.razao_social == "FORNECEDOR TESTE LTDA"
    assert nfe_data.fornecedor.inscricao_estadual == "123456789012"
    
    # Verificar itens
    assert len(nfe_data.itens) == 2
    
    # Verificar primeiro item
    item1 = nfe_data.itens[0]
    assert item1.num_item == 1
    assert item1.codigo == "001"
    assert item1.descricao == "Arroz Branco 5kg"
    assert item1.unidade == "UN"
    assert item1.quantidade == 10.0
    assert item1.valor_unitario == 20.0
    assert item1.valor_total == 200.0
    assert item1.ncm == "10063021"
    assert item1.cfop == "5102"
    assert item1.icms_valor == 36.0
    assert item1.icms_aliquota == 18.0
    
    # Verificar segundo item
    item2 = nfe_data.itens[1]
    assert item2.num_item == 2
    assert item2.codigo == "002"
    assert item2.descricao == "Feiju00e3o Carioca 1kg"
    assert item2.unidade == "UN"
    assert item2.quantidade == 20.0
    assert item2.valor_unitario == 8.5
    assert item2.valor_total == 170.0

def test_extrair_dados_nfe_xml_invalido():
    """Testa a extreu00e7u00e3o de dados de um XML invru00e1lido"""
    # XML malformado
    xml_invalido = "<nfeProc><NFe><infNFe></infNFe></NFe>"
    
    # Deve lanu00e7ar exceção
    with pytest.raises(Exception):
        extrair_dados_nfe(xml_invalido)
    
    # XML bem formado mas sem os dados necessru00e1rios
    xml_incompleto = '''
    <?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
        <NFe xmlns="http://www.portalfiscal.inf.br/nfe">
            <infNFe Id="NFe123" versao="4.00">
                <ide>
                    <cUF>35</cUF>
                </ide>
            </infNFe>
        </NFe>
    </nfeProc>
    '''
    
    # Deve lanu00e7ar exceção
    with pytest.raises(Exception):
        extrair_dados_nfe(xml_incompleto)
