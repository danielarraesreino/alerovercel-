import xmltodict
import json
import os

file_path = '/home/dan/Área de Trabalho/AleroPrice/nf e/NFe35250407374789000190550010000848211154644503-procnfe.xml'

try:
    with open(file_path, 'rb') as f:
        xml_content = f.read()
    
    # Simulate app usage
    # FIX: Map namespace to None to strip it from keys
    ns_map = {'http://www.portalfiscal.inf.br/nfe': None}
    xml_dict = xmltodict.parse(xml_content, process_namespaces=True, namespaces=ns_map)
    
    print("KEYS LEVEL 1:", list(xml_dict.keys()))
    
    def buscar_chave(dados, chave):
        if isinstance(dados, dict):
            for k, v in dados.items():
                if k == chave:
                    return v # Found!
                if isinstance(v, (dict, list)):
                    res = buscar_chave(v, chave)
                    if res: return res
        elif isinstance(dados, list):
            for item in dados:
                res = buscar_chave(item, chave)
                if res: return res
        return None

    inf_nfe = buscar_chave(xml_dict, 'infNFe')
    if inf_nfe:
        print("infNFe FOUND!")
        # Print a summary of what's inside to verify
        print("infNFe keys:", list(inf_nfe.keys()))
    else:
        print("infNFe NOT FOUND via recursive search.")
        # Print full dict structure depth 3
        print(json.dumps(xml_dict, indent=2, default=str))

except Exception as e:
    print(f"Error: {e}")
