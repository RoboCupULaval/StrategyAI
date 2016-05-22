[![Build Status](https://drone.io/github.com/RoboCupULaval/StrategyIA/status.png)](https://drone.io/github.com/RoboCupULaval/StrategyIA/latest)

# StrategyIA

Toute contribution au code est sous [la licence libre MIT](https://opensource.org/licenses/mit-license.php).

### Information générale
Ce dépôt regroupe les différents outils utilisés pour élaborer l'intelligence artificielle de Robocup ULaval.
UltimateStratedy.py est un exemple d'implémentation de l'intelligence artificielle.

L'implémentation de l'intelligence artificielle est basée sur la STA, dont le papier de recherche se retrouve [dans le dépôt Admin de l'équipe IA](https://github.com/RoboCupULaval/Admin/blob/master/documentation/white_paper_stp.pdf).

### Comment cloner le dépot
1. « Forker » le dépôt StrategyIA, s'assurer que l'on est bien sur la branche `dev`.
2. Cloner le dépôt, créer une branche et aller sur celle-ci avec les commandes:
```
git clone https://github.com/nom_de_votre_identifiant/StrategyIA.git
git checkout dev
git branch nom_du_issue_sur_lequel_je_travail/sous_section_si_issue_trop_vague
git checkout nom_du_issue_sur_lequel_je_travail/sous_section_si_issue_trop_vague
```

### Workflow Git
Le dépôt StrategyIA fonctionne avec les forks et les pull requests.
* Pour travailler sur le dépôt en général, il faut que ce soit sur un fork de la branche dev de StrategyIA.
* Chaque nouvelle feature/issue doit être sur sa propre branche.
* Une fois qu'une feature/issue est résolue, faire un pull-request.

### Standard de code
Pour que le code soit considéré comme valide, celui-ci doit respecter le standard de code [PEP-8](https://www.python.org/dev/peps/pep-0008/).
De plus, le code doit avoir les tests unitaires associés ainsi que les docstring pour respecter le standard de code [PEP-257](https://www.python.org/dev/peps/pep-0257/).
#####**Un code non standardisé est considéré comme non-fonctionnel, et se verra refuser le pull request.**
