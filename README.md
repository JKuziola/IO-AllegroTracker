# AllegroTracker
Projekt stworzony w ramach przedmiotu Inżynieria Oprogramowania na Uniwersytecie Warszawskim.

### Użyte technologie

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)

![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## Opis projektu
Aplikacja webowa, która pozwala na śledzenie cen produktów na Allegro. Użytkownik może się zarejestrować i dodać 
interesujące go produkty do listy obserwowanych. Aplikacja będzie sprawdzać cenę produktu i wysyłać powiadomienie, gdy 
cena spadnie poniżej określonej przez użytkownika wartości.

Ponieważ ceny produktów na Allegro nie zmieniają się zbyt często, skonfigurowaliśmy naszą aplikację do działania 
w środowisku testowym Allegro. W tym celu stworzyliśmy konto na Allegro Sandbox, które pozwala na testowanie aplikacji
bez konieczności korzystania z prawdziwych danych. Dodaliśmy do niego kilka ofert, które są dostępne pod linkami
podanymi na końcu tego pliku.

## Korzystanie z aplikacji
Aplikacja została wdrożona na Heroku i jest dostępna pod adresem:
https://allegro-tracker.herokuapp.com/.

Nie ma zatem potrzeby uruchamiania jej lokalnie, jednak jeśli chcesz to zrobić, to poniżej znajdziesz instrukcję.

## Uruchamianie aplikacji lokalnie

Sklonuj repozytorium i przejdź do katalogu z projektem:
```shell
git clone git@github.com:wojsza05/IO.git
cd IO
```

Stwórz i aktywuj środowisko wirtualne:
```shell
virtualenv virtual
source virtual/bin/activate
```

Zainstaluj wymagane biblioteki:
```shell
pip install -r requirements.txt
```

Uruchom aplikację:
```shell
python3 manage.py runserver
```

Uruchom testy jednostkowe Django:
```shell
python3 manage.py test AllegroTracker
```

Aplikacja będzie dostępna pod adresem http://localhost:8000/

### Domyślny użytkownik
    login: admin
    password: admin

## Wygląd aplikacji
### Strona logowania
![Strona logowania](imagesoginPage.png)

### Strona główna
![Strona główna](imagesainPage.png)

### Dodanie produktu
![Dodanie produktu](imagesddProduct.png)

### Widok produktu
![Widok produktu](imagesetailView.png)

## Nasze oferty:
- https://allegro.pl.allegrosandbox.pl/oferta/dlugopis-bialy-klawiatura-7708611553
- https://allegro.pl.allegrosandbox.pl/oferta/opaska-hej-7708611184
- https://allegro.pl.allegrosandbox.pl/oferta/zestaw-naprawczy-wiazki-el-drzwi-107065-7708610767
- https://allegro.pl.allegrosandbox.pl/oferta/acer-testowy-309-7708610327
- https://allegro.pl.allegrosandbox.pl/oferta/poduszka-75-x-55-cm-psy-7708610265
- https://allegro.pl.allegrosandbox.pl/oferta/vonala-zawieszka-kot-na-ksiezycu-stylowa-7708609606