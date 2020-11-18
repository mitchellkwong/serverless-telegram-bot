import os
import requests
import telegram
from telegram import Bot, ParseMode, Update
from telegram.ext import CommandHandler, Dispatcher

"""
================================================================================
"Private" helper functions
--------------------------------------------------------------------------------
redirect
- Dummy handler to forward a request to another cloud function.

request_handler
- Decorator to allow modify update handlers to accept requests.
================================================================================
"""

def _redirect(request, endpoint):
	def dummy_handler(update, context):
		"""Doesn't handle the update! Instead, forwards a request containing the 
		update JSON to the endpoint of a handler in a seperate cloud function"""
		requests.post(
			url = endpoint,
			json = request.get_json(force=True),
			headers = request.headers,
			params = request.args,
		)
	return dummy_handler

def _request_handler(handler):
	def wrapper(request):
		if request.method == 'POST':
			bot = bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
			update = Update.de_json(request.get_json(force=True), bot)
			handler(update, None)
	return wrapper

"""
================================================================================
Base Functions
--------------------------------------------------------------------------------
start
- 

help
- 

error
- 

router
-
================================================================================
"""

def start(update, context):
	"""Handler for the /start command"""
	text = (
		f'Hello {update.effective_user.first_name}!'
		'I am a serverless telgram bot that runs on Google Cloud Functions.'
		'Use /help to find out what I can do!'	
	)
	update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def help(update, context):
	"""Handler for the /help command"""
	text = (
		'Each of the following commands is handled in a seperate cloud function instance which automatically scales with usage.'
		'Additionally, usage analytics are maintained by Google Cloud Platform for each function, allowing easy analysis of bot usage.' + '\n\n'
		'**Commands**' + '\n'
		'/echo to make me repeat after you.' 
	)
	update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def error(update, context):
	"""Handler for any uncaught updates"""
	text = (
		'Telebots will take over the world'
	)
	update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def router(request):
	if request.method == 'POST':
		# Initialize a dummy telebot to make use of dispatchers
		bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])

		# Initialize dispatcher for base functions
		dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
		dispatcher.add_handler(CommandHandler('start', start))
		dispatcher.add_handler(CommandHandler('help', help))
		dispatcher.add_error_handler(error)

		# Initialize dispatcher to route updates for additional features
		dispatcher.add_handler(CommandHandler('echo', _redirect(request, os.environ['ECHO_ENDPOINT'])))

		# Parse update and pass to dispatcher
		update = Update.de_json(request.get_json(force=True), bot)
		dispatcher.process_update(update)
	return 'ok'

@_request_handler
def echo(update, context):
	"""Repeats the last message that was received"""
	text = update.message.text
	update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)