# Alunos: Douglas Lima Menezes (552590), Francisco Wandallis (553083) e Milena de Santiago Maia Costa (552981).

import time
import itertools
import random
from pysat.solvers import Glucose3

TAMANHO_GRADE = 3
ESTADO_FINAL = (0, 1, 2, 3, 4, 5, 6, 7, 8)
ACOES_MOVIMENTO = {"CIMA": (-1, 0), "BAIXO": (1, 0), "ESQUERDA": (0, -1), "DIREITA": (0, 1)}

def estado_inicial_valido(num_embaralhamentos=50):
    tabuleiro = list(ESTADO_FINAL)
    ultimo_movimento = None


    for _ in range(num_embaralhamentos):
        idx_vazio = tabuleiro.index(0)
        linha_vazio, col_vazio = idx_vazio // TAMANHO_GRADE, idx_vazio % TAMANHO_GRADE
        
        movimentos_possiveis = []
        for nome_acao, (dr, dc) in ACOES_MOVIMENTO.items():
            if ultimo_movimento and ACOES_MOVIMENTO.get(ultimo_movimento) == (-dr, -dc):
                continue
            
            if 0 <= linha_vazio + dr < TAMANHO_GRADE and 0 <= col_vazio + dc < TAMANHO_GRADE:
                movimentos_possiveis.append(nome_acao)
        
        if not movimentos_possiveis:
            continue

        movimento_escolhido = random.choice(movimentos_possiveis)
        dr, dc = ACOES_MOVIMENTO[movimento_escolhido]
        
        linha_vizinho, col_vizinho = linha_vazio + dr, col_vazio + dc
        idx_vizinho = linha_vizinho * TAMANHO_GRADE + col_vizinho
        
        tabuleiro[idx_vazio], tabuleiro[idx_vizinho] = tabuleiro[idx_vizinho], tabuleiro[idx_vazio]
        ultimo_movimento = movimento_escolhido
    
    return tuple(tabuleiro)


class SolverPuzzle8SAT:
    def __init__(self, estado_inicial):
        self.estado_inicial = estado_inicial
        self.estado_final = ESTADO_FINAL
        self.tamanho_grade = TAMANHO_GRADE
        self.acoes = ACOES_MOVIMENTO
        self.simbolo_para_int = {}
        self.int_para_simbolo = {}

    def coords_para_indice(self, linha, col):
        return linha * self.tamanho_grade + col

    def indice_para_coords(self, indice):
        return indice // self.tamanho_grade, indice % self.tamanho_grade

    def gerar_variaveis_proposicionais(self, max_passos):
        contador_var = 1

        for t in range(max_passos + 1):
            for r in range(self.tamanho_grade):
                for c in range(self.tamanho_grade):
                    for v in range(9):
                        simbolo = f"{t}_P_{r}_{c}_{v}"
                        self.simbolo_para_int[simbolo] = contador_var
                        self.int_para_simbolo[contador_var] = simbolo
                        contador_var += 1

        for t in range(max_passos):
            for acao in self.acoes:
                simbolo = f"{t}_A_{acao}"
                self.simbolo_para_int[simbolo] = contador_var
                self.int_para_simbolo[contador_var] = simbolo
                contador_var += 1

        return self.simbolo_para_int, self.int_para_simbolo

    def gerar_clausula_estado_inicial(self, vars_map):
        clausulas = []
        for i, valor_peca in enumerate(self.estado_inicial):
            linha, col = self.indice_para_coords(i)
            clausulas.append([vars_map[f"0_P_{linha}_{col}_{valor_peca}"]])
        return clausulas

    def gerar_clausula_estado_final(self, vars_map, max_passos):
        clausulas = []
        for i, valor_peca in enumerate(self.estado_final):
            linha, col = self.indice_para_coords(i)
            clausulas.append([vars_map[f"{max_passos}_P_{linha}_{col}_{valor_peca}"]])
        return clausulas


    def gerar_clausulas_regras_basicas(self, vars_map, max_passos):
        clausulas = []
        posicoes = list(range(self.tamanho_grade * self.tamanho_grade))
        
        for t in range(max_passos + 1):
            for r in range(self.tamanho_grade):
                for c in range(self.tamanho_grade):
                    clausulas.append([vars_map[f"{t}_P_{r}_{c}_{v}"] for v in range(9)])
                    for v1, v2 in itertools.combinations(range(9), 2):
                        clausulas.append([-vars_map[f"{t}_P_{r}_{c}_{v1}"], -vars_map[f"{t}_P_{r}_{c}_{v2}"]])

            for v in range(9):
                clausulas.append([vars_map[f"{t}_P_{self.indice_para_coords(i)[0]}_{self.indice_para_coords(i)[1]}_{v}"] for i in posicoes])
                for i1, i2 in itertools.combinations(posicoes, 2):
                    r1, c1 = self.indice_para_coords(i1)
                    r2, c2 = self.indice_para_coords(i2)
                    clausulas.append([-vars_map[f"{t}_P_{r1}_{c1}_{v}"], -vars_map[f"{t}_P_{r2}_{c2}_{v}"]])
        return clausulas


    def gerar_clausulas_regras_acao(self, vars_map, max_passos):
        clausulas = []
        nomes_acoes = list(self.acoes.keys())
        for t in range(max_passos):
            clausulas.append([vars_map[f"{t}_A_{acao}"] for acao in nomes_acoes])
            for acao1, acao2 in itertools.combinations(nomes_acoes, 2):
                clausulas.append([-vars_map[f"{t}_A_{acao1}"], -vars_map[f"{t}_A_{acao2}"]])
        return clausulas


    def gerar_clausulas_transicao(self, vars_map, max_passos):
        clausulas = []
        for t in range(max_passos):
            for r0 in range(self.tamanho_grade):
                for c0 in range(self.tamanho_grade):
                    for nome_acao, (dr, dc) in self.acoes.items():
                        premissa = [-vars_map[f"{t}_P_{r0}_{c0}_0"], -vars_map[f"{t}_A_{nome_acao}"]]
                        
                        r1, c1 = r0 + dr, c0 + dc

                        if 0 <= r1 < self.tamanho_grade and 0 <= c1 < self.tamanho_grade:
                            clausulas.append(premissa + [vars_map[f"{t+1}_P_{r1}_{c1}_0"]])
                            
                            for v in range(1, 9):
                                clausulas.append(premissa + [-vars_map[f"{t}_P_{r1}_{c1}_{v}"], vars_map[f"{t+1}_P_{r0}_{c0}_{v}"]])
                            
                            for r_outra in range(self.tamanho_grade):
                                for c_outra in range(self.tamanho_grade):
                                    if (r_outra, c_outra) != (r0, c0) and (r_outra, c_outra) != (r1, c1):
                                        for v_outra in range(1, 9):
                                            clausulas.append(premissa + [-vars_map[f"{t}_P_{r_outra}_{c_outra}_{v_outra}"], vars_map[f"{t+1}_P_{r_outra}_{c_outra}_{v_outra}"]])
                        else:
                            for r_repete in range(self.tamanho_grade):
                                for c_repete in range(self.tamanho_grade):
                                    for v_repete in range(9):
                                        clausulas.append(premissa + [-vars_map[f"{t}_P_{r_repete}_{c_repete}_{v_repete}"], vars_map[f"{t+1}_P_{r_repete}_{c_repete}_{v_repete}"]])
        return clausulas


    def resolver(self, max_passos):
        self.gerar_variaveis_proposicionais(max_passos)
        vars_map = self.simbolo_para_int
        int_para_simbolo = self.int_para_simbolo
        
        with Glucose3() as solver:
            solver.append_formula(self.gerar_clausula_estado_inicial(vars_map))
            solver.append_formula(self.gerar_clausula_estado_final(vars_map, max_passos))
            solver.append_formula(self.gerar_clausulas_regras_basicas(vars_map, max_passos))
            solver.append_formula(self.gerar_clausulas_regras_acao(vars_map, max_passos))
            solver.append_formula(self.gerar_clausulas_transicao(vars_map, max_passos))
            
            if solver.solve():
                modelo = solver.get_model()
                return self.extrair_solucao(modelo, int_para_simbolo, max_passos)
            else:
                return None, None


    def extrair_solucao(self, modelo, int_para_simbolo, max_passos):
        caminho_tabuleiros = []
        variaveis_verdadeiras = {p for p in modelo if p > 0}
        
        for t in range(max_passos + 1):
            tabuleiro_passo_t = [[-1] * self.tamanho_grade for _ in range(self.tamanho_grade)]
            for var_int in variaveis_verdadeiras:
                simbolo = int_para_simbolo.get(var_int)
                if simbolo and simbolo.startswith(f"{t}_P_"):
                    _, _, r, c, v = simbolo.split("_")
                    tabuleiro_passo_t[int(r)][int(c)] = int(v)
            caminho_tabuleiros.append(tabuleiro_passo_t)

        lista_acoes = [""] * max_passos
        for var_int in variaveis_verdadeiras:
            simbolo = int_para_simbolo.get(var_int)
            if simbolo and "_A_" in simbolo:
                t, _, nome_acao = simbolo.split("_")
                if int(t) < len(lista_acoes):
                    lista_acoes[int(t)] = nome_acao
        
        return caminho_tabuleiros, lista_acoes

    def imprimir_tabuleiro(self, tabuleiro_matriz):
        for linha in tabuleiro_matriz:
            print(" ".join(str(p) for p in linha))

    def solucao_completa(self, caminho_solucao, acoes):
        for i, tabuleiro in enumerate(caminho_solucao):
            print(f"\nPASSO {i}:")
            self.imprimir_tabuleiro(tabuleiro)
            if i < len(acoes) and acoes[i]:
                print(f"Acao a ser executada: Mover para {acoes[i]}")

                print("mapeamento do estado atual:")
                #adicionanado o mapeamento do estado atual
                for r in range(self.tamanho_grade):
                    for c in range(self.tamanho_grade):
                        valor = tabuleiro[r][c]
                        simbolo = f"{i}_P_{r}_{c}_{valor}"
                        if simbolo in self.simbolo_para_int:
                            print(f"{simbolo} -> {self.simbolo_para_int[simbolo]}")

if __name__ == "__main__":
    estado_inicial_gerado = estado_inicial_valido(num_embaralhamentos=50)
    
    tabuleiro_inicial_matriz = [list(estado_inicial_gerado[i:i+3]) for i in range(0, 9, 3)]
    tabuleiro_final_matriz = [list(ESTADO_FINAL[i:i+3]) for i in range(0, 9, 3)]


    print("--- CONFIGURACAO DO 8-PUZZLE ---")
    print("\nEstado Inicial Gerado:")
    SolverPuzzle8SAT(estado_inicial_gerado).imprimir_tabuleiro(tabuleiro_inicial_matriz)

    print("\nObjetivo do Estado Final:")
    SolverPuzzle8SAT(estado_inicial_gerado).imprimir_tabuleiro(tabuleiro_final_matriz)
    print("-------------------------------------------\n")

    puzzle_solver = SolverPuzzle8SAT(estado_inicial_gerado)
    
    tempo_inicio_busca = time.time()
    for num_passos in itertools.count(1):
        print(f"Buscando solucao em {num_passos} passo(s)...")
        caminho, acoes = puzzle_solver.resolver(num_passos)
        
        if caminho:
            tempo_fim_busca = time.time()
            print("\n===========================================")
            print(f"-> SOLUCAO ENCONTRADA EM {num_passos} PASSOS! <-")
            print(f"-> Tempo total de busca: {tempo_fim_busca - tempo_inicio_busca:.2f} segundos.")
            print("\n===========================================")
            
            puzzle_solver.solucao_completa(caminho, acoes)
            break