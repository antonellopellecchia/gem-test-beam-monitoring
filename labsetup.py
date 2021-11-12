import modules.hv

class LabSetup:
    
    def __init__(self):
        self.hv = modules.hv.HVBoards()
        self.scope = modules.scope.Scope()

    def status_table(self):
        return self.hv.status_table()