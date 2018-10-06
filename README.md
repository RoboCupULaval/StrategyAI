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
Pour install ultron et tous les outils (referee, simulator, ui and autoref):
```bash
sudo apt-get install curl git
sh -c "$(curl -fsSL https://raw.githubusercontent.com/RoboCupULaval/StrategyAI/dev/tools/install_from_scratch.sh)"
```

### Workflow Git
Le dépôt StrategyAI fonctionne avec les pull requests:
* Chaque nouvelle feature/issue doit être sur sa propre branche (git checkout -b branch_name).
* Une fois qu'une feature/issue est résolue, faire un pull-request.

### Standard de code
Pour que le code soit considéré comme valide, celui-ci doit respecter le standard de code [PEP-8](https://www.python.org/dev/peps/pep-0008/).
De plus, le code doit avoir les tests unitaires associés.

### Emplacements des logiciels
- `~/robocup/tools`
    - `grSim/`: Simulateur, peut-être lancer via la commande `grsim`
    - `ssl-refbox/`: Logiciel de Referee, pour le lancer `cd ~/robocup/tools/ssl-refbox && ./sslrefbox`
- `~/robocup/ultron`
    - `StrategyAI/`: Back-end, pour lancer voir plus bas
    - `UI-Debug/`: Front-end, pour lancer voir plus bas

### Exemple pour lancer deux équipes:
À modifier selon vos chemins, à lancer à partir de la racine du dépôt de StrategyAI. Ce fichier est disponible à la racine du dépôt sous le nom de dual_launch.sh

```bash
source ~/robocup/ultron/virtualenv/bin/activate
bash ./dual_launch_two_ui.sh
```