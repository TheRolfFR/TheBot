# Création du Bot Discord de l'UTBiscord

###### tags: `discord` `bot` `open-source` `python` 

## :memo: Informations :

### Quel language ?

Le python, simple et efficace sera utilisé.

### Qui peut participer ?

Toutes les personnes présentes sur le Discord UTBiscord.

### Principales fonctionnalitées à implémenter:
- [ ] Modération
- [ ] Attribution des rôles de jeux
- [ ] Musique
- [ ] Strawpoll
- [ ] Traducteur


# Linux

## :wrench: Dépendances système

- virtualenv
- python3.5


## :wrench: Installation du projet

```
git clone https://github.com/UTBiscord/bot-discord.git
cd bot-discord

virtualenv --system-site-packages --python=python3 env
source env/bin/activate

pip install -r requirements.txt

```

## :wrench: Démarage du projet

```
source env/bin/activate
python DISCORD_TOKER="entrez le token juste ici" bot.py

```

# Windows

La version sans le support de la voix:
```
py -3-m pip install -U discord.py

```
La version avec le support de voix:

```
py -3-m pip install -U discord.py[voice] 
```

- plus d'info ici: https://pypi.org/project/discord.py/  
- vidéo tutoriel (EN) : https://youtu.be/5yahh4tR0L0
