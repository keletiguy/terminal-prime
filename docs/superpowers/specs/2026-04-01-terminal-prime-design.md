# Terminal Prime - Balance Commerciale Agee

## Overview

Application desktop Linux pour le suivi de la balance commerciale agee. Monitoring des factures emises, recouvrements et analyse des retards de paiement. Interface CustomTkinter avec design system "Carbon Console" (theme sombre, esthetique terminal financier).

## Decisions

| Decision | Choix | Raison |
|----------|-------|--------|
| Base de donnees | SQLite local | Mono-poste, zero config |
| Exports v1 | Excel + PDF basique | Relances automatiques en v2 |
| Lettrage | Manuel | Fiabilite, simplicite v1 |
| Saisie donnees | Import factures depuis Mediciel + saisie manuelle paiements | Factures generees par Mediciel |
| Devise | FCFA (XOF) | Format : 1 234 500 FCFA, pas de decimales (monnaie entiere) |
| Stockage montants | INTEGER (francs) | FCFA = monnaie entiere, pas de centimes |
| Graphiques | Canvas Tkinter natif | Controle total du style, pas de dep lourde |
| Architecture | MVC classique | Bon equilibre pour 5 ecrans |

## Stack technique

- Python 3.10+
- CustomTkinter (UI)
- SQLite3 (base de donnees)
- openpyxl (export Excel)
- reportlab (generation PDF)
- Pillow (images/icones)

## Architecture

```
terminal_prime/
├── main.py                     # Point d'entree
├── app.py                      # Controleur principal, navigation
├── theme.py                    # Design system Carbon Console
├── database/
│   ├── connection.py           # Singleton connexion SQLite
│   ├── schema.py               # Creation/migration tables
│   ├── client_repo.py          # CRUD clients (assureurs)
│   ├── affiliate_repo.py       # CRUD affilies
│   ├── invoice_repo.py         # CRUD factures
│   └── payment_repo.py         # CRUD paiements
├── models/
│   ├── client.py               # dataclass Client (assureur)
│   ├── affiliate.py            # dataclass Affiliate
│   ├── invoice.py              # dataclass Invoice
│   └── payment.py              # dataclass Payment
├── services/
│   ├── aging_service.py        # Calcul balance agee (0-30j, 31-60j, 61-90j, +90j)
│   ├── import_service.py       # Import Excel Mediciel
│   ├── dashboard_service.py    # Agregation KPIs
│   └── export_service.py       # Export Excel + PDF
├── views/
│   ├── dashboard_view.py       # Ecran 1 : tableau de bord
│   ├── invoices_view.py        # Ecran 2 : registre factures
│   ├── collections_view.py     # Ecran 3 : recouvrements
│   ├── client_analysis_view.py # Ecran 4 : analyse client
│   └── reports_view.py         # Ecran 5 : rapports
└── components/
    ├── sidebar.py              # Navigation laterale + profil
    ├── topbar.py               # Barre superieure (recherche, titre)
    ├── kpi_card.py             # Carte KPI reutilisable
    ├── data_grid.py            # Tableau zebra avec pagination
    ├── status_pill.py          # Indicateur statut colore
    ├── bar_chart.py            # Graphique barres Canvas
    ├── progress_bar.py         # Barre de progression
    └── search_entry.py         # Champ de recherche stylise
```

## Modele de donnees

### Table clients (assureurs / clients principaux)

| Colonne | Type | Contrainte |
|---------|------|------------|
| id | INTEGER | PK AUTOINCREMENT |
| name | TEXT | NOT NULL UNIQUE (ex: MCI CARE CI) |
| contact_email | TEXT | |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### Table affiliates (entreprises affiliees)

| Colonne | Type | Contrainte |
|---------|------|------------|
| id | INTEGER | PK AUTOINCREMENT |
| name | TEXT | NOT NULL (ex: SERVAIRE ABIDJAN) |
| client_id | INTEGER | FK -> clients (assureur parent) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| UNIQUE | (name, client_id) | Un affilie est unique par assureur |

### Table invoices

| Colonne | Type | Contrainte |
|---------|------|------------|
| id | INTEGER | PK AUTOINCREMENT |
| number | TEXT | UNIQUE (ex: INV-2024-042) |
| client_id | INTEGER | FK -> clients (assureur) |
| affiliate_id | INTEGER | FK -> affiliates (entreprise affiliee) |
| date | DATE | NOT NULL |
| due_date | DATE | NOT NULL (= date + 30 jours) |
| amount | INTEGER | NOT NULL (montant facture en FCFA) |
| status | TEXT | EN_ATTENTE, PAYEE, PARTIELLE |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### Table payments

| Colonne | Type | Contrainte |
|---------|------|------------|
| id | INTEGER | PK AUTOINCREMENT |
| invoice_id | INTEGER | FK -> invoices |
| client_id | INTEGER | FK -> clients (assureur) |
| date | DATE | NOT NULL |
| amount | INTEGER | NOT NULL (francs FCFA) |
| mode | TEXT | VIREMENT, CHEQUE, ESPECES |
| reference | TEXT | (ex: PAY-88219) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

Le statut EN_RETARD n'est PAS stocke en base. Il est derive dynamiquement a l'affichage :
si status != PAYEE et due_date < today, la facture est affichee comme EN_RETARD.
Les seuls statuts persistes sont : EN_ATTENTE, PAYEE, PARTIELLE.

### Gestion des clients

Deux niveaux de clients (structure Mediciel) :
- Client principal = assureur (ex: MCI CARE CI)
- Affilie = entreprise affiliee a l'assureur (ex: SERVAIRE ABIDJAN)

Les clients/affilies sont crees automatiquement lors de l'import Mediciel.
Creation manuelle possible via modals dans Factures et Analyse Client.
Un client ne peut pas etre supprime s'il a des factures associees.

### Formules financieres

- DSO (Days Sales Outstanding) = (Creances totales / CA credit 90 derniers jours) x 90
- CEI (Collection Effectiveness Index) = ((Creances debut mois + Facturations mois) - Creances fin mois) / (Creances debut mois + Facturations mois) x 100
- Taux de recouvrement = Total paiements recus / Total factures emises x 100

### Montants

Un seul champ montant par facture (montant total depuis Mediciel, en FCFA).
Pas de decomposition HT/TTC : la TVA est rarement applicable en pharmacie.

### Import Mediciel

Source : export Excel (.xlsx) de Mediciel.

Colonnes utilisees :

| Colonne Mediciel | Champ app | Traitement |
|------------------|-----------|------------|
| Date facture | invoices.date | Conversion serial Excel -> date |
| Client principal | clients.name | Creation auto si n'existe pas |
| Affilie | affiliates.name | Creation auto, lie au client principal |
| N. Facture | invoices.number | Import tel quel |
| Montant Total | invoices.amount | Montant facture en FCFA |

Colonnes ignorees : M, S, Reglement, Solde, !, Statut Envoi, Date Envoi, Code Recap. Client.

Regles d'import :
- due_date = date + 30 jours (regle fixe)
- Status initial = EN_ATTENTE (les paiements sont saisis manuellement dans l'app)
- Si un client principal n'existe pas, il est cree automatiquement
- Si un affilie n'existe pas pour ce client, il est cree automatiquement
- Detection des doublons par numero de facture (UNIQUE) : les factures deja importees sont ignorees
- L'import affiche un resume : X factures importees, Y ignorees (doublons), Z clients crees

## Design System "Carbon Console"

### Palette de couleurs

```
Surfaces (profond -> eleve):
  SURFACE_LOWEST  = #0e0e0e   (champs input)
  SURFACE         = #131313   (fond de base)
  SURFACE_LOW     = #1c1b1b   (lignes paires zebra)
  SURFACE_CONT    = #20201f   (blocs contenu)
  SURFACE_HIGH    = #2a2a2a   (hover, cartes actives)
  SURFACE_BRIGHT  = #393939   (modales)

Couleurs semantiques:
  PRIMARY         = #a5c8ff   (texte action)
  PRIMARY_CONT    = #1f538d   (CTA, sidebar active)
  TERTIARY        = #fdbb2e   (succes/paye)
  TERTIARY_CONT   = #6d4c00   (fond status paye)
  ERROR           = #ffb4ab   (en retard)
  ERROR_CONT      = #93000a   (fond status en retard)

Texte:
  ON_SURFACE      = #e5e2e1   (principal)
  ON_SURFACE_VAR  = #c2c6d1   (secondaire, labels)
  OUTLINE_VAR     = #424750   (ghost borders 15%)
```

### Regles de design

- Pas de bordures 1px : separation par changement de fond uniquement
- Coins arrondis 10px sur tous les composants
- Police Inter, labels en MAJUSCULES avec tracking large
- Zebra striping : alternance SURFACE_LOW / SURFACE
- Status pills : fond semi-transparent + texte colore, non-interactifs
- Bouton primaire : degrade 145deg de PRIMARY vers PRIMARY_CONT

### Composants

| Composant | Usage | Ecrans |
|-----------|-------|--------|
| sidebar | Navigation 5 items + profil utilisateur | Tous |
| topbar | Titre + recherche + icones | Tous |
| kpi_card | Label, valeur, badge tendance | Dashboard, Factures, Rapports |
| data_grid | Tableau zebra avec pagination | Factures, Recouvrements, Rapports, Analyse |
| status_pill | Chip colore (EN RETARD, PAYEE, etc.) | Factures, Recouvrements |
| bar_chart | Barres verticales Canvas | Dashboard, Analyse client |
| progress_bar | Jauge horizontale degradee | Dashboard |
| search_entry | Champ recherche stylise | Tous (topbar) |

## Ecrans

### Ecran 1 — Dashboard

- 3 cartes KPI : Total Emis, Total Recouvre, Solde Global
- Graphique balance agee : 4 barres Canvas (0-30j, 31-60j, 61-90j, +90j)
- Performance : barre progression taux recouvrement + DSO + CEI
- Top 5 debiteurs : data_grid trie par montant du decroissant

### Ecran 2 — Factures

- Carte KPI : Total Outstanding
- Bouton "Importer Mediciel" : import Excel
- Filtres : dropdown statut + dropdown periode + dropdown client principal
- Tableau : N. Facture, Date, Client principal, Affilie, Montant, Solde, Statut (pill), Actions
- Pagination : 10 factures par page
- Formulaire modal : creation/modification facture manuelle
- Actions rapides : Export PDF batch

### Ecran 3 — Recouvrements

- Formulaire saisie : selection facture, date, mode paiement, montant
- Derniers recouvrements : liste 5 derniers paiements
- Lettrage manuel : selection facture lors de la saisie
- Stats en bas : Total collecte MTD, Montant restant, DSO

### Ecran 4 — Analyse Client

- Recherche client dans topbar
- Carte resume : solde total + repartition par tranche d'age
- Composition agee : legende coloree avec pourcentages
- Timeline : barres Canvas factures vs paiements (6 derniers mois)
- Actions : Full Statement (PDF export du grand livre client)

### Ecran 5 — Rapports & Relances

- Filtres : periode + statut relance
- KPIs : Encours total echu, Retards >30j, Retards >90j
- Tableau factures echues avec colonne retard (jours, pill coloree)
- Export Excel balance agee complete (openpyxl)
- DSO : delai moyen de paiement

## Formulaires

### Import factures (ecran Factures)

Bouton "Importer Mediciel" ouvre un file picker pour selectionner le fichier .xlsx.
L'import parse le fichier, cree clients/affilies si necessaire, et insere les factures.
Un resume s'affiche apres import : X factures importees, Y doublons ignores, Z clients crees.

### Formulaire Facture manuelle (modal, usage ponctuel)

| Champ | Type | Requis | Notes |
|-------|------|--------|-------|
| N. Facture | Texte | Oui | Saisi manuellement |
| Client principal | Dropdown | Oui | Liste assureurs + bouton "Nouveau" |
| Affilie | Dropdown | Oui | Filtre par client principal selectionne |
| Date facture | Date picker | Oui | Defaut : aujourd'hui |
| Montant | Entier | Oui | En FCFA |

La date d'echeance est calculee automatiquement : date + 30 jours.

### Formulaire Paiement (ecran Recouvrements)

| Champ | Type | Requis | Notes |
|-------|------|--------|-------|
| Facture | Dropdown | Oui | Factures non soldees uniquement |
| Date paiement | Date picker | Oui | Defaut : aujourd'hui |
| Mode | Dropdown | Oui | VIREMENT, CHEQUE, ESPECES |
| Montant | Entier | Oui | En FCFA, max = solde restant facture |

La reference est auto-generee : PAY-NNNNN.
Apres saisie, le statut facture est mis a jour : PAYEE si solde = 0, PARTIELLE sinon.

### Formulaire Client principal (modal)

| Champ | Type | Requis | Notes |
|-------|------|--------|-------|
| Nom | Texte | Oui | Nom de l'assureur |
| Email contact | Email | Non | |

### Formulaire Affilie (modal)

| Champ | Type | Requis | Notes |
|-------|------|--------|-------|
| Nom | Texte | Oui | Nom de l'entreprise |
| Client principal | Dropdown | Oui | Assureur parent |

## Sidebar

| Item | Label | Icone |
|------|-------|-------|
| 1 | Tableau de Bord | dashboard |
| 2 | Factures | description |
| 3 | Recouvrements | payments |
| 4 | Analyse Client | analytics |
| 5 | Rapports | assessment |

En bas : profil utilisateur (nom + role) + bouton deconnexion.

## Fenetre

- Taille initiale : 1400x900 pixels
- Taille minimum : 1200x700 pixels
- Layout fixe (pas de responsive), scroll vertical si necessaire

## Navigation

Systeme de frames empilees via app.py. Un seul ecran visible a la fois. Clic sidebar fait tkraise() sur le frame correspondant. Pas de destruction/recreation pour conserver l'etat.

## Hors perimetre v1

- Lettrage automatique/semi-automatique
- Lettres de relance automatiques (niveaux 1-2-3)
- Envoi email
- Multi-utilisateur / PostgreSQL
- Theme clair
- Internationalisation
- Create Adjustment (ajustements comptables)
- Gestion multi-devises
