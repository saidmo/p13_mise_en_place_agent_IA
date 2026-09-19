# Étude de faisabilité — Estimation des coûts

## 1. Méthode : un modèle paramétré

Plutôt qu'un chiffre unique (vite faux), cette étude pose un **modèle de coûts
paramétré** : on fixe des hypothèses (volume de vidéos, échantillonnage, débit
d'inférence, prix GPU, électricité), et le coût en découle. On peut ainsi
défendre la *méthode* et faire varier les hypothèses. Les prix unitaires sont des
valeurs de marché de 2026 ; les efforts de développement sont des estimations,
clairement signalées comme telles.

Deux postes sont distingués, comme demandé : **mise en place** (développement,
one-shot) et **fonctionnement** (récurrent).

## 2. Hypothèses

| Paramètre | Valeur exemple | Base |
|---|---|---|
| Vidéos à indexer | 1 000 | scénario POC élargi |
| Durée moyenne | 20 min | hypothèse |
| Échantillonnage de frames | 1 image / 2 s | compromis précision / coût |
| Frames totales | 600 000 | calcul |
| Débit d'inférence (détection + board-to-FEN) | ~20 frames/s | hypothèse conservatrice |
| Temps GPU d'ingestion | **~8,3 h** | 600 000 / 20 / 3600 |
| Prix GPU cloud (NVIDIA L4, à la demande) | ~0,65 €/h (≈ 0,70 $) | marché cloud 2026 |
| Prix électricité pro (France) | ~0,20 €/kWh | tarif pro 2026 (réf. Tarif Bleu Pro ≈ 0,16 €/kWh HT) |
| Puissance GPU interne (classe A100) | ~0,4 kW | spécification matérielle |
| Coût jour-homme (IA Engineer) | 500 € | valeur illustrative |

> Une L4 suffit largement : la détection d'échiquier et le board-to-FEN sont de
> petits modèles de vision, sans commune mesure avec un LLM. Des options moins
> chères existent (RTX 4090 en cloud communautaire ≈ 0,34 $/h, L4 spot ≈ 0,13 $/h).

## 3. Coûts de mise en place (one-shot)

| Poste | Jours-homme (est.) |
|---|---|
| Pipeline : extraction de frames, détection, board-to-FEN, indexation | 15 – 25 |
| Sélection / fine-tuning du modèle board-to-FEN (gestion des vidéos réelles) | 10 – 20 |
| Serveur MCP (FastMCP) + intégration à l'agent | 5 – 8 |
| Tests, itérations, mesure de précision | 5 – 10 |
| **Total** | **~35 – 60 j** |

À 500 €/j : **~17 500 € à 30 000 €**. Le poste le plus **variable** (et le plus
risqué) est le fine-tuning du modèle de vision : c'est là que se joue la précision
en conditions réelles, donc l'effort réel.

## 4. Coûts de fonctionnement (récurrents)

### 4.1 Calcul d'ingestion

Formule : `temps GPU = frames_totales / (débit × 3600)`, puis coût selon
l'infrastructure.

Pour le scénario (1 000 vidéos, ~8,3 h GPU) :

- **Cloud** (L4 à ~0,65 €/h) : 8,3 × 0,65 ≈ **5,4 € par passe complète**.
- **Interne** (électricité seule) : 8,3 × 0,4 kW × 0,20 €/kWh ≈ **0,7 €**.

Le coût croît linéairement avec le volume : 10 000 vidéos ≈ 54 € en cloud, ≈ 7 €
d'électricité en interne. **Conclusion forte : à cette échelle, le calcul
d'ingestion est un poste marginal**, quelle que soit l'infrastructure.

### 4.2 Stockage

En appliquant la mitigation juridique (ne stocker que `URL + timestamp + FEN`,
jamais les vidéos ni les frames), l'index est essentiellement du texte : quelques
dizaines d'octets par entrée. Pour des centaines de milliers d'entrées, on reste
sous le Go. **Coût négligeable.**

### 4.3 API YouTube

Gratuite dans le quota (10 000 unités/jour ; une recherche = 100 unités). La
collecte étant périodique et modérée, on reste dans le gratuit. Au-delà, un
relèvement de quota est à demander.

### 4.4 Maintenance

C'est le **vrai poste récurrent** : ré-ingestion des nouveaux contenus,
surveillance du modèle, corrections. Estimation ~1 à 3 j/mois, soit
**~500 à 1 500 €/mois**. Il dépasse de loin le coût de calcul.

## 5. Comparaison : GPU interne (PGX) vs cloud

| Critère | Interne (PGX) | Cloud à la demande |
|---|---|---|
| Coût marginal de calcul | ≈ électricité (négligeable) | faible (~5–50 €/passe) |
| Investissement initial | déjà possédé, mutualisé | nul |
| Élasticité | limitée (ressource partagée : n8n, dev internes) | forte, immédiate |
| Contention | risque de concurrence avec la prod interne | aucune |
| Gouvernance des données | **données traitées en interne** (favorable RSSI/DPO) | transit chez un tiers |
| Exploitation | à opérer soi-même | géré par le fournisseur |

**Point clé** : le calcul étant si peu coûteux à cette échelle, **le prix n'est
pas le critère décisif**. La décision se joue sur la **gouvernance des données**
et la **contention** de la ressource, pas sur les euros.

## 6. Synthèse et recommandation

- **Le calcul n'est pas le poste dominant.** À l'échelle d'un tel service
  (milliers de vidéos), l'ingestion coûte quelques euros à quelques dizaines
  d'euros par passe. Les postes réels sont le **développement initial**
  (~17,5–30 k€) et la **maintenance** (~0,5–1,5 k€/mois).
- **Interne vs cloud = un choix de gouvernance, pas de coût.** Pour un service
  récurrent et interne à la SIF, la PGX est cohérente avec la posture de
  souveraineté des données — à condition de planifier l'ingestion en heures
  creuses pour éviter la contention avec la production. Le cloud reste idéal pour
  une **ingestion massive ponctuelle** ou si la PGX est saturée.
- **Approche recommandée (hybride)** : prototyper l'ingestion en **cloud**
  (élastique, zéro engagement) pour la Phase 0 de validation, puis
  **opérationnaliser sur la PGX** l'index récurrent une fois la précision
  validée.
- **Le vrai facteur de décision reste ailleurs** : ce n'est pas le coût qui
  conditionne la faisabilité, mais la **précision de la reconnaissance en
  conditions réelles** (cf. note bénéfices/limites). Un budget de mise en place
  significatif ne se justifie qu'après un go/no-go technique en Phase 0.

> Chiffres illustratifs à ajuster selon le volume réel visé et le taux
> journalier retenu ; la méthode (modèle paramétré) reste valable quelles que
> soient les valeurs.
