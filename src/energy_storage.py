class EnergyStorage:
	def __init__(self, capacity):
		self.capacity = capacity
		self.current_charge = 0

	def get_current_charge(self):
		return self.current_charge
	
	def get_capacity(self):
		return self.capacity

	def charge(self, amount):
		if amount < 0:
			raise ValueError("Amount of energy to store must be non-negative.")
		self.current_charge += amount
		if self.current_charge > self.capacity:
			self.current_charge = self.capacity

	def discharge(self, amount):
		if amount < 0:
			raise ValueError("Amount of energy to retrieve must be non-negative.")
		if amount > self.current_charge:
			amount = self.current_charge
		self.current_charge -= amount
		return amount