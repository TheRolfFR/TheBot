![TheBot](logo/theBot_200px.png)
# TheBot - Bot Discord de l'UTBiscord

###### tags: `discord` `bot` `open-source` `python`


## 📝 Informations :

### Quel language ?

Le python, simple et efficace sera utilisé.

### Qui peut participer ?

Toutes les personnes présentes sur le Discord UTBiscord.

### Principales fonctionnalitées à implémenter:
- [x] Modération
- [ ] Attribution des rôles de jeux
- [x] Radio
- [ ] Musique
- [ ] Strawpoll
- [ ] Traducteur

## 🔧 Dépendances système

- sqlite
- python 3

## 🔧 Lancer le bot en local

Cloner le dépôt distant :
```
git clone https://github.com/TheRolfFR/TheBot
```

Installer les modules python :
```
pip install -r requirements.txt
```

Récupérer les cookies de YT https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp et les placer à la racine du projet.

Ajouter un fichier token.txt à la racine avec le token du bot à l'intérieur.
Vous avez généré ce token sur le portail [Discord developer].
Vous pouvez créer une application en appuyant sur le bouton ``New application``.
(https://discord.com/developers/applications) dans la section ``🧩 bot`` .
Lancer le bot :
```
python bot.py
```

Évidemment il vous faudra inviter votre bot sur votre serveur. Pour cela récupérez le ``CLIENT ID`` dans la section ``🏠 General information``

Maintenant si vous êtes administrateur de votre serveur, vous pouvez inviter le bot en tapant l'url:

https://discord.com/api/oauth2/authorize?client_id=PASTE_CLIENT_ID_HERE&permissions=32630786&scope=bot

Enjoy!


## 🔧 Lancer le bot sur [repl.it](https://repl.it/) 🙊

Demander à [TheRolfFR](https://bit.ly/therolf-github) aka Réseau

## 📜 Informations et documentation

- Librairie discord python (EN) : https://discordpy.readthedocs.io/en/latest/
- Tutoriel vidéo créer un bot discord avec python (EN) : https://youtu.be/5yahh4tR0L0
