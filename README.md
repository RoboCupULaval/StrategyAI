[![Travis Build Status](https://travis-ci.org/RoboCupULaval/StrategyAI.svg?branch=dev)](https://travis-ci.org/RoboCupULaval/StrategyAI)

# StrategyAI

Toute contribution au code est sous [la licence libre MIT](https://opensource.org/licenses/mit-license.php).

### Information générale
Ce dépôt regroupe les différents outils utilisés pour élaborer
l'intelligence artificielle de Robocup ULaval.


L'implémentation de l'intelligence artificielle est basée sur
la STA, dont le papier de recherche se retrouve
[dans le dépôt Admin de l'équipe IA](https://github.com/RoboCupULaval/Admin/blob/master/documentation/white_paper_stp.pdf).


### Installation
To install all including all the tools (referee, simulator, ui and autoref):
```bash
sudo apt-get install python3
mkdir -p ~/robocup/ultron
cd !$ && git clone https://github.com/RoboCupULaval/StrategyAI.git
cd StrategyAI/
python3 install_all.sh
```

### Workflow Git
Le dépôt StrategyAI fonctionne avec les pull requests:
* Chaque nouvelle feature/issue doit être sur sa propre branche (git checkout -b branch_name).
* Une fois qu'une feature/issue est résolue, faire un pull-request.

### Standard de code
Pour que le code soit considéré comme valide, celui-ci doit respecter le standard de code [PEP-8](https://www.python.org/dev/peps/pep-0008/).
De plus, le code doit avoir les tests unitaires associés.

### Exemple pour lancer deux équipes:
À modifier selon vos chemins, à lancer à partir de la racine du dépôt de StrategyAI. Ce fichier est disponible à la racine du dépôt sous le nom de dual_launch.sh

>#!/bin/bash
>
>#start ai blue
>
>python main.py config/sim.cfg | python main.py config/sim_yellow.cfg | python ../UI-Debug/main.py config/field/sim.cfg blue | python ../UI-Debug/main.py config/field/sim.cfg yellow
