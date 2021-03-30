const discord = require('discord.js');

function getIDFromMention(mention) {
    return mention.substring(3, mention.length - 1);
}
async function getMemberByID(id, guild) {
    for (let member of await guild.members.cache.array())
        if (member.id == id)
            return member;
    return null;
}

class Command {
    constructor(aliases, args, help, execute) {
        this.aliases = aliases;
        this.args = args;
        this.help = help;
        this.execute = execute;
    }
    printHelp() {
        let [name, ...alts] = this.aliases;
        for (let i in alts)
            alts[i] = `"${alts[i]}"`;
        let args = [];
        for (let arg of this.args) {
            let [type, defval] = arg.type.split('|');
            args.push(arg.name + (defval ? '=' + defval : '') + ': ' + type + (arg.desc ? ' - ' + arg.desc : ''));
        }
        return `${name}` + (alts.length > 1 ? `[${alts.join(', ')}]` : '') + `${args.length > 0 ? ' (' + args.join(', ') + ')' : ''} - ${this.help}`;
    }
}

class ArgParser {
    constructor(prefix='?', allowSpaceInCommands=true) {
        this.prefix = prefix;
        this.allowSpace = allowSpaceInCommands;
    }
    parse(msg, commands) {
        let text = msg.content;
        if (!text.startsWith(this.prefix))
            return false;

        let cmd = null, fa = '';
        for (let command of commands) {
            for (let alias of command.aliases)
                if (text.toLowerCase().startsWith(this.prefix + alias)) {
                    cmd = command;
                    fa = alias;
                    break;
                }
            if (cmd)
                break;
        }
        if (!cmd)
            return false;
        text = text.substring(this.prefix.length + fa.length);

        let cnstrStr = false;
        let rargs = {}, args = cmd.args, strs = [];

        let ttext = text, i;
        while ((i = ttext.indexOf('"')) >= 0) {
            if (cnstrStr) {
                let tstr = ttext.substring(0, i);
                strs.push(tstr);
                text = text.replace(`"${tstr}"`, '%s');
                cnstrStr = false;
            }
            else
                cnstrStr = true;
            ttext = ttext.substring(i + 1);
        }
        
        i = 0;
        let doVArg = false, vArg = [], vArgType = '', vArgName = '';
        try {
            for (let arg of text.split(' ')) {
                if (arg.length == 0)
                    continue;
                let val = null;

                let ttype;
                if (!doVArg && args.length > i) {
                    ttype = args[i].type;
                    if (ttype.startsWith('...')) {
                        vArgType = ttype.substring(3);
                        doVArg = true;
                        vArgName = args[i].name;
                    }
                }

                switch (doVArg ? vArgType : ttype) {
                    case 'int':
                        val = parseInt(arg);
                        break;
                    case 'float':
                        val = parseFloat(arg);
                        break;
                    case 'string':
                        if (arg == '%s') {
                            arg = strs[0];
                            strs.splice(0);
                        }
                        val = arg;
                        break;
                    case 'bool':
                        val = arg == 'вкл';
                        break;
                    case 'member':
                        val = getMemberByID(getIDFromMention(arg), msg.guild);
                        break;
                    default:
                        val = arg;
                        break;
                }
                if (doVArg)
                    vArg.push(val);
                else if (args.length > i)
                    rargs[args[i].name] = val;
                i++;
            }
            if (doVArg)
                rargs[vArgName] = vArg;

            if (i < args.length)
                for (; i < args.length; i++) {
                    let [type, val] = args[i].type.split('|');
                    if (type.startsWith('...'))
                        break;
                    switch (type) {
                        case 'int':
                            val = parseInt(val);
                            break;
                        case 'float':
                            val = parseFloat(val);
                            break;
                        case 'string':
                            break;
                        case 'member':
                            val = getMemberByID(val, msg.guild);
                            break;
                        case 'bool':
                            val = val == 'вкл';
                            break;
                        default:
                            val = null;
                            break;
                    }
                    rargs[args[i].name] = val;
                }
            return {cmd, args: rargs, refwith: fa};
        }
        catch (e) {
            console.log(e);
            return false;
        }
    }
}

module.exports = {ArgParser: ArgParser, Command: Command};