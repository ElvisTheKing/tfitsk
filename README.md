# TFITSK thingy
typeform.com invites to slack.com

gets submitted emails and names from typeform api and invites this person to slack team
you will need typeform api key and api_token used by slack in web interface (no, generated api key won't work)

#### Usage 
to get slack channel ids
```
Usage: tfitsk_print_slack_channels [OPTIONS]

Options:
  --slack-key TEXT  slack api key
```

to get typeform field ids
```
Usage: tfitsk_print_typeform_fields [OPTIONS]

Options:
  --tf-uid TEXT  typeforms uid
  --tf-key TEXT  typeforms api key
```

to send invitations
```
Usage: tfitsk_send_invitations [OPTIONS]

Options:
  --db TEXT              shelve file to store invited users
  --tf-uid TEXT          typeforms uid
  --tf-key TEXT          typeforms api key
  --tf-email-field TEXT  tf email field id
  --tf-fname-field TEXT  tf first name field id
  --tf-lname-field TEXT  tf last name field id
  --slack-key TEXT       slack api key
  --slack-channels TEXT  slack channel ids, comma separated
```
