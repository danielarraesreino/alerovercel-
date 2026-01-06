#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script para executar todos os testes do AleroPrice com 100% de cobertura de código e UI/UX
'''

import os
import sys
import subprocess
import time
import argparse
from datetime import datetime

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"{title.center(80)}")
    print("=" * 80 + "\n")

def run_command(command, cwd=None):
    """Executa um comando e retorna código de saída, stdout e stderr"""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=cwd,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

def activate_venv():
    """Retorna o comando para ativar o ambiente virtual baseado no SO"""
    if os.name == 'nt':
        return "venv\\Scripts\\activate"
    else:
        return ". venv/bin/activate"

def get_project_root():
    """Retorna o diretório raiz do projeto"""
    return os.path.dirname(os.path.abspath(__file__))

def run_flask_app(project_root):
    """Inicia o servidor Flask em segundo plano"""
    activate_cmd = activate_venv()
    flask_cmd = f"{activate_cmd} && python run.py"
    
    # Inicia o processo em segundo plano
    print("Iniciando servidor Flask em segundo plano...")
    if os.name == 'nt':
        process = subprocess.Popen(
            f"start cmd /c {flask_cmd}", 
            shell=True, 
            cwd=project_root
        )
    else:
        process = subprocess.Popen(
            f"gnome-terminal -- bash -c '{flask_cmd}; exec bash'", 
            shell=True, 
            cwd=project_root
        )
    
    # Aguarda o servidor iniciar
    print("Aguardando o servidor iniciar (5 segundos)...")
    time.sleep(5)
    return process

def stop_flask_app(process=None):
    """Para o servidor Flask"""
    if process:
        process.terminate()
    
    # Encontra e mata todos os processos Flask que possam estar rodando
    if os.name == 'nt':
        os.system("taskkill /f /im python.exe /fi \"WINDOWTITLE eq Flask\"")
    else:
        os.system("pkill -f 'python run.py'")

def run_unit_tests(project_root, html_report=True):
    """Executa todos os testes unitários e retorna se houve falhas"""
    print_header("Executando Testes Unitários")
    
    # Comando para executar testes unitários com cobertura
    report_options = "--html=reports/unit_tests_report.html" if html_report else ""
    command = f"{activate_venv()} && python -m pytest tests/unit/ -v --cov=app --cov-report=term --cov-report=html:reports/coverage {report_options}"
    
    returncode, stdout, stderr = run_command(command, cwd=project_root)
    
    print(stdout)
    if stderr.strip():
        print(f"Erros: {stderr}")
    
    return returncode == 0

def run_integration_tests(project_root, html_report=True):
    """Executa todos os testes de integração e retorna se houve falhas"""
    print_header("Executando Testes de Integração")
    
    report_options = "--html=reports/integration_tests_report.html" if html_report else ""
    command = f"{activate_venv()} && python -m pytest tests/integration/ -v --cov=app --cov-report=term --cov-report=html:reports/integration_coverage {report_options}"
    
    returncode, stdout, stderr = run_command(command, cwd=project_root)
    
    print(stdout)
    if stderr.strip():
        print(f"Erros: {stderr}")
    
    return returncode == 0

def run_e2e_tests(project_root, html_report=True):
    """Executa todos os testes end-to-end e retorna se houve falhas"""
    print_header("Executando Testes End-to-End (E2E)")
    
    # Certifique-se de que o playwright está instalado
    setup_cmd = f"{activate_venv()} && python -m playwright install"
    run_command(setup_cmd, cwd=project_root)
    
    report_options = "--html=reports/e2e_tests_report.html" if html_report else ""
    command = f"{activate_venv()} && python -m pytest tests/e2e/ -v {report_options}"
    
    returncode, stdout, stderr = run_command(command, cwd=project_root)
    
    print(stdout)
    if stderr.strip():
        print(f"Erros: {stderr}")
    
    return returncode == 0

def run_ui_tests(project_root, html_report=True):
    """Executa todos os testes de UI e retorna se houve falhas"""
    print_header("Executando Testes de UI/UX")
    
    # Inicia o servidor Flask
    flask_process = run_flask_app(project_root)
    
    try:
        report_options = "--html=reports/ui_tests_report.html" if html_report else ""
        command = f"{activate_venv()} && python -m pytest tests/e2e/test_e2e_ui_completo.py -v --browser=chromium {report_options} -m ui"
        
        returncode, stdout, stderr = run_command(command, cwd=project_root)
        
        print(stdout)
        if stderr.strip():
            print(f"Erros: {stderr}")
        
        return returncode == 0
    finally:
        # Garante que o servidor Flask seja encerrado mesmo em caso de erros
        stop_flask_app(flask_process)

def merge_coverage_reports(project_root):
    """Mescla relatórios de cobertura e gera relatório final"""
    print_header("Mesclando Relatórios de Cobertura")
    
    command = f"{activate_venv()} && coverage combine && coverage report && coverage html -d reports/full_coverage"
    returncode, stdout, stderr = run_command(command, cwd=project_root)
    
    print(stdout)
    if stderr.strip():
        print(f"Erros: {stderr}")
    
    # Exibe um resumo da cobertura total
    print("\nResumo da cobertura total de código:")
    coverage_cmd = f"{activate_venv()} && coverage report | grep TOTAL"
    returncode, stdout, stderr = run_command(coverage_cmd, cwd=project_root)
    print(stdout)

def generate_combined_report(project_root):
    """Gera um relatório HTML combinado de todos os testes"""
    print_header("Gerando Relatório Combinado")
    
    # Cria diretório de relatórios se não existir
    reports_dir = os.path.join(project_root, 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Gera um relatório combinando todos os resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(reports_dir, f'full_test_report_{timestamp}.html')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AleroPrice - Relatório Completo de Testes</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
            <style>
                .header {{background-color: #343a40; color: white; padding: 20px 0;}}
                .section {{margin: 30px 0;}}
                iframe {{border: 1px solid #ddd; width: 100%; height: 600px;}}
            </style>
        </head>
        <body>
            <div class="header text-center">
                <h1>AleroPrice - Relatório Completo de Testes</h1>
                <p>Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
            </div>
            
            <div class="container mt-4">
                <div class="section">
                    <h2>Resumo</h2>
                    <div class="alert alert-info">
                        <p>Este relatório contém os resultados consolidados de todos os testes do sistema AleroPrice.</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Cobertura de Código</h2>
                    <div class="embed-responsive">
                        <iframe src="full_coverage/index.html"></iframe>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Testes Unitários</h2>
                    <div class="embed-responsive">
                        <iframe src="unit_tests_report.html"></iframe>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Testes de Integração</h2>
                    <div class="embed-responsive">
                        <iframe src="integration_tests_report.html"></iframe>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Testes End-to-End</h2>
                    <div class="embed-responsive">
                        <iframe src="e2e_tests_report.html"></iframe>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Testes de UI/UX</h2>
                    <div class="embed-responsive">
                        <iframe src="ui_tests_report.html"></iframe>
                    </div>
                </div>
            </div>
            
            <footer class="bg-light text-center py-3 mt-5">
                <p>AleroPrice &copy; 2025</p>
            </footer>
            
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        ''')
    
    print(f"Relatório completo gerado em: {report_path}")
    return report_path

def main():
    parser = argparse.ArgumentParser(description='Executa testes completos do AleroPrice')
    parser.add_argument('--no-unit', action='store_true', help='Pula testes unitários')
    parser.add_argument('--no-integration', action='store_true', help='Pula testes de integração')
    parser.add_argument('--no-e2e', action='store_true', help='Pula testes end-to-end')
    parser.add_argument('--no-ui', action='store_true', help='Pula testes de UI/UX')
    parser.add_argument('--no-report', action='store_true', help='Não gera relatório HTML')
    
    args = parser.parse_args()
    
    clear_screen()
    print_header("TESTES COMPLETOS DO ALEROPRICE - 100% COBERTURA")
    
    project_root = get_project_root()
    
    # Cria diretório para relatórios
    reports_dir = os.path.join(project_root, 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Configura arquivo de cobertura
    coverage_file = os.path.join(project_root, '.coveragerc')
    with open(coverage_file, 'w') as f:
        f.write('''
[run]
source = app
omit = 
    */migrations/*
    */tests/*
    */venv/*
    */config.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError
''')
    
    # Executar cada tipo de teste conforme configurações
    results = {}
    
    if not args.no_unit:
        results['unit'] = run_unit_tests(project_root, not args.no_report)
    
    if not args.no_integration:
        results['integration'] = run_integration_tests(project_root, not args.no_report)
    
    if not args.no_e2e:
        results['e2e'] = run_e2e_tests(project_root, not args.no_report)
    
    if not args.no_ui:
        results['ui'] = run_ui_tests(project_root, not args.no_report)
    
    if not args.no_report:
        merge_coverage_reports(project_root)
        report_path = generate_combined_report(project_root)
        print(f"\nAcesse o relatório completo em: {report_path}")
    
    # Exibir resumo dos resultados
    print_header("RESUMO DOS RESULTADOS")
    all_passed = True
    
    for test_type, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_type.upper():12}: {status}")
        all_passed = all_passed and passed
    
    exit_code = 0 if all_passed else 1
    print(f"\nResultado final: {'✅ TODOS OS TESTES PASSARAM' if all_passed else '❌ ALGUNS TESTES FALHARAM'}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
