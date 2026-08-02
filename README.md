# ReRoute Engine

Solver C++ di riassegnazione risorse sotto shock: invece di ricalcolare
l'intero problema ad ogni disruzione (come il sistema di crew scheduling
"SkySolver" di Southwest Airlines, collassato nel dicembre 2022 dopo circa
300 riassegnazioni), ripara solo il sottoinsieme di risorse/task coinvolti.
Il tempo di risposta resta quindi legato alla scala della disruzione, non
alla scala dell'intero problema.

Il modello dati è volutamente generico: "Resource" può essere un membro di
equipaggio, un lavoratore di magazzino, uno slot di banchina; "Task" un
volo, un turno, una finestra di arrivo camion. La demo usa lo scheduling
equipaggi come narrativa perché è l'incidente reale più riconoscibile.

## Struttura

```
reroute-engine/
├── build.bat / build.sh    compila ed esegue in un passo (Windows / Unix)
├── CMakeLists.txt
├── media/make_media.py     rigenera i grafici della submission da results.json
├── src/
│   ├── types.hpp           Resource, Task, Assignment, DisruptionEvent
│   ├── data_generator.*    dataset sintetico + ondata di disruzioni
│   ├── solver.*            IncrementalSolver: assegnazione greedy + riparazione locale
│   ├── baseline.*          NaiveBaseline: ricalcolo completo ad ogni evento (il "prima")
│   ├── metrics.hpp         Timer + scrittore JSON minimale
│   └── main.cpp            orchestrazione: genera dati, simula, scrive results.json
└── dashboard/
    └── index.html          grafico Chart.js incrementale vs naive
```

## Risultati

Dataset: 20.000 risorse, 10.000 task, 8 tag di qualifica. Mediana di 3 run.

| Scala disruzione | Task coinvolti | Incrementale | Naive    | Speedup | Copertura |
|-----------------|---------------|-------------|----------|---------|-----------|
| Piccola         | 100 (1%)      | 13 ms       | 1.807 ms | ~141×   | identica  |
| Media           | 500 (5%)      | 61 ms       | 1.778 ms | ~29×    | identica  |
| Grande          | 1500 (15%)    | 196 ms      | 1.749 ms | ~9×     | identica  |
| Massima demo    | 3000 (30%)    | 444 ms      | 1.808 ms | ~4×     | identica  |

I tempi assoluti variano con l'hardware e il carico della macchina (lo
speedup sulla scala più piccola oscilla tra ~140× e ~160× tra un run e
l'altro); quello che resta stabile è la forma delle due curve.

Il tempo dell'incrementale scala con la disruzione; quello del naive è
sostanzialmente piatto (proporzionale all'intero problema) indipendentemente
da quanti task vengono colpiti. Le due curve convergono quando la disruzione
si avvicina alla dimensione dell'intero problema: è il confine onesto
dell'approccio, che vince sulle disruzioni parziali — cioè su come sono
fatti gli incidenti reali.

Entrambi i solver lasciano scoperti gli stessi 91 task su 10.000 (99,1% di
copertura): il guadagno di velocità non costa nulla in qualità della
soluzione.

## Limiti noti

Espliciti, perché definiscono cosa significano davvero i numeri sopra:

- **Una risorsa copre un solo task.** Non è modellato un equipaggio che
  effettua più tratte non sovrapposte: per questo la demo usa un pool di
  risorse più grande del set di task.
- **Riparazione greedy, non ottima.** Ogni task colpito prende la risorsa
  più economica disponibile in quel momento, senza backtracking né swap con
  task già assegnati. La copertura coincide con la baseline perché anche la
  baseline è greedy: il confronto è tra *architetture*, non una pretesa di
  ottimalità.
- **Vincoli semplificati.** Qualifiche e finestre di disponibilità sono
  applicate; riposi obbligatori, tempi di trasferimento e costi di
  straordinario non ancora.
- **Dati sintetici**, non operativi reali.

## Build & run (sviluppo locale)

Il modo più rapido — uno script che rileva da solo CMake o g++:

```bash
# Windows: doppio click su build.bat, oppure da terminale
build.bat

# Linux / macOS
chmod +x build.sh && ./build.sh
```

Oppure manualmente:

```bash
# Con CMake
cmake -B build -S .
cmake --build build --config Release

# Oppure direttamente con g++ (nessuna dipendenza esterna)
g++ -std=c++17 -O2 -Isrc src/main.cpp src/data_generator.cpp \
    src/solver.cpp src/baseline.cpp -o reroute
./reroute
```

Il binario scrive `results.json` in tutte le posizioni plausibili (radice del
progetto e `dashboard/`), quindi la dashboard lo trova indipendentemente da
dove hai lanciato il programma — non serve copiarlo a mano.

Per visualizzare la dashboard:
```bash
cd dashboard && python3 -m http.server
# poi apri http://localhost:8000
```

---

## Istruzioni per chi riceve lo .zip

Questa sezione descrive passo per passo come compilare il progetto, eseguirlo
e visualizzare la dashboard su un computer che non ha mai visto questo codice.

### Prerequisiti

Serve uno solo dei seguenti compilatori C++17 e Python 3.
Controlla cosa hai già installato aprendo un terminale e provando:

```
g++ --version
python3 --version   (o: python --version)
```

Se entrambi i comandi rispondono con un numero di versione, sei pronto.
In caso contrario:

**Windows**
- Compilatore: installa [MSYS2](https://www.msys2.org/), poi nel terminale MSYS2 esegui:
  ```
  pacman -S mingw-w64-x86_64-gcc
  ```
  Aggiungi `C:\msys64\mingw64\bin` al PATH di sistema se non è già presente.
- Python: scarica da [python.org](https://www.python.org/downloads/) e spunta
  "Add Python to PATH" durante l'installazione.

**macOS**
```bash
xcode-select --install   # installa g++ (clang compatibile)
# Python 3 è già incluso in macOS 12+
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt update && sudo apt install g++ python3
```

### Passaggi

**1. Estrai lo zip**

Estrai la cartella `Hackton1` in un posto a tua scelta, ad esempio il Desktop.
Alla fine avrai la struttura:
```
Desktop/
└── Hackton1/
    └── reroute-engine/
        ├── src/
        ├── dashboard/
        └── ...
```

**2. Apri un terminale nella cartella giusta**

- **Windows**: tasto destro dentro `reroute-engine` → "Apri in Terminale"
  (oppure apri il terminale MSYS2 e naviga con `cd /c/Users/TUO_NOME/Desktop/Hackton1/reroute-engine`)
- **macOS / Linux**: apri Terminale, poi:
  ```bash
  cd ~/Desktop/Hackton1/reroute-engine
  ```

**3. Compila ed esegui**

Il modo più semplice è lo script incluso, che compila e lancia il programma:

```bash
# Windows
build.bat

# macOS / Linux
chmod +x build.sh && ./build.sh
```

Se preferisci farlo a mano:

```bash
g++ -std=c++17 -O2 -Isrc src/main.cpp src/data_generator.cpp \
    src/solver.cpp src/baseline.cpp -o reroute
./reroute      # su Windows: reroute.exe
```

Su Windows (terminale MSYS2/MinGW) il comando di compilazione è identico.
Il compilatore non stampa nulla se va tutto bene.

Vedrai un output simile a:
```
Scale 100 | incremental: 11.4 ms (91 uncovered) | naive: 1784.9 ms (91 uncovered) | speedup: 155.9x
Scale 500 | incremental: 63.6 ms (91 uncovered) | naive: 1775.1 ms (91 uncovered) | speedup: 27.9x
...
results.json written to 2 location(s)
```

I tempi assoluti varieranno in base al tuo hardware; quello che conta è il
rapporto tra le due colonne. Il file `results.json` viene scritto
automaticamente anche dentro `dashboard/`, quindi non devi copiare nulla.

**4. Avvia il server locale**

```bash
cd dashboard
python3 -m http.server
```

Su Windows, se `python3` non viene trovato, prova:
```
python -m http.server
```

Vedrai:
```
Serving HTTP on 0.0.0.0 port 8000 ...
```

**5. Apri la dashboard nel browser**

Vai a: **http://localhost:8000**

Comparirà un grafico con due curve: la linea rossa (naive) resta alta e piatta
al variare della scala della disruzione, quella blu (incrementale) cresce
lentamente e proporzionalmente solo ai task coinvolti.

Per fermare il server premi `Ctrl+C` nel terminale.

---

## Perché questo approccio (per la submission)

- **Technical Execution**: algoritmo di matching reale con struttura dati
  pensata per la riparazione incrementale, non un mock.
  Complessità della riparazione: O(disruzione × risorse_con_qualifica_richiesta),
  contro O(intero_problema) del naive.
- **Originalità**: reinterpreta un incidente reale documentato invece di un
  problema di scheduling generico da manuale.
- **Impatto**: lo stesso motore si applica a crew scheduling, turni di
  magazzino, slot di banchina — qualsiasi dominio con riassegnazione sotto shock.
- **Chiarezza**: la demo mostra un confronto diretto e leggibile (grafico
  tempo di risposta vs scala della disruzione).

## Roadmap

- Local search vincolata (swap via augmenting path o simulated annealing)
  sopra la riparazione greedy, per migliorare la qualità sulle istanze strette
- Più task per risorsa, con rilevamento dei conflitti sulle finestre temporali
- Vincoli di riposo obbligatorio e costi di straordinario
- Riparazione parallela per cluster di disruzione indipendenti

## Fonti

- [2022 Southwest Airlines scheduling crisis — Wikipedia](https://en.wikipedia.org/wiki/2022_Southwest_Airlines_scheduling_crisis)
- [Southwest Airlines and the anatomy of an IT meltdown — The Air Current](https://theaircurrent.com/airlines/southwest-airlines-anatomy-it-meltdown/)
