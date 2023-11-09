# Model design
import agentpy as ap
import networkx as nx
import random
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import IPython

class Person(ap.Agent):

    def setup(self):
        """ Initialize a new variable at agent creation. """
        self.condition = 0  # Susceptible = 0, Infected = 1, Recovered = 2
        self.time_infected = 1
        #Estados internos describen a cuantos han infectado, su estado de salud al paso del tiempo
        self.internal_states = {'Infected':0, 'health_history':[self.condition]}
        
       

    def see(self):
        #The person/agent "see" its current health
        return self.condition
    
    def next(self, health):
        #The person health changes
        self.condition = health
        return health
    
    def actionA(self, agent, rng):
        #Action, proceso de desición si se infecta al vecino
        if agent.see() == 0 and self.p.infection_chance > rng.random():
            return True
        return False
    
    def actionB(self, rng):
        #Action, si se recupera el host
        if self.p.recovery_chance > rng.random():
            return True
        return False
    

    def being_sick(self):
        """ Spread disease to peers in the network. """
        rng = self.model.random
        for n in self.network.neighbors(self):
            if n.actionA(n, rng):
                n.next(1) # Infect susceptible peer
                self.internal_states['Infected'] = 1 + self.internal_states['Infected']
            n.internal_states['health_history'].append(self.see())
        if self.actionB(rng):
            self.next(2)  # Recover from infection
            self.internal_states['health_history'].append(self.see())

        self.internal_states['health_history'].append(self.see())


class VirusModel(ap.Model):

    def setup(self):
        """ Initialize the agents and network of the model. """

        # Prepare a small-world network
        graph = nx.watts_strogatz_graph(
            self.p.population,
            self.p.number_of_neighbors,
            self.p.network_randomness)

        # Create agents and network
        self.agents = ap.AgentList(self, self.p.population, Person)
        self.network = self.agents.network = ap.Network(self, graph)
        self.network.add_agents(self.agents, self.network.nodes)

        # Infect a random share of the population
        I0 = int(self.p.initial_infection_share * self.p.population)
        self.agents.random(I0).condition = 1

    def update(self):
        """ Record variables after setup and each step. """

        # Record share of agents with each condition
        for i, c in enumerate(('S', 'I', 'R')):
            n_agents = len(self.agents.select(self.agents.condition == i))
            self[c] = n_agents / self.p.population
            self.record(c)

        # Stop simulation if disease is gone
        if self.I == 0:
            self.stop()

    def step(self):
        """ Define the models' events per simulation step. """

        # Call 'being_sick' for infected agents
        self.agents.select(self.agents.condition == 1).being_sick()

    def end(self):
        """ Record evaluation measures at the end of the simulation. """

        # Record final evaluation measures
        self.report('Total share infected', self.I + self.R)
        self.report('Peak share infected', max(self.log['I']))

    def utility(self):

        utility = [agent.internal_states['Infected'] for agent in self.agents]

        return utility
    
    def plot_utility(self, num_agents_per_plot):
        agent_utility = self.utility()

        total_agents = len(self.agents)

        groups_plot = total_agents // num_agents_per_plot

        for i in range(groups_plot):
            agents_slice = agent_utility[i * num_agents_per_plot : (i + 1) * num_agents_per_plot]
            indices = np.arange(i * num_agents_per_plot, (i + 1) * num_agents_per_plot)
            plt.figure(figsize=(12, 6))
            plt.bar(indices, agents_slice)
            plt.xlabel('Agents')
            plt.ylabel('Total Infected')
            plt.title(f'Infected - Group {i+1}')
            plt.show()

parameters = {
    'population': 1000,
    'infection_chance': 0.3,
    'recovery_chance': 0.1,
    'initial_infection_share': 0.1,
    'number_of_neighbors': 2,
    'network_randomness': 0.5
}

model = VirusModel(parameters)
results = model.run()

print(results)

def virus_stackplot(data, ax):
    """ Stackplot of people's condition over time. """
    x = data.index.get_level_values('t')
    y = [data[var] for var in ['I', 'S', 'R']]

    sns.set()
    ax.stackplot(x, y, labels=['Infected', 'Susceptible', 'Recovered'],
                 colors = ['r', 'b', 'g'])

    ax.legend()
    ax.set_xlim(0, max(1, len(x)-1))
    ax.set_ylim(0, 1)
    ax.set_xlabel("Time steps")
    ax.set_ylabel("Percentage of population")


"""
fig, ax = plt.subplots()
virus_stackplot(results.variables.VirusModel, ax)

plt.show()
"""

model.plot_utility(100)
