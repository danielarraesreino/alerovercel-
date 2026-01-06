from flask import Blueprint, request, jsonify, render_template
from app.utils.nfe_importer import importar_nfe_xml
from app.models.modelo_nfe import NFNota
from app.extensions import db
import logging

bp = Blueprint('nfe', __name__)

@bp.route('/importar', methods=['GET', 'POST'])
def importar_nfe():
    if request.method == 'GET':
        return render_template('nfe/importar.html')
    
    # Log para debug
    logging.info(f"Recebendo requisição POST em /nfe/importar")
    logging.info(f"Content-Type: {request.content_type}")
    logging.info(f"Content-Length: {request.content_length}")
    
    try:
        xml_content = request.get_data(as_text=True)
        if not xml_content:
            logging.error("Nenhum XML fornecido")
            return jsonify({'error': 'Nenhum XML fornecido'}), 400
            
        logging.info("Processando XML...")
        nota, mensagens = importar_nfe_xml(xml_content)
        logging.info(f"Nota processada com sucesso: {nota.numero}/{nota.serie}")
        
        return jsonify({
            'success': True,
            'nota': {
                'id': nota.id,
                'numero': nota.numero,
                'serie': nota.serie,
                'data_emissao': nota.data_emissao.isoformat(),
                'valor_total': float(nota.valor_total),
                'fornecedor': nota.fornecedor.razao_social
            },
            'mensagens': mensagens
        })
        
    except ValueError as e:
        logging.error(f"Erro de validação: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Erro interno: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@bp.route('/listar', methods=['GET'])
def listar_nfes():
    """
    Lista todas as notas fiscais importadas.
    """
    try:
        notas = NFNota.query.order_by(NFNota.data_emissao.desc()).all()
        
        return jsonify({
            'success': True,
            'notas': [{
                'id': nota.id,
                'numero': nota.numero,
                'serie': nota.serie,
                'data_emissao': nota.data_emissao.isoformat(),
                'valor_total': float(nota.valor_total),
                'fornecedor': nota.fornecedor.razao_social
            } for nota in notas]
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@bp.route('/<int:nota_id>', methods=['GET'])
def obter_nfe(nota_id):
    """
    Obtém detalhes de uma nota fiscal específica.
    """
    try:
        nota = NFNota.query.get_or_404(nota_id)
        
        return jsonify({
            'success': True,
            'nota': {
                'id': nota.id,
                'numero': nota.numero,
                'serie': nota.serie,
                'data_emissao': nota.data_emissao.isoformat(),
                'valor_total': float(nota.valor_total),
                'valor_produtos': float(nota.valor_produtos),
                'valor_frete': float(nota.valor_frete),
                'valor_seguro': float(nota.valor_seguro),
                'valor_desconto': float(nota.valor_desconto),
                'valor_impostos': float(nota.valor_impostos),
                'fornecedor': {
                    'id': nota.fornecedor.id,
                    'razao_social': nota.fornecedor.razao_social,
                    'cnpj': nota.fornecedor.cnpj_formatado
                },
                'itens': [{
                    'id': item.id,
                    'produto': item.produto.nome,
                    'quantidade': float(item.quantidade),
                    'valor_unitario': float(item.valor_unitario),
                    'valor_total': float(item.valor_total),
                    'unidade_medida': item.unidade_medida
                } for item in nota.itens]
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500 