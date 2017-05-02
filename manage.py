#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from app import create_app, db
from app.models import Examinee, QuestionMaker, Admin, Corrector
from flask_script import Manager, Shell
'''
The flask-script extension provides an external script to flask.
Including running a server for development, a custom Python shell,
set up the database script, cronjobs,
and other tasks running in command line outside web applications.
'''

# implement migrate of database in command line
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)


def full_fill_string(string):
    if not string:
        return "hard to find string"
    return string

app.jinja_env.filters['full_fill_string'] = full_fill_string


def make_shell_context():
    """
    integrate Python shell
        avoid to repeat import instance of database and models \
            after execute session of shell each time
        make some configuratins to import specified object automatically \
            by shell command of Flask-Script
    """
    return dict(app=app, db=db, Examinee=Examinee, QuestionMaker=QuestionMaker,
                Admin=Admin, Corrector=Corrector)

# add object to list of import by registering a callback function
    # of make_context to shell command
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """
        Run the unit tests in command line(build and add command,able: $ xxx -test).
    """
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
