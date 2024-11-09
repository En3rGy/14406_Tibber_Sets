# Tibber Sets (14406)

## Beschreibung 

Der Baustein nutzt den Ausgang von Baustein [Tibber (14464)](https://github.com/SvenBunge/hs_tibber) und bestimmt Zeitfenster, in denen
der Strom günstig bzw. teuer ist. Der Anwendungsfall ist das Steuern von Batterien bzgl. laden und entladen.

## Eingänge

| Nr. | Name               | Initialisierung | Beschreibung                                                                                  |
|-----|--------------------|-----------------|-----------------------------------------------------------------------------------------------|
| 1   | Prices Today       |                 | Link auf entsprechenden Ausgang von [Tibber (14464) ](https://github.com/SvenBunge/hs_tibber) |
| 2   | Prices Tomorrow    |                 | Link auf entsprechenden Ausgang von [Tibber (14464) ](https://github.com/SvenBunge/hs_tibber) |
| 3   | Cheap [€]          | 0.23            | Preis, ab dem Einzelpreise als "günstig" gewertet werden, unabhängig vom Durchschnittspreis.  |
| 4   | Expensive [€]      | 0.99            | Preis, ab dem Einzelpreise als "teuer" gewertet werden, unabhängig vom Durchschnittspreis.    | 
| 5   | Normal Usag        | 0               | "Normal"-Preisen könne mit -1 einem günstigen Preis-Intervall zugeordnet werden.<br>1 interpretiert Normale-Intervalle als "teuer",<br>0 ordnet sie weder den teuren, noch den günstigen Intervallen zu. |

## Ausgänge

Zeiten als String im Format HH:MM, z.B. 07:00

| Nr. | Name                     | Initialisierung | Beschreibung                                                   |
|-----|--------------------------|-----------------|----------------------------------------------------------------|
| 1   | Cheap Period Start 1     |                 | Beginn des 1. Günstig-Abschnitts                               |
| 2   | Cheap Period Stop 1      |                 | Ende des 1. Günstig-Abschnitts                                 |
| 3   | Cheap Period Start 2     |                 | Beginn des 1. Günstig-Abschnitts                               |
| 4   | Cheap Period Stop 2      |                 | Ende des 1. Günstig-Abschnitts                                 |
| 5   | Expensive Period Start 1 |                 | Beginn des 1. Teuer-Abschnitts                                 |
| 6   | Expensive Period Stop 1  |                 | Ende des 1. Teuer-Abschnitts                                   |
| 7   | Expensive Period Start 2 |                 | Beginn des 2. Teuer-Abschnitts                                 |
| 8   | Expensive Period Stop 2  |                 | Ende des 2. Teuer-Abschnitts                                   |
| 9   | Is Cheap                 | 0               | 1, wenn aktuell ein Günstig-Abschnitt ist.                     |
| 10  | Is Expensive             | 0               | 1, wenn aktuell ein Teuer-Abschnitt ist.                       |
| 11  | Price Level +1h          | 0               | Current price level with -1 = cheap, 0 = normal, 1 = expensive |
| 12  | Price Level +1h          | 0               | Price level in 1h with -1 = cheap, 0 = normal, 1 = expensive   |
| 13  | Price Level +2h          | 0               | Price level in 2h with -1 = cheap, 0 = normal, 1 = expensive   |
| 14  | Price Level +3h          | 0               | Price level in 3h with -1 = cheap, 0 = normal, 1 = expensive   |

## Sonstiges

- Neuberechnug beim Start: Nein
- Baustein ist remanent: nein
- Interne Bezeichnung: 14406
- Kategorie: Energiemanagement

### Change Log

Siehe [github Changelog](https://github.com/En3rGy/14405_AlphaESS_ModbusTCP/releases) zum jew. Release. 

### Open Issues / Know Bugs

Bekannte Fehler werden auf [github](https://github.com/En3rGy/14107_NibeWP) verfolgt.

### Support

Please use [github issue feature](https://github.com/En3rGy/14405_AlphaESS_ModbusTCP/issues) to report bugs or rise feature requests.
Questions can be addressed as new threads at the [knx-user-forum.de](https://knx-user-forum.de) also. There might be discussions and solutions already.

### Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14405_AlphaESS_ModbusTCP).

### Devleopment Environment

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python markdown module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)


## Anforderungen

- Der Baustein soll die nächsten günstigen Preisintervalle ausgeben.
- Der Baustein soll die nächsten teuren Preisintervalle ausgeben.
- Zeiten sollen im Format HH:MM ausgegeben werden.
- Überlappen Zeitintervalle (bspw. weil sie an verschiedenen Tagel liegen) soll nur das zeitlich näherliegende ausgegeben werden.
- Abgelaufene Intervalle sollen nicht mehr ausgegeben werden.
- Wird ein Intervall nicht genutzt, soll Start- und Stoppzeit auf "00:00" gesetzt werden.

## Software Design Description

-

## Validierung & Verifikation

- Teilweise Abdeckung durch Unit Tests 

## Licence

Copyright 2024 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
