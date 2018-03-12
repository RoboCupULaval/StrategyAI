[![Travis Build Status](https://travis-ci.org/RoboCupULaval/StrategyIA.svg?branch=dev)](https://travis-ci.org/RoboCupULaval/StrategyIA)

# StrategyIA

Toute contribution au code est sous [la licence libre MIT](https://opensource.org/licenses/mit-license.php).

### Information générale
Ce dépôt regroupe les différents outils utilisés pour élaborer
l'intelligence artificielle de Robocup ULaval.


L'implémentation de l'intelligence artificielle est basée sur
la STA, dont le papier de recherche se retrouve
[dans le dépôt Admin de l'équipe IA](https://github.com/RoboCupULaval/Admin/blob/master/documentation/white_paper_stp.pdf).


### Installation
Pour les détails d'installations voir le fichier INSTALLATION.md

### Workflow Git
Le dépôt StrategyIA fonctionne avec les forks et les pull requests.
* Pour travailler sur le dépôt en général, il faut que ce soit sur un fork de la branche dev de StrategyIA.
* Chaque nouvelle feature/issue doit être sur sa propre branche.
* Une fois qu'une feature/issue est résolue, faire un pull-request.

### Standard de code
Pour que le code soit considéré comme valide, celui-ci doit respecter le standard de code [PEP-8](https://www.python.org/dev/peps/pep-0008/).
De plus, le code doit avoir les tests unitaires associés ainsi que les docstring pour respecter le standard de code [PEP-257](https://www.python.org/dev/peps/pep-0257/).

### Exemple pour lancer deux équipes:
À modifier selon vos chemins, à lancer à partir de la racine du dépôt de StrategyIA. Ce fichier est disponible à la racine du dépôt sous le nom de dual_launch.sh

>#!/bin/bash
>
>#start ai blue
>
>python main.py config/sim.cfg | python main.py config/sim_yellow.cfg | python ../UI-Debug/main.py config/field/sim.cfg blue | python ../UI-Debug/main.py config/field/sim.cfg yellow
