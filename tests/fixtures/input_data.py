# -*- coding: utf-8 -*-

usernames = {
    'valids': (
        'bizeuuu',
    ),
    'invalids': (
        'bizeuuuñño',
        'bizeuá sdf',
    )
}

emails = {
    'valids': (
        'bizeuuu@example.com',
    ),
    'invalids': (
        'bizeuuu@?',
    )
}

passwords = {
    'valids': (
        'eñaaaÁ2710',
    ),
    'invalids': (
        '',
        '____________________________12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgss12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgsdgs12fdsgss12fdsgsdgs12fdsgsdgs12dgs12fdsgsdgs12',
    )
}

# para logueo
usernames_emails = {
    'valids': usernames['valids'] + emails['valids'],
    'invalids': usernames['invalids'] + emails['invalids'],
}