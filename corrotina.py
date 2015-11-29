class Corrotina:
	def __init__(self, nome, args):
		self.nome = nome
		self.args = args
		self.ret_args = [("reg1", 'int'), ("reg2", 'int'), ("reg3", 'int'), ("reg4", 'int'), ("reg5", 'int'), ("reg6", 'int')]
		self.instructions = []
		self.counter = 0
	def add_instruction(self, instruction):
		self.instructions += [instruction]
