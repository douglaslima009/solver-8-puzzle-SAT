import matplotlib.pyplot as plt
from dadoscoletados import TEMPO_DAS_EXECUCOES
import numpy as np

passos = [d["passos"] for d in TEMPO_DAS_EXECUCOES]
tempos_medios = [sum(d["tempos"])/len(d["tempos"]) for d in TEMPO_DAS_EXECUCOES]
cores = ["green" if d["solucao"] else "red" for d in TEMPO_DAS_EXECUCOES]


plt.figure(figsize=(10, 6))
plt.plot(passos, tempos_medios, marker='o', linestyle='-', color='blue', label='Tempo Médio')

for passo, tempo, cor in zip(passos, tempos_medios, cores):
    plt.scatter(passo, tempo, color=cor, s=100, zorder=5)

max_tempo = max(tempos_medios)
plt.ylim(0, max_tempo + (2 - (max_tempo % 2)) if max_tempo % 2 != 0 else max_tempo + 2)
plt.yticks(np.arange(0, plt.ylim()[1], 2.00))


plt.xlabel("Passos Máximos")
plt.ylabel("Tempo (s)")
plt.title("Tempo de Resolução")
plt.grid(True)
plt.legend()

plt.savefig("Gráfico com o tempo de resolução do programa.png")
print("Gráfico salvo como Gráfico com o tempo de resolução do programa.png")