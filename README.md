# StrategyIA
### Comment cloner le dépot
1. « Forker » le dépôt StrategyIA, s'assurer que l'on est bien sur la branche `dev`.
2. Cloner le dépôt, créer une branche et aller sur celle-ci avec les commandes:
```
git clone https://github.com/nom_de_votre_identifiant/StrategyIA.git
git checkout dev
git branch 
git checkout nom_du_issue_sur_lequel_je_travail/sous_section_si_issue_trop_vague
```

### Workflow Git
Le dépôt StrategyIA fonctionne avec les forks et les pull requests.
* Pour travailler sur le dépôt en général, il faut que ce soit sur un fork de la branche dev de StrategyIA.
* Chaque nouvelle feature/issue doit être sur sa propre branche.
* Une fois qu'une feature/issue est résolue, faire un pull-request.

### Standard de code
Pour que le code soit considéré comme valide, celui-ci doit respecter le santdard de code *PEP-8*.
**Un code non standardisé est considéré comme non-fonctionnel, et se verra refuser le pull request.**
