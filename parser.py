# *coroutine *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+)) *\((.*)\) -> identifica se eh uma corrotina
# *start *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+)) *\((.*)\)
# *active *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+))
# *stop *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+))
# *resume *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+))
# *cancel *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+))

#str.strip() remove leading and trailing spaces

import sys
import re
from corrotina import Corrotina
regex_corrotina = re.compile(ur' *coroutine *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+)) *\((.*)\)')
regex_start = re.compile(ur' *start *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+)) *\(([A-z0-9_, ]*)\);')
regex_active = re.compile(ur' *active *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+));')
regex_stop = re.compile(ur' *stop *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+));')
regex_resume = re.compile(ur' *resume *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+));')
regex_cancel = re.compile(ur' *cancel *((?:[A-z][A-z_0-9])*|(?:_[A-z_0-9]+));')
regex_op = re.compile(ur' *op;')
regex_program = re.compile(ur' *program')
regex_end_program = re.compile(ur' *end program')
regex_shared = re.compile(ur' *shared (.*);') 
regex_begin = re.compile(ur' *begin') 
regex_end = re.compile(ur' *end')

in_program = False
out_progam = False
got_begin = False
current_coroutine = ''
in_coroutine = False
shared_vars = []

coroutines_activation = {}


def exact_match(result, line):
	return result != None and (result.start() == 0 and result.end() == len(line))


def parse_decl_coroutine(result):
	(name, arguments) = result.groups()
	list_arguments = arguments.split(',')
	

	ret_args = []
	if(len(list_arguments) == 1 and len(list_arguments[0]) == 0):
		return (name, ret_args)
	
	for _argument in list_arguments:
		argument = _argument.strip().split(':')
		if(len(argument) != 2):
			return None
		argument[0] = argument[0].strip()
		argument[1] = argument[1].strip()
		if( (not ' ' in argument[0]) and (not ' ' in argument[0]) ):
			ret_args.append((argument[0],argument[1]))
		else:
			return None
	return (name, ret_args)


def parse_decl_start(result):
	(name, arguments) = result.groups()
	list_arguments = arguments.split(',')

	# return (name, list_arguments)
	ret_args = []
	
	for _argument in list_arguments:
		
		argument = _argument.strip()
		if( not ' ' in argument):
			if(argument != ''):
				ret_args.append(argument)
		else:
			return None
	return (name, ret_args)

def parse_decl_shared(result):
	(arguments,) = result.groups()

	list_arguments = arguments.split(',')

	# return (name, list_arguments)
	ret_args = []
	
	for _argument in list_arguments:
		
		argument = _argument.strip()
		if( not ' ' in argument):
				ret_args.append(argument)
		else:
			return None
	return ret_args


f = open(sys.argv[1], 'r')

i = 0

# print str(f.readlines())
for _line in f.readlines():
	i += 1
	#print(_line)
	line = _line[:len(_line)-1].strip()
	#print(line)
	if(in_program == False):
		if(line == ""):
			continue
		result = re.search(regex_program, line)
		if(exact_match(result,line)):
			in_program = True
		else:
			sys.exit(1)
		continue

	if(in_coroutine == True):
		if(line == "\n"):
			continue
		if(got_begin == False):
			result = re.search(regex_begin, line)
			if(exact_match(result, line)):
				got_begin = True
				continue
		else:
			result = re.search(regex_end, line)
			if(exact_match(result, line)):
				got_begin = False
				in_coroutine = False
				continue
			result = re.search(regex_op, line)
			if(exact_match(result, line)):
				coroutines_activation[current_coroutine].add_instruction(["op"])
				continue



			result = re.search(regex_start, line)
			if(exact_match(result, line)):
				temp = parse_decl_start(result)
				if(temp == None):
					print " Erro na linha " + str(i) + ": " + line
					quit()
				(coroutine_to_start, args) = temp
				coroutines_activation[current_coroutine].add_instruction(["start", coroutine_to_start, args])
				continue


			result = re.search(regex_stop, line)
			if(exact_match(result, line)):
				(name,) = result.groups()
				coroutines_activation[current_coroutine].add_instruction(["stop", name])
				continue

			result = re.search(regex_resume, line)
			if(exact_match(result, line)):
				(name,) = result.groups()
				coroutines_activation[current_coroutine].add_instruction(["resume", name])
				continue

			result = re.search(regex_active, line)
			if(exact_match(result, line)):
				(name,) = result.groups()
				coroutines_activation[current_coroutine].add_instruction(["active", name])
				continue

			result = re.search(regex_cancel, line)
			if(exact_match(result, line)):
				(name,) = result.groups()
				coroutines_activation[current_coroutine].add_instruction(["cancel", name])
				continue

	if(in_program == True):
		if(line == ""):
			continue
		if(in_coroutine == False):
			result = re.search(regex_end_program, line)
			if(exact_match(result, line)):
				out_progam = True
				continue
			result = re.search(regex_corrotina, line)

			if(exact_match(result, line)):
				in_coroutine = True
				corrotina = parse_decl_coroutine(result)
				if(corrotina == None):
					print " Erro 1 na linha " + str(i) + ": " + line
					exit(0)
				(coroutine_name, coroutine_args) = corrotina
				current_coroutine = coroutine_name
				coroutines_activation[coroutine_name] = Corrotina(coroutine_name, coroutine_args)
				continue

			result = re.search(regex_shared, line)

			if(exact_match(result, line)):
				variables = parse_decl_shared(result)
				if(variables == None or variables == []):
					print " Erro 2 na linha " + str(i) + ": " + line
					exit(0)
				(new_shared_vars) = variables
				
				#TODO: Verificar se alguma variavel ja nao foi declarada
				shared_vars += new_shared_vars
				continue
		print " Erro na linha  3" + str(i) + ": " + line

		
		quit()
	if(in_program == True and out_progam == True):
		if(line != ""):
			exit(0)


print "Sintaxe -> Ok! "



################################################################################################

if("main" in coroutines_activation.keys()):
	corrotina_atual = coroutines_activation["main"]
else:
	print "Erro -> corrotina main indefinida"
	quit()



corrotinas_ativas = ["main"]
corrotinas_pausadas = []

#copiando
corrotinas_nao_iniciadas = coroutines_activation.keys()[:]
corrotinas_nao_iniciadas.remove("main")

print corrotinas_nao_iniciadas

maxIt = 5
remaining_it = maxIt

while len(corrotinas_ativas) != 0:

	if(corrotina_atual.counter == len(corrotina_atual.instructions)):
		corrotinas_ativas = corrotinas_ativas[1:]
		if(len(corrotinas_ativas) > 0 ):
			corrotina_atual = coroutines_activation[corrotinas_ativas[0]]
		remaining_it = maxIt
		continue


	print corrotina_atual.nome

	remaining_it -= 1
	# print corrotina_atual.instructions
	line = corrotina_atual.instructions[corrotina_atual.counter]
	corrotina_atual.counter += 1
	
	if line[0] == "start":
		if(line[1] not in coroutines_activation.keys()):
			print "Erro de execucao -> corrotina " +  line[1] + " nao definida"
			quit()

		if len(line[2]) == len(coroutines_activation[line[1]].args):
			if( line[1] in corrotinas_nao_iniciadas):
				corrotinas_nao_iniciadas.remove(line[1])
				corrotinas_ativas.append(line[1])
				coroutines_activation[line[1]].counter = 0
			else:
				print "Erro de execucao -> Tentando iniciar corrotina " +  str(line[1]) + ", mas ela ja foi iniciada"
				quit()
		else:
			print "Erro -> Numero errado de argumentos -> " + str(line[2])

 	elif line[0] == "active":
 		if(line[1] not in coroutines_activation.keys()):
			print "Erro de execucao -> corrotina " +  str(line[1]) + " nao definida"
			quit()
		if(line[1] not in corrotinas_ativas):
			print "Tentando passar o controle para Corrotina " + str(line[1]) + " mas ela nao esta ativa"
		corrotinas_ativas.remove(line[1])
		corrotinas_ativas = [line[1]] + corrotinas_ativas
		corrotina_atual = coroutines_activation[line[1]]
		remaining_it = maxIt

	elif line[0] == "resume":
		if(line[1] not in coroutines_activation.keys()):
			print "Erro de execucao -> corrotina " +  str(line[1]) + " nao definida"
			quit()
		if(line[1] in corrotinas_nao_iniciadas):
			print "Erro de execucao -> Tentando resumir a corrotina " +  str(line[1]) + ", mas nao esta alocada"
			quit()

		#Se tentar usar resume em uma que nao esteja pausada, continua
		if(line[1] in corrotinas_pausadas):
			corrotinas_pausadas.remove(line[1])
		if(line[1] not in corrotinas_ativas):
			corrotinas_ativas.append(line[1])

	elif line[0] == "stop":
		if(line[1] not in coroutines_activation.keys()):
			print "Erro de execucao -> corrotina " +  str(line[1]) + " nao definida"
			quit()
		if(line[1] in corrotinas_nao_iniciadas):
			print "Erro de execucao -> Tentando pausar a corrotina " +  str(line[1]) + ", mas nao esta alocada"
			quit()

		#Se para ela mesmo, troca o controle
		if(line[1] == corrotina_atual.nome):
			corrotinas_ativas = corrotinas_ativas[1:]
			remaining_it = maxIt

			if(len(corrotinas_ativas) != 0):
				corrotina_atual = coroutines_activation[corrotinas_ativas[0]]
			else:
				continue

		#remove da lista de ativas
		if(line[1] in corrotinas_ativas):
			corrotinas_ativas.remove(line[1])
		if(line[1] not in corrotinas_pausadas):
			corrotinas_pausadas.append(line[1])

	elif line[0] == "cancel":
		print " ---> " + line[1]
		if(line[1] not in coroutines_activation.keys()):
			print "Erro de execucao -> corrotina " +  str(line[1]) + " nao definida"
			quit()

		#Se para ela mesmo, troca o controle
		if(line[1] == corrotina_atual.nome):
			corrotinas_ativas = corrotinas_ativas[1:]
			remaining_it = maxIt

			if(len(corrotinas_ativas) != 0):
				corrotina_atual = coroutines_activation[corrotinas_ativas[0]]
			else:
				continue

		#Se tentar usar resume em uma que nao esteja pausada, continua
		if(line[1] in corrotinas_pausadas):
			corrotinas_pausadas.remove(line[1])
		if(line[1] in corrotinas_ativas):
			corrotinas_ativas.remove(line[1])

		corrotinas_nao_iniciadas.append(line[1])




	if(remaining_it == 0):
		temp = corrotinas_ativas[0]
		corrotinas_ativas = corrotinas_ativas[1:]
		corrotinas_ativas.append(temp)
		corrotina_atual = coroutines_activation[corrotinas_ativas[0]]
		remaining_it = maxIt









