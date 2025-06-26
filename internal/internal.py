class Utils():

    def generate_t_vector(self):
        start = 0.0
        end = 6.0
        interval = 0.25
        return [start + i *
                interval for i in range(int((end - start) / interval) + 1)]
