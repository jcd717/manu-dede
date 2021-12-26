Téléchargement de vidéos YouTube (et autres)
============================================

Dans `versionAsyncQuiMarchePas`, il y a un essai de version asynchone.
* C'est à dire: l'application affiche des informations sur l'état du download et permet de l'arrêter

Mais je n'y suis pas arrivé, car en utilisant `subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)`, `os.set_blocking(process.stdout.fileno(), False)` et `line = process.stdout.readline()`, il semblerait que je tombe sur le *deadlock* signalé par la doc lors d'un accès à `stdout` ou `stderr` puisque le processus de download passe en mode *SLEEP* et n'en sort pas.

Donc je laisse tomber et fait une application qui lorsqu'on appuie sur le bouton de *Récupération* (=download côté serveur), télécharge jusqu'à la fin => attente qui peut être longue.

**Si quelqu'un a une solution simple (sans passer par des appels de lancement de processus bas niveau), ça m'intéresse**

