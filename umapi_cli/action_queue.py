class ActionQueue:
    def __init__(self, conn):
        self.actions = []
        self.conn = conn

    def push(self, user_action):
        self.actions.append(user_action)

    def execute(self):
        for action in self.actions:
            self.conn.execute_single(action)
        self.conn.execute_queued()

    def errors(self):
        return [a.execution_errors() for a in self.actions if a.execution_errors()]
