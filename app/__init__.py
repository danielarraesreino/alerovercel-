# -*- coding: utf-8 -*-

from flask import Flask
from app.config import config
from app.extensions import db, migrate
import locale

def create_app(config_name='default'):
    """
    Factory para criação da aplicação Flask
    :param config_name: Nome da configuração a ser usada
    :return: Instância da aplicação Flask
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configura a localização brasileira
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
            except locale.Error:
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
                except locale.Error:
                    app.logger.warning('Não foi possível configurar locale brasileiro. Usando padrão do sistema.')
                    pass
    
    # Registra os filtros de template para formatação brasileira
    from app.utils.template_filters import registrar_filtros
    registrar_filtros(app)
    
    # Registra os blueprints
    from app.routes.estoque import bp as estoque_bp
    from app.routes.fornecedores import bp as fornecedores_bp
    from app.routes.nfe import bp as nfe_bp
    from app.routes.pratos import bp as pratos_bp
    from app.routes.produtos import bp as produtos_bp
    from app.routes.cardapios import bp as cardapios_bp
    from app.routes.desperdicio import bp as desperdicio_bp
    from app.routes.previsao import bp as previsao_bp
    from app.routes.dashboard import bp as dashboard_bp
    
    app.register_blueprint(estoque_bp, url_prefix='/estoque')
    app.register_blueprint(fornecedores_bp, url_prefix='/fornecedores')
    app.register_blueprint(nfe_bp, url_prefix='/nfe')
    app.register_blueprint(pratos_bp, url_prefix='/pratos')
    app.register_blueprint(produtos_bp, url_prefix='/produtos')
    app.register_blueprint(cardapios_bp, url_prefix='/cardapios')
    app.register_blueprint(desperdicio_bp, url_prefix='/desperdicio')
    app.register_blueprint(previsao_bp, url_prefix='/previsao')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    
    # Registra o blueprint de erro (opcional)
    # from app.errors import bp as errors_bp
    # app.register_blueprint(errors_bp)
    
    # Registra shell context
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'migrate': migrate}
    
    return app
