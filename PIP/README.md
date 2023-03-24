# Description
This library was originally created to be used with Discord API. But you can parse string messages as well, even though you won't be able to use Discord-specific things such as mentions.
# Example
```python
from foresteam_cmdargparse import Command, ArgParser

# Ceclare some commands
from foresteam_cmdargparse import Command, ArgParser

# Ceclare some commands
def Help(msg: str, args = {}, refwith = None):
	global commands
	fs: str = None
	if 'command' in args:
		args['command'] = ' '.join(args['command'])
	else:
		args['command'] = ''
	if args['command']:
		for com in commands:
			if (args['command'] in com.aliases):
				fs = com.printHelp()
				break
	else:
		r = ['Список команд:'];
		for com in commands:
			r.append(com.printHelp())
		fs = '\n'.join(r)
	print(fs or 'Команда не найдена') # msg.reply

# Create a parser
parser = ArgParser(_prefix='?')
# create a list of actual commands
commands = [
	Command(
		['помощь', 'help', '?'],
		[ { 'type': '...string|', 'name': 'command', 'desc': 'команда, по которой требуется помощь / ничего для показа списка команд' } ],
		'Помощь/список команд',
		Help
	),
]

def onMessage(msg: str):
	cmd: Command
	# Now call the parser to find choose the command and parse its arguments
	try:
		cmd, args, refwith = parser.parse(msg, commands)
		# Execute the found command
		cmd.execute(msg, args=args, refwith=refwith)
	except ArgParser.CommandNotFound:
		pass

onMessage(input('Enter a message: '))
```