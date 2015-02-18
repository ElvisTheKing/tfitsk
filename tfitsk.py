import click
import requests
import shelve
import logging
import slacker


def retrieve_fields(tf_uid, tf_key):
    r = requests.get(
        'https://api.typeform.com/v0/form/%s?key=%s&completed=true&offset=0' %
        (tf_uid, tf_key)
    )

    if (r.status_code != 200):
        raise Exception('typeforms request failed', r.text)

    data = r.json()
    return(data['questions'])


def retrieve_applicants(tf_uid, tf_key,
                        tf_email_field, tf_fname_field,
                        tf_lname_field, offset=0):
    r = requests.get(
        'https://api.typeform.com/v0/form/%s?key=%s&completed=true&offset=%d' %
        (tf_uid, tf_key, offset)
    )

    if (r.status_code != 200):
        raise Exception('typeforms request failed', r.text)

    data = r.json()

    def parse_item(item):
        ans = item['answers']
        return {
            'email': ans[tf_email_field],
            'first_name': ans[tf_fname_field],
            'last_name': ans[tf_lname_field],
        }

    applicants = map(parse_item, data['responses'])

    return applicants


def retrieve_channels(slack_key):
    slack = slacker.Slacker(slack_key)
    r = slack.channels.list().body['channels']
    return r


def invite_applicant(slack_key, slack_channels, email, first_name, last_name):
    slack = slacker.Slacker(slack_key)
    r = slack.api.post('users.admin.invite', params={
        'email': email,
        'channes': slack_channels,
        'set_active': 'true',
        '_attempts': 1,
        'first_name': first_name,
        'last_name': last_name
    })

    return r


@click.command()
@click.option('--tf-uid', help='typeforms uid')
@click.option('--tf-key', help='typeforms api key')
def print_fields(tf_uid, tf_key):
    fields = retrieve_fields(tf_uid, tf_key)
    click.echo(fields)


@click.command()
@click.option('--slack-key', help='slack api key')
def print_channels(slack_key):
    channels = retrieve_channels(slack_key)
    for channel in channels:
        click.echo('%s - %s' % (channel['id'], channel['purpose']['value']))


@click.command()
@click.option('--db',
              help='shelve file to store invited users',
              default='./shelve.db'
              )
@click.option('--tf-uid', help='typeforms uid')
@click.option('--tf-key', help='typeforms api key')
@click.option('--tf-email-field', help='tf email field id')
@click.option('--tf-fname-field', help='tf first name field id')
@click.option('--tf-lname-field', help='tf last name field id')
@click.option('--slack-key', help='slack api key')
@click.option('--slack-channels', help='slack channel ids, comma separated')
def do_invite(db, tf_uid, tf_key,
              tf_email_field, tf_fname_field, tf_lname_field,
              slack_key, slack_channels):
    d = shelve.open(db, writeback=True)
    if 'emails' not in d:
        d['emails'] = set()

    offset = 0
    while True:
        applicants = retrieve_applicants(tf_uid, tf_key,
                                         tf_email_field, tf_fname_field,
                                         tf_lname_field, offset
                                         )
        offset += 1000

        cnt = 0
        for applicant in applicants:
            cnt += 1

            if applicant['email'] in d['emails']:
                logging.debug('%s is already invited', applicant['email'])
                continue

            try:
                invite_applicant(slack_key, slack_channels,
                                 applicant['email'],
                                 applicant['first_name'],
                                 applicant['last_name']
                                 )

                d['emails'].add(applicant['email'])
                logging.info('inviting %s', applicant['email'])
            except slacker.Error as e:
                logging.error('slacker error: %s', e)
                if str(e) in ['already_in_team',
                              'already_invited',
                              'invalid_email',
                              'sent_recently']:
                    d['emails'].add(applicant['email'])

        else:
            if cnt < 1000:
                logging.debug('done %d applicants, it shouldnt be more' % cnt)
                break

            if cnt == 0:
                logging.debug('no more applicants')
                break

    d.close()
