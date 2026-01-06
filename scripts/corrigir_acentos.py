#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import codecs
from pathlib import Path

# Diretório base dos templates
TEMPLATE_DIR = Path('/home/dan/Documentos/AleroPrice/app/templates')

# Padrão para encontrar sequências como "u00e1" que representam acentos codificados incorretamente
PADRAO_UNICODE_ESCAPE = re.compile(r'u00([a-f0-9]{2})')

# Mapeamento de códigos comuns para caracteres acentuados
MAPEAMENTO_ACENTOS = {
    'u00e1': 'á',  # á
    'u00e0': 'à',  # à
    'u00e2': 'â',  # â
    'u00e3': 'ã',  # ã
    'u00e4': 'ä',  # ä
    'u00c1': 'Á',  # Á
    'u00c0': 'À',  # À
    'u00c2': 'Â',  # Â
    'u00c3': 'Ã',  # Ã
    'u00c4': 'Ä',  # Ä
    'u00e9': 'é',  # é
    'u00e8': 'è',  # è
    'u00ea': 'ê',  # ê
    'u00eb': 'ë',  # ë
    'u00c9': 'É',  # É
    'u00c8': 'È',  # È
    'u00ca': 'Ê',  # Ê
    'u00cb': 'Ë',  # Ë
    'u00ed': 'í',  # í
    'u00ec': 'ì',  # ì
    'u00ee': 'î',  # î
    'u00ef': 'ï',  # ï
    'u00cd': 'Í',  # Í
    'u00cc': 'Ì',  # Ì
    'u00ce': 'Î',  # Î
    'u00cf': 'Ï',  # Ï
    'u00f3': 'ó',  # ó
    'u00f2': 'ò',  # ò
    'u00f4': 'ô',  # ô
    'u00f5': 'õ',  # õ
    'u00f6': 'ö',  # ö
    'u00d3': 'Ó',  # Ó
    'u00d2': 'Ò',  # Ò
    'u00d4': 'Ô',  # Ô
    'u00d5': 'Õ',  # Õ
    'u00d6': 'Ö',  # Ö
    'u00fa': 'ú',  # ú
    'u00f9': 'ù',  # ù
    'u00fb': 'û',  # û
    'u00fc': 'ü',  # ü
    'u00da': 'Ú',  # Ú
    'u00d9': 'Ù',  # Ù
    'u00db': 'Û',  # Û
    'u00dc': 'Ü',  # Ü
    'u00e7': 'ç',  # ç
    'u00c7': 'Ç',  # Ç
    'u00f1': 'ñ',  # ñ
    'u00d1': 'Ñ',  # Ñ
}

def corrigir_texto(texto):
    """Corrige códigos de escape unicode no texto para caracteres acentuados"""
    for codigo, caractere in MAPEAMENTO_ACENTOS.items():
        texto = texto.replace(codigo, caractere)
    return texto

def corrigir_arquivo(caminho):
    """Corrige os acentos em um arquivo de template"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verifica se há códigos de escape para corrigir
        conteudo_corrigido = corrigir_texto(conteudo)
        
        if conteudo != conteudo_corrigido:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo_corrigido)
            print(f"Corrigido: {caminho}")
            return True
        else:
            print(f"Sem alterações: {caminho}")
            return False
    except Exception as e:
        print(f"Erro ao processar {caminho}: {e}")
        return False

def corrigir_todos_templates():
    """Corrige todos os arquivos de template no diretório"""
    total_arquivos = 0
    arquivos_corrigidos = 0
    
    for pasta_atual, _, arquivos in os.walk(TEMPLATE_DIR):
        for arquivo in arquivos:
            if arquivo.endswith('.html'):
                caminho_completo = os.path.join(pasta_atual, arquivo)
                total_arquivos += 1
                if corrigir_arquivo(caminho_completo):
                    arquivos_corrigidos += 1
    
    print(f"\nProcessamento concluído!")
    print(f"Total de arquivos: {total_arquivos}")
    print(f"Arquivos corrigidos: {arquivos_corrigidos}")

if __name__ == "__main__":
    print("Iniciando correção de acentos nos templates...\n")
    corrigir_todos_templates()
