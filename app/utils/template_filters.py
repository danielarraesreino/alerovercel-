# -*- coding: utf-8 -*-

from app.utils.formatacao_br import (
    formatar_moeda, 
    formatar_peso, 
    formatar_percentual,
    formatar_data,
    formatar_numero
)

def registrar_filtros(app):
    """
    Registra os filtros personalizados do template para o Flask
    """
    @app.template_filter('moeda_br')
    def moeda_br_filter(valor):
        return formatar_moeda(valor)
    
    @app.template_filter('peso_br')
    def peso_br_filter(valor, unidade='kg'):
        return formatar_peso(valor, unidade)
    
    @app.template_filter('percentual_br')
    def percentual_br_filter(valor):
        return formatar_percentual(valor)
    
    @app.template_filter('data_br')
    def data_br_filter(data, formato='%d/%m/%Y'):
        return formatar_data(data, formato)
    
    @app.template_filter('numero_br')
    def numero_br_filter(valor, decimais=2):
        return formatar_numero(valor, decimais)
