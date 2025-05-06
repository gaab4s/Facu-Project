import psycopg2
import tkinter as tk
from tkinter import messagebox

# Configurações de conexão
host = "localhost"
user = "postgres"
password = ""
port = "5432"

# Verifica se o banco 'Escola_tentando' existe, se não, cria
def garantir_banco():
    try:
        conexao = psycopg2.connect(
            host=host, user=user, password=password, port=port, dbname='postgres'
        )
        conexao.set_session(autocommit=True)
        cursor = conexao.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'Escola_tentando';")
        existe = cursor.fetchone()
        if not existe:
            cursor.execute("CREATE DATABASE Escola_tentando;")
            print("Banco 'Escola_tentando' criado com sucesso.")
        else:
            print("Banco 'Escola_tentando' já existe.")
    except psycopg2.Error as erro:
        print("Erro ao verificar/criar banco:", erro)
        messagebox.showerror("Erro", f"Erro ao verificar/criar banco:\n{erro}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()

def pesquisar_aluno():
    nome = entry_nome.get()
    materia = entry_materia.get()
    try:
        matricula = int(entry_matricula.get())
        if not (1 <= matricula <= 30):
            messagebox.showwarning("Aviso", "A matrícula deve ser um número entre 1 e 30.")
            return
    except ValueError:
        messagebox.showwarning("Aviso", "A matrícula deve ser um número.")
        return
    try:
        turma = int(entry_turma.get())
    except ValueError:
        messagebox.showwarning("Aviso", "A turma deve ser um número.")
        return
    if not nome or not materia:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    garantir_banco()
    try:
        conexao = psycopg2.connect(
            host=host, user=user, password=password, port=port, dbname='Escola_tentando'
        )
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                matricula INTEGER,
                nome VARCHAR(100),
                turma INTEGER,
                materia VARCHAR(100),
                PRIMARY KEY (matricula, turma)
            );
        """)
        cursor.execute("""
            INSERT INTO alunos (matricula, nome, turma, materia)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (matricula, turma) DO NOTHING;
        """, (matricula, nome, turma, materia))
        if cursor.rowcount == 0:
            messagebox.showinfo("Aviso", "Aluno já cadastrado com essa matrícula e turma.")
        else:
            conexao.commit()
            messagebox.showinfo("Sucesso", "Dados inseridos com sucesso!")
    except Exception as erro:
        messagebox.showerror("Erro", f"Erro ao inserir dados: {erro}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()

def listar_alunos():
    try:
        turma = int(entry_turma.get())
    except ValueError:
        messagebox.showwarning("Aviso", "Informe um número válido de turma para listar.")
        return
    try:
        conexao = psycopg2.connect(
            host=host, user=user, password=password, port=port, dbname='Escola_tentando'
        )
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT matricula, nome, materia FROM alunos
            WHERE turma = %s ORDER BY matricula;
        """, (turma,))
        alunos = cursor.fetchall()
        if not alunos:
            messagebox.showinfo("Resultado", f"Nenhum aluno encontrado para a turma {turma}.")
            return
        janela_resultado = tk.Toplevel()
        janela_resultado.title(f"Alunos da Turma {turma}")
        text = tk.Text(janela_resultado, width=50, height=15)
        text.pack(padx=10, pady=10)
        text.insert(tk.END, f"Alunos da turma {turma}:\n\n")
        for matricula, nome, materia in alunos:
            text.insert(tk.END, f"Matrícula: {matricula} | Nome: {nome} | Matéria: {materia}\n")
        text.config(state=tk.DISABLED)
    except Exception as erro:
        messagebox.showerror("Erro", f"Erro ao buscar alunos: {erro}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()

def inserir_nota():
    try:
        matricula = int(entry_matricula.get())
        turma = int(entry_turma.get())
        materia = entry_materia.get()
        nota = float(entry_nota.get())
    except ValueError:
        messagebox.showwarning("Aviso", "Preencha todos os campos corretamente.")
        return
    garantir_banco()
    try:
        conexao = psycopg2.connect(
            host=host, user=user, password=password, port=port, dbname='Escola_tentando'
        )
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas (
                matricula INTEGER,
                turma INTEGER,
                materia VARCHAR(100),
                nota NUMERIC(4,2),
                PRIMARY KEY (matricula, turma, materia),
                FOREIGN KEY (matricula, turma) REFERENCES alunos(matricula, turma)
            );
        """)
        cursor.execute("""
            INSERT INTO notas (matricula, turma, materia, nota)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (matricula, turma, materia)
            DO UPDATE SET nota = EXCLUDED.nota;
        """, (matricula, turma, materia, nota))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Nota inserida/atualizada com sucesso!")
    except Exception as erro:
        messagebox.showerror("Erro", f"Erro ao inserir nota: {erro}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()

def pesquisar_nota():
    try:
        matricula = int(entry_matricula.get())
        turma = int(entry_turma.get())
        materia = entry_materia.get()
    except ValueError:
        messagebox.showwarning("Aviso", "Preencha matrícula, turma e matéria corretamente.")
        return
    garantir_banco()
    try:
        conexao = psycopg2.connect(
            host=host, user=user, password=password, port=port, dbname='Escola_tentando'
        )
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT nota FROM notas
            WHERE matricula = %s AND turma = %s AND materia = %s;
        """, (matricula, turma, materia))
        resultado = cursor.fetchone()
        if resultado:
            messagebox.showinfo("Nota", f"Nota do aluno: {resultado[0]}")
        else:
            messagebox.showinfo("Nota", "Nota não encontrada para esse aluno/matéria.")
    except Exception as erro:
        messagebox.showerror("Erro", f"Erro ao pesquisar nota: {erro}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()

# ----- Interface gráfica -----
janela = tk.Tk()
janela.title("Cadastro de Aluno")

tk.Label(janela, text="Matrícula (1-30):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
entry_matricula = tk.Entry(janela)
entry_matricula.grid(row=0, column=1)

tk.Label(janela, text="Turma (número):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
entry_turma = tk.Entry(janela)
entry_turma.grid(row=1, column=1)

tk.Label(janela, text="Matéria:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
entry_materia = tk.Entry(janela)
entry_materia.grid(row=2, column=1)

tk.Label(janela, text="Nome:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
entry_nome = tk.Entry(janela)
entry_nome.grid(row=3, column=1)

tk.Label(janela, text="Nota:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
entry_nota = tk.Entry(janela)
entry_nota.grid(row=4, column=1)

botao_pesquisar = tk.Button(janela, text="Salvar Aluno", command=pesquisar_aluno)
botao_pesquisar.grid(row=5, column=0, columnspan=2, pady=10)

botao_listar = tk.Button(janela, text="Listar Alunos da Turma", command=listar_alunos)
botao_listar.grid(row=6, column=0, columnspan=2, pady=5)

botao_nota = tk.Button(janela, text="Inserir Nota", command=inserir_nota)
botao_nota.grid(row=7, column=0, columnspan=2, pady=5)

botao_pesquisar_nota = tk.Button(janela, text="Pesquisar Nota", command=pesquisar_nota)
botao_pesquisar_nota.grid(row=8, column=0, columnspan=2, pady=5)

janela.mainloop()