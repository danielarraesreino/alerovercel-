#!/usr/bin/env python
"""
Script para executar todos os testes do projeto AleroPrice

Este script permite executar testes por tipo (unit, integration, e2e)
ou todos os testes de uma vez.
"""

import os
import sys
import argparse
import subprocess

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Execute testes do AleroPrice')
    parser.add_argument('--unit', action='store_true', help='Executar apenas testes de unidade')
    parser.add_argument('--integration', action='store_true', help='Executar apenas testes de integração')
    parser.add_argument('--e2e', action='store_true', help='Executar apenas testes end-to-end')
    parser.add_argument('--database', action='store_true', help='Executar apenas testes de banco de dados')
    parser.add_argument('--html', action='store_true', help='Gerar relatório HTML dos resultados')
    parser.add_argument('--coverage', action='store_true', help='Gerar relatório de cobertura de código')
    return parser.parse_args()

def run_unit_tests(html=False, coverage=False):
    """Execute unit tests"""
    print("\n\033[1m\033[94mExecutando testes de unidade...\033[0m")
    cmd = ["pytest", "tests/unit", "-v"]
    
    if html:
        cmd.extend(["--html=reports/unit_tests_report.html", "--self-contained-html"])
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html:reports/coverage/unit"])
    
    return subprocess.run(cmd).returncode

def run_integration_tests(html=False, coverage=False):
    """Execute integration tests"""
    print("\n\033[1m\033[94mExecutando testes de integração...\033[0m")
    cmd = ["pytest", "tests/integration", "-v"]
    
    if html:
        cmd.extend(["--html=reports/integration_tests_report.html", "--self-contained-html"])
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html:reports/coverage/integration"])
    
    return subprocess.run(cmd).returncode

def run_e2e_tests(html=False):
    """Execute end-to-end tests"""
    print("\n\033[1m\033[94mExecutando testes end-to-end...\033[0m")
    cmd = ["pytest", "tests/e2e", "-v"]
    
    if html:
        cmd.extend(["--html=reports/e2e_tests_report.html", "--self-contained-html"])
    
    return subprocess.run(cmd).returncode

def run_database_tests(html=False, coverage=False):
    """Execute database tests"""
    print("\n\033[1m\033[94mExecutando testes de banco de dados...\033[0m")
    cmd = ["pytest", "tests/unit/test_database.py", "-v"]
    
    if html:
        cmd.extend(["--html=reports/database_tests_report.html", "--self-contained-html"])
    if coverage:
        cmd.extend(["--cov=app.models", "--cov-report=term", "--cov-report=html:reports/coverage/database"])
    
    return subprocess.run(cmd).returncode

def run_all_tests(html=False, coverage=False):
    """Execute all tests"""
    print("\n\033[1m\033[93mExecutando todos os testes do projeto...\033[0m")
    results = []
    
    # Ensure reports directory exists
    os.makedirs("reports/coverage", exist_ok=True)
    
    results.append(run_unit_tests(html, coverage))
    results.append(run_integration_tests(html, coverage))
    results.append(run_database_tests(html, coverage))
    results.append(run_e2e_tests(html))
    
    return max(results)  # Return the highest exit code (non-zero indicates failure)

def main():
    """Main function"""
    args = parse_args()
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    if not any([args.unit, args.integration, args.e2e, args.database]):
        # If no specific test type is specified, run all tests
        return run_all_tests(args.html, args.coverage)
    
    results = []
    
    if args.unit:
        results.append(run_unit_tests(args.html, args.coverage))
    
    if args.integration:
        results.append(run_integration_tests(args.html, args.coverage))
    
    if args.e2e:
        results.append(run_e2e_tests(args.html))
    
    if args.database:
        results.append(run_database_tests(args.html, args.coverage))
    
    return max(results)  # Return the highest exit code (non-zero indicates failure)

if __name__ == '__main__':
    sys.exit(main())
