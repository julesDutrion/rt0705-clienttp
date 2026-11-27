# rt0705-clienttp

Le catalogue gère les supports physiques et numériques via l'API :
les types sont chargés depuis `/support-types` et les supports créés, modifiés
ou supprimés via `/supports`. Un support numérique est un lien HTTP(S) de
streaming ; le client ne gère aucun fichier vidéo. La page « Types de supports »
permet de gérer les types disponibles, et la recherche du catalogue accepte le
paramètre `supportType` pour filtrer les films.

Les utilisateurs peuvent créer un compte puis se connecter via `/auth/login`
de l'API. Le rôle par défaut est consulteur; seuls les gestionnaires et
administrateurs peuvent publier ou modifier le catalogue. Chaque utilisateur
peut modifier ses informations personnelles dans « Mon compte »; seul un
administrateur peut lister les comptes, modifier le rôle d'un autre compte ou
supprimer un compte depuis le panneau d'administration. L'inscription demande
une confirmation du mot de passe; une modification de mot de passe vérifie
également que les deux saisies correspondent.

Les utilisateurs authentifiés peuvent consulter leurs emprunts et leur
historique. Les gestionnaires et administrateurs disposent d'une page de gestion
globale, d'une recherche ciblée par login (`GET /loans/user/<login>`) et peuvent
confirmer le retour d'un support via `PATCH /loans/<idLoan>/return`. La recherche
est effectuée par l'API; un utilisateur inexistant est distingué d'un compte
existant sans emprunt.

La fiche d'un film affiche la disponibilité de chaque support physique depuis
les données de l'API et permet à un utilisateur connecté d'emprunter un support
disponible. La date de retour est affichée quand elle est visible via les
emprunts personnels ou la liste réservée aux gestionnaires et administrateurs;
l'API ne révèle pas cette date pour le prêt d'un autre utilisateur standard.
