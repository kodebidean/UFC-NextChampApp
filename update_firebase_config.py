import os
import json

# Read the firebase_config.json file
with open('firebase_config.json', 'r') as f:
    config = json.load(f)

# Update the values with environment variables
config['project_id'] = os.environ['FIREBASE_PROJECT_ID']
config['private_key_id'] = os.environ['FIREBASE_PRIVATE_KEY_ID']
config['private_key'] = os.environ['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n')  # Replace escaped newlines
config['client_email'] = os.environ['FIREBASE_CLIENT_EMAIL']
config['client_id'] = os.environ['FIREBASE_CLIENT_ID']

# Update client_x509_cert_url
config['client_x509_cert_url'] = config['client_x509_cert_url'].replace('{{FIREBASE_CLIENT_EMAIL}}', os.environ['FIREBASE_CLIENT_EMAIL'])

# Write the updated config back to the file
with open('firebase_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Firebase config updated successfully.")
