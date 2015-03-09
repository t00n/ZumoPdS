# Atelier robots PdS 2015

Code pour l'atelier "Programmation de robots" organisé par UrLab au
[Printemps des Sciences](http://www.ulb.ac.be/inforsciences3/pds/index.html) 2015

[![Build Status](https://travis-ci.org/UrLab/ZumoPdS.svg)](https://travis-ci.org/UrLab/ZumoPdS)

## Installation

### Initialiser le repo

    git clone git@github.com:UrLab/ZumoPdS.git
    git submodule init
    git submodule update

### Utiliser Arduino 1.6+

* Exécuter `install-arduino-sketch.sh`

### Initialiser l'Arduino Yun

* Appuyer plus de 30 secondes sur le bouton "reset wan" (factory settings)
* Se connecter au wifi de l'Arduino
* Changer le nom de l'Arduino en Robot, mettre un mot de passe

### Uploader le code

* Aller dans l'Arduino IDE, File > Sketch > ZumoPds
* Tools > Board > Arduino Yun
* Tools > Serial Port > Robot @ 192.168.240.1
* Cliquer sur le bouton "upload"

### Tester le script carre.logo

    cd pylogo
    make run

## Ressources

* [Primitives LOGO](http://fr.wikipedia.org/wiki/Logo_%28langage%29#Primitives_graphiques)

