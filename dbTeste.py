import mysql.connector
from mysql.connector import Error
import socket
import time


def testar_conexao_mysql(host, database, user, password, port=3306):
    """
    Testa a conexão com o banco de dados MySQL e retorna um diagnóstico detalhado

    Args:
        host (str): Endereço do servidor MySQL
        database (str): Nome do banco de dados
        user (str): Nome de usuário
        password (str): Senha
        port (int): Porta (padrão 3306)

    Returns:
        dict: Dicionário com resultados do teste e sugestões
    """
    resultado = {
        'status_geral': 'FALHA',
        'etapas': [],
        'sugestoes': []
    }

    # Etapa 1: Verificar resolução DNS e conectividade com o host
    try:
        start_time = time.time()
        socket.gethostbyname(host)
        latency = (time.time() - start_time) * 1000
        resultado['etapas'].append({
            'nome': 'Resolução DNS e ping',
            'status': 'SUCESSO',
            'detalhes': f'Host resolvido com latência de {latency:.2f} ms'
        })
    except socket.gaierror:
        resultado['etapas'].append({
            'nome': 'Resolução DNS e ping',
            'status': 'FALHA',
            'detalhes': 'Não foi possível resolver o nome do host'
        })
        resultado['sugestoes'].append('Verifique o nome do host e sua conexão com a internet')
        return resultado

    # Etapa 2: Tentar conexão sem especificar o banco de dados
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        conn.close()
        resultado['etapas'].append({
            'nome': 'Conexão básica ao servidor',
            'status': 'SUCESSO',
            'detalhes': 'Credenciais válidas para conectar ao servidor MySQL'
        })
    except Error as e:
        resultado['etapas'].append({
            'nome': 'Conexão básica ao servidor',
            'status': 'FALHA',
            'detalhes': str(e)
        })
        if "Access denied" in str(e):
            resultado['sugestoes'].append('Verifique usuário e senha')
            resultado['sugestoes'].append('Confira se o usuário tem permissão para conectar do seu IP')
        elif "Can't connect" in str(e):
            resultado['sugestoes'].append('Verifique se o servidor MySQL está rodando')
            resultado['sugestoes'].append('Confira a porta e se há firewall bloqueando')
        return resultado

    # Etapa 3: Verificar se o banco de dados existe
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )
        conn.close()
        resultado['etapas'].append({
            'nome': 'Acesso ao banco específico',
            'status': 'SUCESSO',
            'detalhes': f'Banco de dados "{database}" acessível'
        })
    except Error as e:
        resultado['etapas'].append({
            'nome': 'Acesso ao banco específico',
            'status': 'FALHA',
            'detalhes': str(e)
        })
        if "Unknown database" in str(e):
            resultado['sugestoes'].append(f'O banco de dados "{database}" não existe')
            resultado['sugestoes'].append('Crie o banco de dados ou verifique o nome')
        elif "Access denied" in str(e):
            resultado['sugestoes'].append(f'O usuário não tem permissão para acessar o banco "{database}"')
        return resultado

    # Etapa 4: Verificar permissões básicas
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )
        cursor = conn.cursor()

        # Testar SELECT
        cursor.execute("SHOW TABLES")
        cursor.fetchall()

        # Testar INSERT (usando tabela temporária)
        cursor.execute("CREATE TEMPORARY TABLE test_perm (id INT)")
        cursor.execute("INSERT INTO test_perm VALUES (1)")
        cursor.execute("DROP TEMPORARY TABLE test_perm")

        conn.close()
        resultado['etapas'].append({
            'nome': 'Permissões básicas',
            'status': 'SUCESSO',
            'detalhes': 'Usuário tem permissões SELECT, INSERT, CREATE TEMPORARY TABLE'
        })
    except Error as e:
        resultado['etapas'].append({
            'nome': 'Permissões básicas',
            'status': 'FALHA',
            'detalhes': str(e)
        })
        resultado['sugestoes'].append('O usuário não tem todas as permissões necessárias')
        return resultado

    # Se chegou até aqui, todas as etapas foram bem sucedidas
    resultado['status_geral'] = 'SUCESSO'
    return resultado


# Função para exibir os resultados de forma amigável
def exibir_resultado_teste(resultado):
    print("\n=== RESULTADO DO TESTE DE CONEXÃO ===")
    print(f"Status Geral: {resultado['status_geral']}\n")

    print("--- Etapas do Teste ---")
    for etapa in resultado['etapas']:
        print(f"{etapa['nome']}: {etapa['status']}")
        print(f"  Detalhes: {etapa['detalhes']}\n")

    if resultado['sugestoes']:
        print("--- Sugestões para Resolver Problemas ---")
        for i, sugestao in enumerate(resultado['sugestoes'], 1):
            print(f"{i}. {sugestao}")


# Exemplo de uso:
if __name__ == "__main__":
    print("Testando conexão com o banco de dados...")

    # Substitua com suas credenciais reais
    teste = testar_conexao_mysql(
        host='162.241.2.230',
        database='dougl947_DeltaGo',
        user='dougl947_user2',
        password='a#=d,F*No6)'
    )

    exibir_resultado_teste(teste)