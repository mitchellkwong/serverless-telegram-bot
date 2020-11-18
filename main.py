import os
import requests
import telegram

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

def echo(update, context):
	"""Repeats the last message that was received"""
	text = update.message.text
	update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def error(update, context):
	"""Handler for any uncaught updates"""
	text = """
	"""
	update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def router(request):
	if request.type == 'POST':
		# Initialize a dummy telebot to make use of dispatchers
		bot = telegram.Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])

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