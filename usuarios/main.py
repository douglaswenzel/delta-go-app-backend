from UserRegistration import UserRegistration

def main():
    db_config = {
        'host': '162.241.2.230',
        'database': 'dougl947_DeltaGo',
        'user': 'dougl947_user2',
        'password': 'a#=d,F*No6)D'
    }

    print("Cadastro de Usuário")
    print("--------------------")

    name = input("Nome: ")
    sobrenome = input("Sobrenome: ")
    tipo = input("Tipo (funcionario, aluno, visitante): ")
    nascimento = input("Data de nascimento (YYYY-MM-DD): ")
    unidade = input("Unidade: ")
    observacoes = input("Observações: ")
    permissao = input("Permissão (1 = LIBERADO /0 = NEGADO: ")

    if tipo == 'funcionario':
        cargo = input("Cargo: ")
        setor = input("Setor: ")
        data_admissao = input("Data de admissão (YYYY-MM-DD): ")
        user_data = {
            'name': name,
            'sobrenome': sobrenome,
            'tipo': tipo,
            'nascimento': nascimento,
            'unidade': unidade,
            'observacoes': observacoes,
            'permissao': permissao,
            'funcionario': {
                'cargo': cargo,
                'setor': setor,
                'data_admissao': data_admissao
            }
        }
    elif tipo == 'aluno':
        matricula = input("Matrícula: ")
        curso = input("Curso: ")
        turma = input("Turma: ")
        user_data = {
            'name': name,
            'sobrenome': sobrenome,
            'tipo': tipo,
            'nascimento': nascimento,
            'unidade': unidade,
            'observacoes': observacoes,
            'permissao': permissao,
            'aluno': {
                'matricula': matricula,
                'curso': curso,
                'turma': turma
            }
        }
    else:
        motivo_visita = input("Motivo da visita: ")
        visitado = input("Visitado: ")
        data_visita = input("Data da visita (YYYY-MM-DD): ")
        user_data = {
            'name': name,
            'sobrenome': sobrenome,
            'tipo': tipo,
            'nascimento': nascimento,
            'unidade': unidade,
            'observacoes': observacoes,
            'permissao': permissao,
            'visitante': {
                'motivo_visita': motivo_visita,
                'visitado': visitado,
                'data_visita': data_visita
            }
        }

    try:
        registration = UserRegistration(db_config)
        user_id = registration.register_user(user_data)
        print(f"Usuário {user_id} registrado com sucesso!")
    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")

if __name__ == "__main__":
    main()