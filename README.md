# rt0705-clienttp

Le formulaire des films gère leurs supports physiques et numériques via l'API :
les types sont chargés depuis `/support-types` et les supports créés, modifiés
ou supprimés via `/supports`. Un support numérique est un lien HTTP(S) de
streaming ; le client ne gère aucun fichier vidéo. La page « Types de supports »
permet de gérer les types disponibles, et la recherche du catalogue accepte le
paramètre `supportType` pour filtrer les films.