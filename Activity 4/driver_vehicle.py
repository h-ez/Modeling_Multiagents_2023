import agentpy as ap

class Driver(ap.Agent):
    def setup(self):
        self.position = (0, 0)
        self.destination_a = (3, 9)
        self.destination_b = (0, 0)
        self.knowledge_vehicle_position = None
        self.decision_history = []

    def step(self):
        print(f"Driver position: {self.position}")
        next_move = self.decide_next_move()
        print(f"Driver decides to move {next_move}")
        self.model.vehicle.move(next_move)
        self.knowledge_vehicle_position = self.model.vehicle.position
        self.position = self.knowledge_vehicle_position
        self.decision_history.append(self.knowledge_vehicle_position)

    def decide_next_move(self):
        if self.model.vehicle.position == self.destination_a:
            return "back"
        else:
            return "forward"

    def inform_vehicle_action_completion(self):
        print(f"Vehicle action completed. Current position: {self.model.vehicle.position}")

class Vehicle(ap.Agent):
    def setup(self):
        self.position = (0, 0)
        self.driver_position = None
        self.movement_history = []
        self.sensor_range = 3

    def move(self, direction):
        if self.is_valid_move(direction):
            print(f"Vehicle position: {self.position}")
            self.position = self.calculate_new_position(direction)
            self.driver_position = self.model.driver.position
            self.movement_history.append(self.position)
            self.inform_action_completion()

    def is_valid_move(self, direction):
        if direction == "forward" and self.position != self.model.driver.destination_a:
            return True
        elif direction == "back" and self.position != self.model.driver.destination_b:
            return True
        else:
            return False

    def calculate_new_position(self, direction):
        if direction == "forward":
            return self.position[0] + 1, self.position[1] + 1
        elif direction == "back":
            return self.position[0] - 1, self.position[1] - 1

    def inform_action_completion(self):
        self.model.driver.inform_vehicle_action_completion()

class MyModel(ap.Model):
    def setup(self):
        self.driver = Driver(self)
        self.vehicle = Vehicle(self)

    def step(self):
        self.driver.step()

parameters = {
    'agents': 2,
    'steps': 10
}

model = MyModel(parameters)

try:
    results = model.run()
    for step in results.get('Vehicle', {}).get('position', []):
        print(f"Step {step.t}: {step.value}")
except Exception as e:
    print(f"An error occurred: {e}")
