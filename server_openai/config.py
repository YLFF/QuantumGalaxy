import argparse

parser = argparse.ArgumentParser(description='My app description')
parser.add_argument('--neo-name', type=str, default='nova',choices=['atlas', 'nova'],
                    help='neo4j database name')
parser.add_argument('--secret-key', type=str, default='quantumgalaxy',
                    help='secret key')
parser.add_argument('--debug', type=bool,default=False,
                    help='enable debug mode')
'''parser.add_argument('--allowed-extensions', type=str, default='txt,pdf,png,jpg,jpeg,gif',
                    help='allowed file extensions (comma-separated)')
parser.add_argument('--log-level', type=str, default='debug',
                    help='log level')'''

args = parser.parse_args()

NEO_NAME = args.neo_name
SECRET_KEY = args.secret_key
DEBUG = args.debug
#ALLOWED_EXTENSIONS = set(args.allowed_extensions.split(','))
#LOG_LEVEL = args.log_level