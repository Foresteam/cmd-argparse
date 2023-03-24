from typing import Any, Callable
import discord

def getIDFromMention(mention):
	return mention[3:mention.length - 1]
def getMemberByID(id, guild: discord.Guild):
	for member in guild.members:
		if member.id == id:
			return member
	return None

class Command:
	def __init__(self, aliases: list[str], args: list[dict], help: str, execute: Callable[[list, str, discord.Message], Any]):
		self.aliases = aliases
		self.args = args
		self.help = help
		self.execute = execute

	def printHelp(self) -> str:
		name, alts = self.aliases[0], self.aliases[1:]
		for i in range(len(alts)):
			alts[i] = f'"{alts[i]}"'
		args = []
		for arg in self.args:
			try: arg['type'].index('|')
			except: arg['type'] += '|'
			typ, defval = arg['type'].split('|')
			args.append(arg['name'] + (defval and '=' + defval or '') + ': ' + typ + (arg['desc'] and ' - ' + arg['desc'] or ''))
		return f'{name}' + (len(alts) > 0 and f'[{", ".join(alts)}]' or '') + f'{len(args) > 0 and " (" + ", ".join(args) + ")" or ""} - {self.help}'
class ArgParser:
	class CommandNotFound(Exception):
		def __init__(self, msg: str):
			self.msg = msg
			super.__init__('Does not start with the prefix')
	class NotACommand(Exception):
		def __init__(self, msg: str):
			self.msg = msg
			super.__init__('Command not found')

	def __init__(self, _prefix='?'):
		self._prefix = _prefix
	def parse(self, msg: discord.Message | str, commands) -> tuple[Command, list, str]:
		text = msg if type(msg) == str else msg.content
		if not text.startswith(self._prefix):
			raise ArgParser.NotACommand(text)

		cmd: Command = None
		fa = ''
		for command in commands:
			for alias in command.aliases:
				if text.lower().startswith(self._prefix + alias):
					cmd = command
					fa = alias
					break
			if cmd:
				break
		if not cmd:
			raise ArgParser.CommandNotFound(text)
		text = text[len(self._prefix) + len(fa):]

		cnstrStr = False
		rargs, args, strs = {}, cmd.args, []

		ttext, i = text, -1
		while ttext.find('"') >= 0:
			i = ttext.find('"')
			if cnstrStr:
				tstr = ttext[:i]
				strs.append(tstr)
				text = text.replace(f'"{tstr}"', '%s')
				cnstrStr = False
			else:
				cnstrStr = True
			ttext = ttext[i + 1:]
		
		i = 0
		doVArg, vArg, vArgType, vArgName = False, [], '', ''
		for arg in text.split(' '):
			if len(arg) == 0:
				continue
			val = None

			ttype: str = ''
			if not doVArg and len(args) > i:
				ttype = args[i]['type']
				if ttype.startswith('...'):
					vArgType = ttype[3:]
					doVArg = True
					vArgName = args[i]['name']

			tp = vArgType if doVArg else ttype
			tp = tp.replace('|', '')
			if tp == 'int':
				val = int(arg)
			elif tp == 'float':
				val = float(arg)
			elif tp == 'string':
				if arg == '%s':
					arg = strs[0]
					del strs[0]
				val = arg
			elif tp == 'bool':
				val = arg == (args[i]['swon'] or 'on')
			elif tp == 'member':
				if type(msg) == str:
					val = None
				else:
					val = getMemberByID(getIDFromMention(arg), msg.guild)
			else:
				val = arg
			if doVArg:
				vArg.append(val)
			elif len(args) > i:
				rargs[args[i]['name']] = val
			i += 1
		if doVArg:
			rargs[vArgName] = vArg

		if i < len(args):
			for i in range(len(args)):
				if args[i]['name'] in rargs:
					continue
				try: args[i]['type'].index('|')
				except: args[i]['type'] += '|'
				typ, val = args[i]['type'].split('|')
				if typ.startswith('...'):
					break
				if typ == 'int':
					val = int(val)
				elif typ == 'float':
					val = float(val)
				elif typ == 'string':
					pass
				elif typ == 'member':
					if type(msg) == str:
						val = None
					else:
						val = getMemberByID(val, msg.guild)
				elif typ == 'bool':
					val = arg == (args[i]['swon'] or 'on')
				else:
					val = None
				rargs[args[i]['name']] = val
		return cmd, rargs, fa