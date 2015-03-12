class Position():
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "x= " + str(self.x) + ", y= " + str(self.y) + ", z= " + str(self.z)
