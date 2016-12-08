'''
Authors: Tobe Ezekwenna, Sam Saks-Fithian, Aman Zargarpur
'''

from prefpy.kemeny import MechanismKemeny
from gurobipy import *

#=====================================================================================
#=====================================================================================

def precedenceMatrix(preferences, counts):
	n, m = sum(counts), len(preferences[0])    # n preferences, m candidates
	print("m is", m)
	Q = np.zeros((m,m))
	for k in range(len(preferences)):
		vote = preferences[k]
		for i in range(len(vote) - 1):
			for j in range(i + 1, len(vote)):
				Q[vote[i][0]-1][vote[j][0]-1] += 1*counts[k] #Q[vote[i]][vote[j]] += 1
	return Q / n

#=====================================================================================
#=====================================================================================

class MechanismKemenyILP(MechanismKemeny):
	"""
	The Kemeny mechanism. Calculates winning ranking(s)/candidate(s) based on Gurobi
	optimization of ILP formula.
	"""
	#=====================================================================================

	def __init__(self):
		super(MechanismKemenyILP, self).__init__()

	#=====================================================================================

	def calcWinRanks(self, profile):
		"""
		Clears the self.winningRankings list, then fills it with any/all full rankings formed
		from the optimization of the ILP description:

		Goal: minimize SUMMATION_a,b( Q_ab * X_ba + Q_ba * X_ab )
			where Q is the precedence matrix formed from profile
			i.e. Q_ab is the fraction of times a>b across all rankings in profile
		Constraints:
			X_ab in {0, 1}
			X_ab + X_ba = 1, for ALL a,b
			X_ab + X_bc + X_ca >= 1, for ALL a,b,c

		:ivar Profile profile: A Profile object that represents an election profile.
		"""
		try:
			# Create a new model
			m = Model("kemeny")

			binaryMap = {}
			candMap = profile.candMap
			keys = candMap.keys()
			# print(keys)
			
			precedence = precedenceMatrix(profile.getOrderVectors(), profile.getPreferenceCounts())
			
			# Begin constructing the objective
			obj = LinExpr()
			for i in range(len(keys)-1):
				for j in range(i+1, len(keys)):

					# Create variables (2, 3)
					binaryMap[(i,j)] = m.addVar(vtype=GRB.BINARY, name=candMap[i+1]+candMap[j+1])
					binaryMap[(j,i)] = m.addVar(vtype=GRB.BINARY, name=candMap[j+1]+candMap[i+1])
					# Integrate new variables
					m.update()

					# Add constraint: X_ab + X_ba = 1 (4)
					m.addConstr(binaryMap[(i,j)] + binaryMap[(j,i)] == 1)
					obj += precedence[i][j]*binaryMap[(j,i)] + precedence[j][i]*binaryMap[(i,j)]
					obj += precedence[j][i]*binaryMap[(i,j)] + precedence[i][j]*binaryMap[(j,i)]

			# Add transitivity constraint: X_ab + X_bc + X_ca >= 1 (5)
			for i in range(len(keys)-2):
				for j in range(i+1, len(keys)-1):
					for k in range(j+1, len(keys)):
						m.addConstr(binaryMap[(i,j)] + binaryMap[(j,k)] + binaryMap[k, i] >= 1)

			# Set objective
			m.setObjective(obj, GRB.MINIMIZE)
			m.optimize()

			# print(precedence)
			# for v in m.getVars():
				# print(v.varName, v.x)
			# print('Obj:', m.objVal)

			self.winningRankings = []
			self.winningRankings = self.convertOptBinVarsToRanking(m)

		except GurobiError:
			print('Gurobi Error reported')

	#=====================================================================================

	def convertOptBinVarsToRanking(self, model):
		"""
		Returns a list containing the ranking(s) formed from the values of the binary 
		variables contained (and already optimized) by model.

		:ivar Model model: A Gurobi Model object that has been set and optimized. 
		"""
		# ???????????
		pass

#=====================================================================================
#=====================================================================================









