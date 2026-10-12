# Idées

## Analyseur de solos jazz « façon prof » (2026-10-11)

Analyser mes solos enregistrés avec JamCapture (session stompbox `multifx` ou autre)
et me faire un retour comme un prof.

1. Audio → notes : transcription en MIDI avec basic-pitch (Spotify, open source).
   Enregistrer un signal le plus propre possible (peu de disto/reverb).
2. Grille + tempo : grilles iReal (`linux-mao/ireal`), tempo Hydrogen/backing track.
3. Analyse temps par temps :
   - harmonie : notes de l'accord sur les temps forts, approches, enclosures, tensions ;
   - rythme : placement swing, avance/retard ;
   - phrasé : longueur des phrases, silences, tessiture, répétitions.
4. Retour pédagogique : un LLM transforme ces statistiques en conseils concrets.

Points durs : transcription quand le son est saturé, alignement précis sur la grille.

## C Jam Blues : repérer la grille et le turnaround (2026-10-12)

Constat : backing track contrebasse + batterie, je perds la grille sur les phrases
longues ; sur le turnaround (rapide), je reste sur l'arpège de Sol.

Grille (Do, à vérifier sur la backing track, les mesures 9-10 varient) :

```
| C7  | F7  | C7  | C7  |
| F7  | F7  | C7  | C7  |
| G7  | F7  | C7 A7 | Dm7 G7 |
```

1. Penser en 3 blocs de 4 mesures : phrases qui démarrent mesures 1, 5, 9
   (question / réponse / conclusion). D'abord 2 mesures jouées + 2 de silence,
   puis 4 mesures. Repères à la basse : mesure 5 (Fa), mesure 9 (Sol).
2. Notes guides : une note au 1er temps de chaque mesure, Mi sur C7, Mib sur F7
   (le Mi → Mib des mesures 4 → 5 est le repère). Puis broder autour.
3. Turnaround (mesures 11-12) en ligne de tierces, une note par accord :
   C7 Mi, A7 Do#, Dm7 Fa, G7 Si → Do. Version minimale : viser Si sur la mesure 12.
4. S'enregistrer avec JamCapture et noter où je décroche.
