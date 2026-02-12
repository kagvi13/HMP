# HyperCortex Mesh Protocol (HMP) — Description courte

**Version :** v5.0 (Core Specification Stable)  
**Date :** 2026  

---

## Qu’est-ce que HMP ?

Le **HyperCortex Mesh Protocol (HMP)** est une spécification ouverte destinée à la construction de réseaux cognitifs décentralisés d’agents autonomes.

HMP permet aux agents de :

- maintenir une continuité cognitive à long terme,
- échanger des connaissances structurées,
- coordonner des objectifs et des actions,
- atteindre un consensus distribué,
- s’aligner éthiquement à travers des systèmes hétérogènes.

Contrairement aux API d’IA traditionnelles sans état, HMP considère les agents comme des entités cognitives persistantes, intégrées dans un mesh de raisonnement et de mémoire partagés.

---

## Fondement conceptuel

HMP répond aux défis majeurs de la recherche contemporaine en IA et AGI :

- absence de continuité mémorielle à long terme,
- manque de coordination décentralisée,
- interopérabilité limitée entre agents autonomes,
- absence de gouvernance éthique au niveau du protocole.

HMP propose une architecture en couches dans laquelle le raisonnement, la mémoire, la gouvernance et le transport sont explicitement séparés mais interopérables.

---

## Concepts fondamentaux

### Agents cognitifs

Entités autonomes qui :

- raisonnent à l’aide de modèles d’IA embarqués ou externes,
- maintiennent des graphes sémantiques,
- consignent leurs décisions dans des journaux cognitifs,
- participent à la coordination distribuée.

HMP définit deux types d’agents :

- **Cognitive Core** — agent doté d’un modèle de raisonnement embarqué et d’un cycle de pensée continu basé sur REPL.
- **Cognitive Connector** — agent servant de couche de compatibilité pour des systèmes LLM externes.

---

### Conteneurs

HMP introduit les **conteneurs** comme unités cognitives atomiques.

Les conteneurs sont :

- signés,
- vérifiables,
- transportables à travers le mesh,
- structurellement indépendants du langage d’implémentation.

Ils assurent le lien entre le raisonnement local et la coordination distribuée.

---

### Graphes sémantiques & journaux

- Les **graphes sémantiques** représentent des connaissances structurées avec des relations pondérées.
- Les **journaux cognitifs** stockent des traces chronologiques de raisonnement, hypothèses, observations et réflexions.

Ensemble, ils garantissent la traçabilité de la pensée et la persistance de la mémoire.

---

### Coordination distribuée

HMP inclut des mécanismes au niveau protocolaire pour :

- la gestion du cycle de vie des objectifs,
- le consensus distribué,
- l’évaluation éthique,
- les requêtes et l’introspection entre agents.

La gouvernance est évolutive et fondée sur des propositions.

---

## Architecture du protocole (v5)

HMP distingue :

1. **Couche cognitive** — raisonnement, journaux, graphes, réputation.
2. **Couche des conteneurs** — représentation atomique et signée de l’état.
3. **Protocoles centraux** — consensus, gouvernance, gestion des objectifs, éthique.
4. **Couche de transport** — DHT, P2P, libp2p, ANP ou réseaux personnalisés.

Cette séparation favorise la modularité, la scalabilité et l’interopérabilité.

---

## Confiance & vérifiabilité

- Signature cryptographique des conteneurs et des instantanés
- Profils de réputation
- Mécanismes optionnels de résistance aux attaques Sybil
- Compatibilité prospective avec la cryptographie post-quantique

La confiance est considérée comme une propriété fondamentale du protocole.

---

## Interopérabilité

HMP n’impose aucune architecture cognitive interne.

Il peut interagir avec :

- ANP (Agent Network Protocol)
- OpenCog Hyperon
- Infrastructures orientées événements
- Systèmes basés sur des LLM via le Cognitive Connector

HMP se concentre sur la continuité cognitive plutôt que sur la seule standardisation du transport.

---

## Domaines d’application possibles

- Collaboration scientifique distribuée
- Systèmes de recherche multi-agents
- Réseaux de gouvernance éthique de l’IA
- Compagnons IA persistants
- Écosystèmes de connaissances basés sur un mesh

---

## Statut

- **v5.0 Core Specification — Stable**
- Early exploratory Python drafts (non-production, illustrative only)
- Raffinement architectural en cours
- Ouvert aux audits et aux contributions

---

## En savoir plus

- [Project Philosophy](PHILOSOPHY.md)
- [HMP-0005 Core Specification](HMP-0005.md)
- [Overview of v5 Architecture (RU)](HMPv5_Overview_Ru.md)

Les contributions et discussions sont bienvenues via le dépôt principal.
