from setuptools import setup

setup(
    name='tfitsk',
    version='0.1',
    py_modules=['tfitsk'],
    install_requires=[
        'Click',
        'Requests',
        'Slacker'
    ],
    entry_points='''
        [console_scripts]
        tfitsk_print_typeform_fields=tfitsk:print_fields
        tfitsk_print_slack_channels=tfitsk:print_channels
        tfitsk_send_invitations=tfitsk:do_invite
    ''',
)
