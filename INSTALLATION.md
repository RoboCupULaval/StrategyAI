# INSTALLATION

### Cloner le dépôt

Télécharger le dépôt sur son ordinateur pour pouvoir travailler
dessus.

1. Downloader et installer [git](https://git-scm.com/downloads)
2. Cloner le dépôt (le télécharger sur son ordinateur avec les liens vers le dépôt en ligne)
    1. ouvrir un terminal/command prompt
    2. naviguer vers le dossier où vous désirez mettre les fichiers
    3. executer la commande `git clone https://github.com/robocupulaval/strategyia.git`
3. Naviguer jusqu'au dossier nouvellement télécharger
4. Changer de branch pour aller vers la branche "dev" avec la commande `git checkout dev`

### Installer python

Installer le language de programmation qui sert à faire rouler l'IA

1. Downloader et installer [python](https://www.python.org/downloads/) 3.5+
2. Donloader et installer le manager de packages de python
 [pip](https://pypi.python.org/pypi/pip) s'il ne s'est pas installer avec python

### Installer les dépendances

Dans un terminal se trouvant dans le dossier StrategyIA/ run the command:
```
pip install -e requirements.txt
```