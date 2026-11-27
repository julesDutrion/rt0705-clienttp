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
