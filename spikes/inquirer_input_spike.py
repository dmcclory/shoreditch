
from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json

questions = [
    {
        'type': 'input',
        'name': 'first_name',
        'message': 'What\'s your first name',
    },
    {
        'type': 'input',
        'name': 'last_name',
        'message': 'What is ... your last name',
    }
]

answers = prompt(questions)
print('uh... answers', answers)
print('uh... answers', answers['first_name'])
print('uh... answers', answers['last_name'])
print_json(answers)  # use the answers as input for your app
